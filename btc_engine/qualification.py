"""BTC-013: conservative research-only qualification; no order placement."""
import argparse
import hashlib
import json
import math
from dataclasses import asdict, replace
from decimal import Decimal, InvalidOperation
from pathlib import Path
from .backtest import Config, backtest
from .market import Candle, validate
from .diagnostics import diagnose, trade_ledger


def _decimal(value):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid exchange decimal") from exc
    if not number.is_finite() or number <= 0:
        raise ValueError("nonpositive or nonfinite exchange filter")
    return number


def parse_spot_filters(exchange_info):
    """Parse only relevant BTCUSDT Spot filters from an externally supplied snapshot.

    A parsed snapshot is NOT proof of recency, authenticity or executable orders.
    """
    if not isinstance(exchange_info, dict):
        raise ValueError("exchange information must be object")
    symbols = exchange_info.get("symbols")
    if not isinstance(symbols, list):
        raise ValueError("symbols missing")
    matches = [s for s in symbols if isinstance(s, dict) and s.get("symbol") == "BTCUSDT"]
    if len(matches) != 1:
        raise ValueError("BTCUSDT missing or ambiguous")
    sym = matches[0]
    if sym.get("status") != "TRADING" or sym.get("isSpotTradingAllowed") is not True:
        raise ValueError("Spot symbol not tradable")
    fs = sym.get("filters")
    if not isinstance(fs, list):
        raise ValueError("filters missing")
    bytype = {}
    for f in fs:
        if not isinstance(f, dict) or f.get("filterType") in bytype:
            raise ValueError("duplicate or malformed filter")
        bytype[f.get("filterType")] = f
    if not all(k in bytype for k in ("LOT_SIZE", "PRICE_FILTER")):
        raise ValueError("required filters missing")
    lot, price = bytype["LOT_SIZE"], bytype["PRICE_FILTER"]
    minqty = _decimal(lot["minQty"])
    step = _decimal(lot["stepSize"])
    tick = _decimal(price["tickSize"])
    if "NOTIONAL" in bytype:
        minimum = _decimal(bytype["NOTIONAL"]["minNotional"])
        if bytype["NOTIONAL"].get("applyMinToMarket") is not True:
            raise ValueError("notional market-order rule unavailable")
    elif "MIN_NOTIONAL" in bytype:
        minimum = _decimal(bytype["MIN_NOTIONAL"]["minNotional"])
        if bytype["MIN_NOTIONAL"].get("applyToMarket") is not True:
            raise ValueError("notional market-order rule unavailable")
    else:
        raise ValueError("market-order notional filter missing")
    return {"step_size":str(step),"min_qty":str(minqty),"tick_size":str(tick),
            "min_notional":str(minimum),"source_status":"UNVERIFIED_SNAPSHOT"}


def check_order_size(price, quantity, filters, budget):
    """A hypothetical order check; not a substitute for Binance pretrade checks."""
    p, q, b = _decimal(price), _decimal(quantity), _decimal(budget)
    step, minimum_qty, minimum_notional = (_decimal(filters[k])
        for k in ("step_size", "min_qty", "min_notional"))
    reasons = []
    if q < minimum_qty: reasons.append("MIN_QTY")
    if (q / step) != (q / step).to_integral_value(): reasons.append("STEP_SIZE")
    if p*q < minimum_notional: reasons.append("MIN_NOTIONAL")
    if p*q > b: reasons.append("BUDGET")
    return {"hypothetical_accepted":not reasons,"reasons":reasons}


def stress_qualification(candles, interval, config=Config()):
    """No tuning: predetermined friction and latency diagnostics on held out data."""
    validate(candles, interval)
    if len(candles) < 300:
        raise ValueError("at least 300 complete candles needed")
    split = len(candles)*80//100
    scenarios = {}
    for label,multiplier in (("baseline",1),("2x_costs",2),("3x_costs",3)):
        cf = replace(config, fee_rate=config.fee_rate*multiplier,
                     slippage_rate=config.slippage_rate*multiplier,
                     spread_rate=config.spread_rate*multiplier)
        r = backtest(candles,interval,cf)
        before = r["equity_curve"][split-1]["equity"]
        after = r["equity_curve"][-1]["equity"]
        events = r["events"]
        ledger, open_entry = trade_ledger(events)
        scenarios[label] = {"holdout_return_pct":100*(after/before-1),
             "full_max_drawdown_pct":r["max_drawdown_pct"],
             "closed_trades":len(ledger),"fees_usdt":r["fees_usdt"],
             "still_open_position":open_entry is not None}
    diag = diagnose(candles, interval, config)
    # Intrabar loss and true execution risk cannot be proven from OHLC backtest.
    blockers = ["REAL_EXCHANGE_FILTERS_NOT_AUTHENTICATED",
                "PARTIAL_FILL_AND_RESTART_RECONCILIATION_NOT_IMPLEMENTED",
                "INTRABAR_DAILY_LOSS_NOT_ENFORCEABLE",
                "INDEPENDENT_WALK_FORWARD_NOT_COMPLETED",
                "LIVE_EXECUTION_NOT_AUTHORIZED"]
    if diag["risk_audit"]["observed_daily_loss_breach_bars"]:
        blockers.append("HISTORICAL_CLOSE_MARK_DAILY_LOSS_BREACH")
    if scenarios["baseline"]["holdout_return_pct"] <= 0:
        blockers.append("NONPOSITIVE_BASELINE_HOLDOUT")
    if scenarios["3x_costs"]["holdout_return_pct"] <= 0:
        blockers.append("NONPOSITIVE_STRESSED_HOLDOUT")
    return {"program":"BTC-013","interval":interval,
            "status":"RESEARCH_ONLY","decision":"NO_GO_LIVE_AND_PAPER",
            "scenarios":scenarios,"risk_audit":diag["risk_audit"],
            "filter_snapshot_authenticated":False,
            "blockers":blockers,
            "notes":["Costs and filters remain illustrative.",
                     "No inference of profitability or guaranteed risk cap.",
                     "This gate never grants execution permission."]}


def main():
    parser=argparse.ArgumentParser(description="BTC-013 research qualification only")
    parser.add_argument("--input",required=True)
    parser.add_argument("--interval",choices=("1h","4h"),required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    raw=Path(args.input).read_bytes()
    candles=[Candle(**row) for row in json.loads(raw)]
    report=stress_qualification(candles,args.interval)
    report["source_candles_sha256"]=hashlib.sha256(raw).hexdigest()
    Path(args.output).write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps({"program":report["program"],"interval":args.interval,
        "decision":report["decision"],"scenarios":report["scenarios"],
        "blockers":report["blockers"]},indent=2))


if __name__=="__main__":
    main()
