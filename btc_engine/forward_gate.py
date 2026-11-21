"""BTC-015 forward-evidence admission gate. No orders or account access.

A frozen research protocol is not proof of independent prospective testing.
This gate rejects reuse of the historic 12-month dataset and unsealed data.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .market import Candle, STEPS, validate

# Earlier BTC-011–014 analysis included archives through 2026-10-31.
# Prospective evaluation must not reuse those already examined candles.
FIRST_UNSEEN_MS = 1796083200000  # 2026-12-01T00:00:00Z
MIN_FORWARD_DAYS = 60
REGISTERED_INTERVAL = "4h"
REGISTERED_SYMBOL = "BTCUSDT"
REGISTERED_STRATEGY = "sma_5_20_4h_baseline"
REGISTERED_CONFIG = {
    "fast": 5, "slow": 20, "starting_usdt": 100.0,
    "max_exposure": 0.30, "daily_loss_limit": 0.02,
    "fee_rate": 0.001, "slippage_rate": 0.0005,
    "spread_rate": 0.0002, "step_size": 0.00001,
    "min_qty": 0.00001, "min_notional": 5.0,
}


def admit_forward_candles(candles, interval, collected_at, provenance):
    """Validate a fully complete, unseen forward period; never auto-promote.

    collected_at must be a timezone-aware datetime and cannot assert a
    collection in the future. Provenance is a descriptive record, not
    independent cryptographic authentication of source ownership.
    """
    if interval != REGISTERED_INTERVAL:
        raise ValueError("BTC-015 forward registration is 4h only")
    if collected_at.tzinfo is None:
        raise ValueError("timezone-aware collection time required")
    now = datetime.now(timezone.utc)
    if collected_at.astimezone(timezone.utc) > now:
        raise ValueError("future collection time")
    if not isinstance(provenance, dict) or not provenance.get("source_url") or not provenance.get("sha256"):
        raise ValueError("source URL and hash required")
    expected = provenance["sha256"]
    if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
        raise ValueError("invalid SHA256")
    validate(candles, interval)
    step = STEPS[interval]
    if candles[0].time < FIRST_UNSEEN_MS:
        raise ValueError("contains previously examined data")
    if candles[0].time != FIRST_UNSEEN_MS:
        raise ValueError("missing beginning of registered forward period")
    if len(candles) * step < MIN_FORWARD_DAYS * 86400000:
        raise ValueError("insufficient forward evidence")
    if candles[-1].time + step > int(collected_at.timestamp() * 1000) - step:
        raise ValueError("potentially incomplete most recent candle")
    return {
        "registration": REGISTERED_STRATEGY,
        "registered_interval": interval,
        "first_unseen_ms": FIRST_UNSEEN_MS,
        "last_ms_exclusive": candles[-1].time + step,
        "candles": len(candles),
        "provenance": provenance,
        "gate_status": "ADMITTED_FOR_FUTURE_RESEARCH_ONLY",
        "authorization": "NONE",
        "warnings": [
            "A dataset hash alone cannot prove independent or untampered historical sourcing.",
            "Observing this future period will make it no longer untouched.",
            "Exchange filters, fills, and risk limits remain unresolved.",
            "No trading is authorized by dataset admission."
        ],
    }


def main():
    p = argparse.ArgumentParser(description="BTC-015 unseen-data admission only")
    p.add_argument("--candles", required=True)
    p.add_argument("--provenance", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--collected-at", required=True, help="UTC ISO timestamp")
    args = p.parse_args()
    raw = Path(args.candles).read_bytes()
    provenance = json.loads(Path(args.provenance).read_text())
    digest = hashlib.sha256(raw).hexdigest()
    if provenance.get("sha256") != digest:
        raise ValueError("candle-file SHA256 mismatch")
    date = datetime.fromisoformat(args.collected_at.replace("Z", "+00:00"))
    candles = [Candle(**item) for item in json.loads(raw)]
    decision = admit_forward_candles(candles, REGISTERED_INTERVAL, date, provenance)
    Path(args.output).write_text(json.dumps(decision, indent=2))
    print(json.dumps({"gate_status":decision["gate_status"], "candles":decision["candles"]}, indent=2))


if __name__ == "__main__":
    main()
