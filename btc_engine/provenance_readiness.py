"""BTC-025: data-only provenance verifier readiness assessment.

A non-executing requirements registry: does not read candle files, fetch market
data, verify file bytes, authenticate suppliers, or evaluate strategies.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .spec_amendment import canonical_bytes
from .simulator_architecture import WARMUP_COUNT, WARMUP_START, WARMUP_END_EXCLUSIVE

REVIEW_VERSION = "BTC-025-v1"
REQUIRED_EVIDENCE = {
    "EVID-01": {"name": "explicit_offline_input_scope", "status": "NOT_APPROVED",
                "proof": "Separate authorization must limit verifier to supplied local read-only files and an output report"},
    "EVID-02": {"name": "raw_archive_digest", "status": "MISSING",
                "proof": "Record immutable raw ZIP/CSV SHA256 and byte length; recompute digest from bytes rather than trust manifest"},
    "EVID-03": {"name": "source_authenticity", "status": "MISSING",
                "proof": "Independent source URL, retrieval time, original provider checksums where available, and chain-of-custody review; manifest URLs are not proof"},
    "EVID-04": {"name": "canonical_candle_digest", "status": "MISSING",
                "proof": "Define canonicalization, recompute SHA256 from parsed records, bind hash to source archive and revision"},
    "EVID-05": {"name": "ohlc_and_volume_integrity", "status": "NOT_TESTED",
                "proof": "Finite positive OHLC, nonnegative volume, low/high consistency, schema count and timestamp units"},
    "EVID-06": {"name": "strict_4h_continuity", "status": "NOT_TESTED",
                "proof": "Each UTC open multiple of 14,400,000 ms and successive timestamps differ by exactly 14,400,000 ms; no duplicates"},
    "EVID-07": {"name": "warmup_partition", "status": "NOT_EVIDENCED",
                "proof": "Exactly 1200 consecutive 4h bars from 2026-05-15 00:00Z through 2026-11-30 20:00Z (exclusive boundary December 1)"},
    "EVID-08": {"name": "prospective_partition", "status": "NOT_YET_COMPLETE",
                "proof": "No data before 2026-12-01 00:00Z; at least 60 fully closed future days; disjoint from warmup"},
    "EVID-09": {"name": "time_and_finality", "status": "NOT_TESTED",
                "proof": "Never admit an in-progress bar; collection/retrieval timestamp must be after last recorded candle closes"},
    "EVID-10": {"name": "independent_human_review", "status": "MISSING",
                "proof": "Document reviewer, exact file hashes and review decision independent from generated self-asserted manifest"},
    "EVID-11": {"name": "reproduction_and_negative_controls", "status": "NOT_TESTED",
                "proof": "Identical bytes produce identical verified report; mutations, gaps, overlaps, revised data and mismatched hashes fail closed"},
    "EVID-12": {"name": "boundary_and_capability_isolation", "status": "NOT_APPROVED",
                "proof": "No network credentials, account balances, trading signals, fills, optimizers, paper/live execution or strategy returns"},
}

CAPABILITIES = {
    "verify_input_file_bytes": False,
    "authenticate_remote_provider": False,
    "fetch_market_data": False,
    "produce_h01_signals": False,
    "run_h01_backtest": False,
    "paper_orders": False,
    "live_orders": False,
    "binance_credentials": False,
}

def assessment_report():
    if WARMUP_COUNT != 1200 or WARMUP_START != "2026-05-15T00:00:00Z" or WARMUP_END_EXCLUSIVE != "2026-12-01T00:00:00Z":
        raise ValueError("Unexpected BTC-024 source boundaries")
    if any(CAPABILITIES.values()):
        raise PermissionError("BTC-025 must remain non-executing")
    return {
        "program": REVIEW_VERSION,
        "reviewed_architecture": "BTC-024",
        "reviewed_spec_sha256": hashlib.sha256(canonical_bytes()).hexdigest(),
        "data_scope": {"symbol": "BTCUSDT", "timeframe": "4h",
                       "warmup_start": WARMUP_START,
                       "warmup_end_exclusive": WARMUP_END_EXCLUSIVE,
                       "warmup_candles": WARMUP_COUNT,
                       "prospective_start": WARMUP_END_EXCLUSIVE,
                       "minimum_future_complete_days": 60},
        "required_evidence": REQUIRED_EVIDENCE,
        "not_satisfied": list(REQUIRED_EVIDENCE),
        "manifest_shape_is_authenticity_proof": False,
        "hash_format_is_content_verification": False,
        "source_url_is_provider_authentication": False,
        "file_verifier_implementation_authorized": False,
        "h01_backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "capabilities": CAPABILITIES,
        "decision": "REVIEW_ONLY_DATA_VERIFIER_AUTHORIZATION_WITHHELD",
        "limitations": [
            "These are required evidence definitions, not results from inspecting actual data.",
            "External provenance and chain of custody require separately grounded evidence.",
            "The prospective 60-day minimum cannot be complete before 2027-01-30T00:00:00Z.",
            "Future separate scope approval would not authorize H01 strategy simulation."
        ]
    }


def require_verifier_authorization():
    raise PermissionError("BTC-025 permits readiness documentation only; no file verifier implementation")


def main():
    parser = argparse.ArgumentParser(description="BTC-025 provenance verifier readiness report only")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report=assessment_report()
    Path(args.output).write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"program":REVIEW_VERSION,"decision":report["decision"],
                      "evidence_items_outstanding":len(report["not_satisfied"])},indent=2))


if __name__=="__main__":
    main()
