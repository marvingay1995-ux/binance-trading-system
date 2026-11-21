"""BTC-024 review-only architecture and evidence manifest validator.

No simulator, signal computation, candle loader, exchange endpoint, or order code.
Manifest validation does not authenticate sources or authorize strategy research.
"""
import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .spec_amendment import AMENDMENT, canonical_bytes

TIMEFRAME_MS = 4 * 60 * 60 * 1000
WARMUP_COUNT = 1200
WARMUP_START = "2026-05-15T00:00:00Z"
WARMUP_END_EXCLUSIVE = "2026-12-01T00:00:00Z"
PROSPECTIVE_START = WARMUP_END_EXCLUSIVE
REQUIRED_MANIFEST_KEYS = frozenset({
    "symbol", "interval", "kind", "source_uri", "retrieved_utc",
    "period_start_utc", "period_end_exclusive_utc", "candle_count",
    "raw_sha256", "canonical_sha256", "specification_sha256",
    "review_status"
})
SHA256_HEX = frozenset("0123456789abcdef")

ARCHITECTURE = {
    "program": "BTC-024",
    "stage": "REVIEW_ONLY_NO_SIMULATOR_IMPLEMENTATION",
    "purpose": "Reproducible offline H01 simulation architecture and negative-control evidence design",
    "modules": [
        {"name": "ingest_boundary", "role": "accept explicit user-supplied immutable files; forbid network and credentials"},
        {"name": "manifest_verifier", "role": "check data hashes, source provenance, UTC ranges and bar continuity; reject any mismatch"},
        {"name": "pure_signal", "role": "future separately approved module; only completed closes[i-1200:i] at open[i]"},
        {"name": "decimal_accounting", "role": "future isolated USDT cash/BTC inventory; fee-inclusive step-rounded sizes"},
        {"name": "hypothetical_fill_engine", "role": "future reject/partial-fill/dust and terminal-liquidation reporting, no exchange order transport"},
        {"name": "risk_observer", "role": "future daily UTC mark and intrabar low diagnostics; no promised 2% guaranteed stop"},
        {"name": "benchmark_engine", "role": "future 100 USDT cash versus initially 20%-allocated non-rebalancing BTC"},
        {"name": "report_gate", "role": "future evidence hashes, cost stresses and explicit NO_AUTOMATIC_PROMOTION"},
    ],
    "isolation": {
        "network_access": False, "exchange_credentials": False,
        "binance_api": False, "account_balances": False,
        "real_orders": False, "paper_orders": False,
        "strategy_signals_implemented": False,
        "strategy_backtesting_enabled": False,
    },
    "interfaces": {
        "inputs": ["warmup_candles_json", "future_candles_json", "warmup_manifest", "future_manifest", "immutable_protocol_sha256", "filter_snapshot_manifest"],
        "outputs": ["input_sha256_audit", "hypothetical_fills_if_later_approved", "equity_report_if_later_approved", "blocker_report"],
        "ordering": "manifest and authorization verification BEFORE any data processing",
        "fail_closed_events": ["missing_bar", "duplicate_bar", "unaligned_time", "revised_hash",
                               "unknown_filter", "unresolved_partial_fill", "missing_cash_state",
                               "portfolio_exposure_unknown", "stale_data", "missing_review_signoff"],
    },
    "negative_controls": [
        "same-bar close contamination cannot change next-open decision",
        "missing, duplicate or non-4h data must reject",
        "improper warmup return attribution must reject",
        "unverified min notional or order step must reject",
        "dust, partial fills, and crash recovery must not silently mark positions flat",
        "fee-inclusive budget cannot exceed modeled free cash",
        "marked BTC portfolio exposure cannot exceed 30% at admission",
        "UTC daily losses beyond 2% must be reported and cannot be called guaranteed prevented",
        "multiple-run inputs must reproduce identical hashes and outputs",
    ],
    "required_external_evidence": [
        "immutable 1200-bar warmup and source hashes",
        "complete future 4h dataset after registered prospective cutoff",
        "independently reviewed BTC-022 specification digest",
        "realistic filters and fees with retrieval time/source, without implying live safety",
        "separately approved offline-only simulator implementation scope",
        "reviewer identity and explicit human signoff",
    ],
    "decision": "ARCHITECTURE_FOR_REVIEW_ONLY_NOT_AUTHORIZED",
}


