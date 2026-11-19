"""BTC-014: fixed-parameter chronological stability diagnostics.

Research only. These are non-overlapping observation windows from one
continuous backtest; they are NOT independent retraining or holdout samples.
"""
import argparse
import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path

from .backtest import Config, backtest
from .market import Candle, STEPS, validate


def fold_boundaries(n, first_fraction=0.40, fold_fraction=0.10):
    if n < 300 or first_fraction != 0.40 or fold_fraction != 0.10:
        raise ValueError("fixed BTC-014 window protocol requires >=300 candles")
    start = n * 4 // 10
    boundaries = [start] + [n * x // 10 for x in range(5, 11)]
    if any(b <= a for a, b in zip(boundaries, boundaries[1:])):
        raise ValueError("empty chronological window")
    return list(zip(boundaries, boundaries[1:]))


def walkforward(candles, interval, config=Config()):
    validate(candles, interval)
    folds = fold_boundaries(len(candles))
    step = STEPS[interval]
    scenarios = {}
    for label, multiplier in (("baseline", 1), ("double_costs", 2), ("triple_costs", 3)):
        stressed = replace(config, fee_rate=config.fee_rate * multiplier,
                           slippage_rate=config.slippage_rate * multiplier,
                           spread_rate=config.spread_rate * multiplier)
        result = backtest(candles, interval, stressed)
        curve = result["equity_curve"]
        output = []
        for a, b in folds:
            before = curve[a-1]["equity"]
            end = curve[b-1]["equity"]
            if before <= 0:
                raise ValueError("nonpositive period-start equity")
            peak = before
            dd = 0.0
            for point in curve[a:b]:
                peak = max(peak, point["equity"])
                dd = max(dd, 1 - point["equity"]/peak)
            output.append({
                "start_ms": candles[a].time,
                "end_ms_exclusive": candles[b-1].time + step,
                "candles": b-a,
                "start_equity_usdt": before,
                "end_equity_usdt": end,
                "return_pct": 100 * (end / before - 1),
                "max_drawdown_pct": 100 * dd,
                "buy_hold_price_return_pct": 100 * (candles[b-1].close / candles[a].open - 1)
            })
        positives = sum(window["return_pct"] > 0 for window in output)
        scenarios[label] = {
            "windows": output,
            "positive_windows": positives,
            "negative_or_flat_windows": len(output)-positives,
            "worst_window_return_pct": min(w["return_pct"] for w in output),
            "full_period_net_pnl_usdt": result["net_pnl_usdt"],
            "full_period_max_drawdown_pct": result["max_drawdown_pct"],
            "full_period_fees_usdt": result["fees_usdt"]
        }
    return {
        "program": "BTC-014",
        "status": "HISTORICAL_STABILITY_RESEARCH_ONLY",
        "strategy": "frozen SMA 5/20",
        "window_protocol": "40% initial observed history; 6 consecutive 10% windows; continuous inventory",
        "parameter_optimization": False,
        "interval": interval,
        "source_candles": len(candles),
        "scenarios": scenarios,
        "decision": "NO_GO_PAPER_AND_LIVE",
        "limitations": [
            "Previously examined data: windows are retrospective, not new untouched out-of-sample proof.",
            "Continuous backtest and positions; windows are not independent restarted simulations.",
            "No rolling retraining, parameter search, bootstrap inference or regime classification.",
            "Simplified execution model; risk caps cannot be guaranteed from OHLC candles.",
            "Exchange filters and real fills remain unverified."
        ]
    }


def main():
    p = argparse.ArgumentParser(description="BTC-014 fixed strategy stability checks; no orders")
    p.add_argument("--input", required=True)
    p.add_argument("--interval", choices=("1h", "4h"), required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    raw = Path(args.input).read_bytes()
    candles = [Candle(**item) for item in json.loads(raw)]
    result = walkforward(candles, args.interval)
    result["source_candles_sha256"] = hashlib.sha256(raw).hexdigest()
    Path(args.output).write_text(json.dumps(result, indent=2, allow_nan=False))
    print(json.dumps({"program": result["program"], "interval": args.interval,
        "decision": result["decision"],
        "baseline_positive_windows": result["scenarios"]["baseline"]["positive_windows"],
        "baseline_worst_window_pct": result["scenarios"]["baseline"]["worst_window_return_pct"],
        "triple_costs_positive_windows": result["scenarios"]["triple_costs"]["positive_windows"]
        }, indent=2))


if __name__ == "__main__":
    main()
