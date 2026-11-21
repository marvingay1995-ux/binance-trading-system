"""Chronological, no-optimization holdout evaluation of the fixed baseline."""
import json, math
from dataclasses import asdict
from pathlib import Path
from .market import Candle, validate
from .backtest import Config, backtest

def evaluate(candles, interval, config=Config()):
    validate(candles, interval)
    n = len(candles)
    if n < max(300, 5*(config.slow+2)):
        raise ValueError("at least 300 complete candles required")
    cut1, cut2 = n*60//100, n*80//100
    # Warm up using only preceding history. Report only evaluation-window
    # trades and equity; avoid attributing warmup profits to holdout.
    # Run full-prefix simulations for each endpoint; differences are
    # path-dependent and must not be described as independently restarted P&L.
    full = backtest(candles,interval,config)
    curve = full["equity_curve"]
    events = full["events"]
    def window(a,b,label):
        begin = curve[a-1]["equity"] if a else config.starting_usdt
        end = curve[b-1]["equity"]
        segment = curve[a:b]
        peak, dd = begin, 0.
        for x in segment:
            peak=max(peak,x["equity"])
            dd=max(dd,1-x["equity"]/peak)
        trades = [x for x in events if candles[a].time <= x["time"] < candles[b-1].time+({"1h":3600000,"4h":14400000}[interval])]
        return {"period":label,"start_ms":candles[a].time,"end_ms_exclusive":candles[b-1].time+({"1h":3600000,"4h":14400000}[interval]),
                "candles":b-a,"starting_equity":begin,"ending_equity":end,
                "net_pnl":end-begin,"return_pct":100*(end/begin-1),
                "max_drawdown_pct":100*dd,"events":len(trades),
                "buy_hold_price_return_pct":100*(candles[b-1].close/candles[a].open-1)}
    return {"status":"RESEARCH_ONLY_NOT_PROFIT_VERIFIED",
            "strategy":"fixed SMA 5/20 next-open baseline",
            "split":"chronological 60/20/20, continuous inventory; no parameter tuning",
            "config":asdict(config),
            "train":window(0,cut1,"train"),"validation":window(cut1,cut2,"validation"),
            "holdout":window(cut2,n,"untouched holdout"),
            "full":{"net_pnl":full["net_pnl_usdt"],"return_pct":full["return_pct"],
                    "max_drawdown_pct":full["max_drawdown_pct"],
                    "closed_trades":full["closed_trades"],"fees":full["fees_usdt"]},
            "limitations":["Synthetic fees and filters; not verified exchange filters",
                           "Continuous strategy state across splits; split returns not independent runs",
                           "No parameter search, statistical significance, walk-forward, or regime analysis",
                           "No live execution; no guarantee of future results"]}

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True)
    p.add_argument("--interval",choices=["1h","4h"],required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    candles=[Candle(**row) for row in json.loads(Path(args.input).read_text())]
    result=evaluate(candles,args.interval)
    Path(args.output).write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps({k:result[k] for k in ("status","train","validation","holdout")},indent=2))

if __name__=="__main__": main()
