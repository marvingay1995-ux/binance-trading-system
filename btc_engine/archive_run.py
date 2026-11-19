"""Historical evaluation using official public monthly ZIP archives (no private data)."""
import argparse
import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from .archive import fetch_completed_months
from .evaluate import evaluate


def main():
    p = argparse.ArgumentParser(description="Research-only BTCUSDT historical ZIP evaluation")
    p.add_argument("--interval", choices=["1h", "4h"], required=True)
    p.add_argument("--months", type=int, choices=[6, 12, 24], default=12)
    p.add_argument("--output-dir", default="research-output")
    args = p.parse_args()
    candles, manifest = fetch_completed_months(args.interval, args.months)
    folder = Path(args.output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    raw = json.dumps([asdict(c) for c in candles], separators=(",", ":"), sort_keys=True)
    (folder / f"BTCUSDT-{args.interval}-candles.json").write_text(raw)
    result = evaluate(candles, args.interval)
    result["provenance"] = {
        "source": "Official Binance Vision public monthly Spot kline ZIPs",
        "symbol": "BTCUSDT", "interval": args.interval,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "candles_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "archives": manifest,
    }
    (folder / f"BTCUSDT-{args.interval}-report.json").write_text(
        json.dumps(result, indent=2, allow_nan=False))
    print(json.dumps({"interval": args.interval, "candles": len(candles),
                      "status": result["status"], "holdout": result["holdout"]}, indent=2))


if __name__ == "__main__":
    main()
