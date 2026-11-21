"""BTC-012 independent diagnostics; all outputs are simulated, never live orders."""
import argparse
import hashlib
import json
import math
from dataclasses import asdict, replace
from pathlib import Path
from .backtest import Config, backtest
from .market import Candle, STEPS, validate


def trade_ledger(events):
    """Pair complete long entries and exits; expose unmatched events."""
    entry, trades = None, []
    for event in events:
        if event["side"] == "buy":
            if entry is not None:
                raise ValueError("overlapping buys")
            entry = event
        elif event["side"] == "sell":
            if entry is None:
                raise ValueError("unmatched exit")
            if not math.isclose(entry["qty"], event["qty"], rel_tol=1e-10, abs_tol=1e-10):
                raise ValueError("unexpected partial fill")
            trades.append({"entry_ms":entry["time"], "exit_ms":event["time"],
                           "quantity":entry["qty"], "entry_price":entry["price"],
                           "exit_price":event["price"], "net_pnl_usdt":event["pnl"]})
            entry = None
        else:
            raise ValueError("unknown event")
    return trades, entry


def summarize_trades(trades):
    wins = sum(t["net_pnl_usdt"] > 0 for t in trades)
    gross_win = sum(max(0, t["net_pnl_usdt"]) for t in trades)
    gross_loss = sum(max(0, -t["net_pnl_usdt"]) for t in trades)
    return {"closed_trades":len(trades),
            "win_rate_pct":(100*wins/len(trades) if trades else None),
            "mean_net_pnl_usdt":(sum(t["net_pnl_usdt"] for t in trades)/len(trades) if trades else None),
            "gross_profit_usdt":gross_win,"gross_loss_usdt":gross_loss,
            "profit_factor":gross_win/gross_loss if gross_loss else None,
            "loss_free_profit_factor_undefined":gross_loss==0}


def drawdown_audit(curve, starting_equity, limit=.02):
    peak = starting_equity
    largest = 0.
    day, start = None, starting_equity
    breaches = []
    max_daily = 0.
    for x in curve:
        v, t = x["equity"], x["time"]
        if v <= 0 or not math.isfinite(v):
            raise ValueError("invalid equity")
        peak = max(peak, v)
        largest = max(largest, 1-v/peak)
        current_day = t//86400000
        if current_day != day:
            day, start = current_day, v
        dd = max(0.,1-v/start)
        max_daily = max(max_daily,dd)
        if dd > limit + 1e-12:
            breaches.append({"time":t,"drawdown_pct":100*dd})
    return {"max_drawdown_pct":100*largest,
            "max_close_to_close_utc_day_loss_pct":100*max_daily,
            "observed_daily_loss_breach_bars":len(breaches),
            "first_breach_ms":breaches[0]["time"] if breaches else None,
            "warning":"Close-mark daily losses may exceed limit; simulator does not guarantee a stop."}


def diagnose(candles, interval, config=Config()):
    validate(candles,interval)
    if len(candles) < 300:
        raise ValueError("insufficient candles")
    baseline=backtest(candles,interval,config)
    split=len(candles)*80//100
    cut_time=candles[split].time
    trades, open_entry=trade_ledger(baseline["events"])
    holdout_trades=[t for t in trades if t["exit_ms"] >= cut_time]
    # Exit-date attribution includes positions opened before holdout; do not
    # present as independently restarted holdout P&L.
    scenarios={}
    for name,fee,slip,spread in [
        ("baseline",config.fee_rate,config.slippage_rate,config.spread_rate),
        ("double_fees",config.fee_rate*2,config.slippage_rate,config.spread_rate),
        ("double_slippage",config.fee_rate,config.slippage_rate*2,config.spread_rate),
        ("double_spread",config.fee_rate,config.slippage_rate,config.spread_rate*2),
        ("combined_stress",config.fee_rate*2,config.slippage_rate*2,config.spread_rate*2),
    ]:
        candidate=replace(config,fee_rate=fee,slippage_rate=slip,spread_rate=spread)
        result=backtest(candles,interval,candidate)
        before=result["equity_curve"][split-1]["equity"]
        after=result["equity_curve"][-1]["equity"]
        scenarios[name]={"full_net_pnl_usdt":result["net_pnl_usdt"],
                         "holdout_equity_change_usdt":after-before,
                         "holdout_return_pct":100*(after/before-1),
                         "max_full_drawdown_pct":result["max_drawdown_pct"],
                         "closed_trades":result["closed_trades"],
                         "fees_usdt":result["fees_usdt"]}
    first=baseline["equity_curve"][split-1]["equity"]
    last=baseline["equity_curve"][-1]["equity"]
    audit=drawdown_audit(baseline["equity_curve"],config.starting_usdt,config.daily_loss_limit)
    # Static notional feasibility warning using the fixed research defaults.
    # These parameters are NOT certified Binance exchange filters.
    min_notional_required=config.min_notional*(1+config.fee_rate)
    maximum_nominal_budget=config.starting_usdt*config.max_exposure
    return {
        "status":"RESEARCH_ONLY_NO_LIVE_AUTHORIZATION",
        "interval":interval,"candles":len(candles),
        "holdout_cut_ms":cut_time,
        "holdout_equity_change_usdt":last-first,
        "holdout_return_pct":100*(last/first-1),
        "closed_trade_diagnostics":summarize_trades(trades),
        "holdout_exit_attributed_diagnostics":summarize_trades(holdout_trades),
        "open_entry":open_entry,"risk_audit":audit,
        "cost_sensitivity":scenarios,
        "sizing":{"assumed_step_size":config.step_size,
                  "assumed_min_qty":config.min_qty,
                  "assumed_min_notional_usdt":config.min_notional,
                  "starting_max_exposure_budget_usdt":maximum_nominal_budget,
                  "initial_notional_feasible":maximum_nominal_budget>=min_notional_required,
                  "exchange_filters_verified":False},
        "decision":"NO_GO_LIVE",
        "limitations":["Historical backtest, simulated full fills only",
                       "Filters are examples, not verified current Binance BTCUSDT Spot filters",
                       "Intrabar risk, partial fills, restart reconciliation not modeled",
                       "Stress tests do not estimate statistical uncertainty",
                       "Holdout exit-attributed trades may have entries before cut",
                       "Inspect independent data integrity and additional market regimes"]}


def main():
    p=argparse.ArgumentParser(description="BTC-012 risk/strategy diagnostics - research only")
    p.add_argument("--input",required=True)
    p.add_argument("--interval",choices=("1h","4h"),required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    raw=Path(args.input).read_bytes()
    candles=[Candle(**row) for row in json.loads(raw)]
    result=diagnose(candles,args.interval)
    result["source_candles_sha256"]=hashlib.sha256(raw).hexdigest()
    Path(args.output).write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps({"interval":args.interval,"status":result["status"],
                      "holdout_return_pct":result["holdout_return_pct"],
                      "risk_audit":result["risk_audit"],
                      "decision":result["decision"]},indent=2))


if __name__=="__main__":
    main()