def _utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("timestamp must be UTC ISO8601 Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid UTC timestamp") from exc
    if parsed.utcoffset() != timedelta(0) or parsed.microsecond:
        raise ValueError("non-UTC or fractional timestamp")
    return parsed


def _digest(value):
    if not isinstance(value, str) or len(value) != 64 or any(c not in SHA256_HEX for c in value):
        raise ValueError("invalid SHA256")
    return value


def validate_manifest(manifest):
    """Validate a descriptive *untrusted* file manifest, not the data or source."""
    if not isinstance(manifest, dict) or set(manifest) != REQUIRED_MANIFEST_KEYS:
        raise ValueError("missing or unexpected manifest fields")
    if manifest["symbol"] != "BTCUSDT" or manifest["interval"] != "4h":
        raise ValueError("unregistered market")
    if manifest["kind"] not in ("WARMUP_ONLY", "PROSPECTIVE_ONLY"):
        raise ValueError("unregistered data kind")
    if not isinstance(manifest["source_uri"], str) or not manifest["source_uri"].startswith("https://"):
        raise ValueError("source URI required; no URL fetched")
    for key in ("raw_sha256","canonical_sha256","specification_sha256"):
        _digest(manifest[key])
    expected_spec = hashlib.sha256(canonical_bytes()).hexdigest()
    if manifest["specification_sha256"] != expected_spec:
        raise ValueError("specification hash mismatch")
    if manifest["review_status"] != "UNVERIFIED_REVIEW_ONLY":
        raise ValueError("cannot self-certify a review")
    start,end,retrieved = map(_utc, (manifest["period_start_utc"], manifest["period_end_exclusive_utc"], manifest["retrieved_utc"]))
    if not start < end or retrieved < end:
        raise ValueError("period or retrieval time invalid")
    if int(start.timestamp()) % (4*3600) or int(end.timestamp()) % (4*3600):
        raise ValueError("unaligned four-hour boundary")
    if type(manifest["candle_count"]) is not int or manifest["candle_count"] <= 0:
        raise ValueError("invalid candle count")
    if end-start != timedelta(hours=4*manifest["candle_count"]):
        raise ValueError("manifest count does not match period; this does not verify content")
    if manifest["kind"] == "WARMUP_ONLY":
        if (manifest["period_start_utc"],manifest["period_end_exclusive_utc"],manifest["candle_count"]) != (WARMUP_START,WARMUP_END_EXCLUSIVE,WARMUP_COUNT):
            raise ValueError("incorrect warmup boundary or count")
    elif start < _utc(PROSPECTIVE_START):
        raise ValueError("future dataset overlaps warmup")
    return {
        "status": "MANIFEST_SHAPE_VALIDATED_CONTENT_NOT_VERIFIED",
        "kind": manifest["kind"],
        "specification_sha256": expected_spec,
        "external_source_authenticated": False,
        "candles_checked": False,
        "research_implementation_authorized": False,
        "backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
    }


def architecture_report():
    return {
        "architecture": ARCHITECTURE,
        "reference_spec_sha256": hashlib.sha256(canonical_bytes()).hexdigest(),
        "source_hypothesis": AMENDMENT["version"],
        "authorization": "NONE",
    }


def main():
    parser = argparse.ArgumentParser(description="BTC-024 offline simulator architecture report; no simulation")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    Path(args.output).write_text(json.dumps(architecture_report(),indent=2,allow_nan=False)+"\n")
    print(json.dumps({"program": "BTC-024", "decision": ARCHITECTURE["decision"]},indent=2))


if __name__ == "__main__":
    main()
