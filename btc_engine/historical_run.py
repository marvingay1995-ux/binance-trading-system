"""Read-only historical data research. No account credentials or order endpoints."""
import argparse, hashlib, json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from .market import fetch_klines, STEPS
from .evaluate import evaluate

def main():
    p=argparse.ArgumentParser(description="Fetch public BTCUSDT klines and evaluate fixed baseline; NO LIVE TRADING")
    p.add_argument("--interval",choices=["1h","4h"],required=True)
    p.add_argument("--days",type=int,default=365)
    p.add_argument("--output-dir",default="research-output")
    a=p.parse_args()
    if not 90 <= a.days <= 730:
        p.error("days must be between 90 and 730")
    step=STEPS[a.interval]
    now=int(datetime.now(timezone.utc).timestamp()*1000)
    # Exclude the current forming bar, and one additional bar for conservative finality.
    end=(now//step-1)*step
    start=end-a.days*86400000
    candles=fetch_klines("BTCUSDT",a.interval,start,end)
    dest=Path(a.output_dir)
    dest.mkdir(parents=True,exist_ok=True)
    raw=json.dumps([asdict(c) for c in candles],separators=(",",":"),sort_keys=True)
    (dest/f"BTCUSDT-{a.interval}-candles.json").write_text(raw)
    report=evaluate(candles,a.interval)
    report["provenance"]={"source":"Binance public Spot /api/v3/klines",
                          "symbol":"BTCUSDT","interval":a.interval,"start_ms":start,
                          "end_ms_exclusive":end,"candles_sha256":hashlib.sha256(raw.encode()).hexdigest(),
                          "retrieved_at_utc":datetime.now(timezone.utc).isoformat()}
    (dest/f"BTCUSDT-{a.interval}-report.json").write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps({"interval":a.interval,"candles":len(candles),"sha256":report["provenance"]["candles_sha256"],
                      "holdout":report["holdout"],"status":report["status"]},indent=2))

if __name__=="__main__":
    main()
