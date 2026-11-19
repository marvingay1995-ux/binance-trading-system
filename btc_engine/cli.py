"""Research-only command line."""
import argparse, json
from pathlib import Path
from dataclasses import asdict
from .market import Candle, fetch_klines
from .backtest import backtest

def main():
    p = argparse.ArgumentParser(description="NO LIVE TRADING")
    sub = p.add_subparsers(dest="command",required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--interval",choices=["1h","4h"],required=True)
    f.add_argument("--start-ms",type=int,required=True)
    f.add_argument("--end-ms",type=int,required=True)
    f.add_argument("--output",required=True)
    b = sub.add_parser("backtest")
    b.add_argument("--interval",choices=["1h","4h"],required=True)
    b.add_argument("--input",required=True)
    args = p.parse_args()
    if args.command == "fetch":
        data = fetch_klines("BTCUSDT",args.interval,args.start_ms,args.end_ms)
        Path(args.output).write_text(json.dumps([asdict(x) for x in data],indent=2))
        print(f"Saved {len(data)} candles")
    else:
        data = [Candle(**x) for x in json.loads(Path(args.input).read_text())]
        result = backtest(data,args.interval)
        print(json.dumps({k:v for k,v in result.items() if k not in ("events","equity_curve")},indent=2))

if __name__ == "__main__":
    main()
