"""BTC-026: review of permission to build a local-file provenance verifier.

This module is not the verifier. No files are read apart from a requested
local JSON output, no credentials, network access, candle parsing or orders.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .provenance_readiness import REQUIRED_EVIDENCE
from .spec_amendment import canonical_bytes

REVIEW_ID = "BTC-026"
PROPOSED_BOUNDARY = {
    "allowed_after_separate_explicit_approval": [
        "read specified local BTCUSDT 4h raw CSV/ZIP files with size and decompression bounds",
        "compute raw SHA256 and independently canonicalized candle SHA256",
        "validate OHLC, nonnegative volume, timestamp units, UTC candle finality, order, gaps and duplicates",
        "check fixed 1200-bar pre-2026-12-01 warmup versus future partition",
        "write immutable, data-integrity-only reports that distinguish content integrity and source authenticity",
        "run synthetic fixtures and negative-control tests that cannot evaluate H01 returns",
    ],
    "forbidden_without_new_independent_authorization": [
        "web downloads or any runtime network access",
        "Binance API keys, signed endpoints, balances or account sessions",
        "H01 signal calculation, strategy simulation, optimization or backtest",
        "returns, trading recommendations, paper or real orders",
        "blindly trusting manifest hashes, source URLs or unsigned provider claims",
        "mutable source data or self-declared human signoff",
    ],
    "implementation_limits": {
        "local_files_only": True,
        "no_network": True,
        "no_exchange": True,
        "strict_file_size_limits_required": True,
        "strict_zip_entry_and_expansion_limits_required": True,
        "timestamp_unit_must_be_explicit": True,
        "source_authenticity_separate_from_integrity": True,
        "no_simulator_or_trade_logic": True,
    },
}
AUTHORIZATION_EVIDENCE = {
    "exact_scoped_change_request_approved_by_product_owner": False,
    "independent_security_review_completed": False,
    "local_file_threat_model_reviewed": False,
    "negative_control_acceptance_plan_approved": False,
    "original_spec_hash_frozen": True,
    "downstream_h01_and_trading_denied": True,
}


def review_decision():
    if not REQUIRED_EVIDENCE or any(not v for v in PROPOSED_BOUNDARY["implementation_limits"].values()):
        raise ValueError("scope boundary invalid")
    if any(x is True for x in [
        AUTHORIZATION_EVIDENCE["exact_scoped_change_request_approved_by_product_owner"],
        AUTHORIZATION_EVIDENCE["independent_security_review_completed"],
        AUTHORIZATION_EVIDENCE["local_file_threat_model_reviewed"],
        AUTHORIZATION_EVIDENCE["negative_control_acceptance_plan_approved"]
    ]):
        raise ValueError("unverified approval assertion in fixed BTC-026 record")
    return {
        "program": REVIEW_ID,
        "review_type": "INTERNAL_SCOPE_AND_PERMISSION_REVIEW_NOT_EXTERNAL_SECURITY_SIGNOFF",
        "reviewed_program": "BTC-025",
        "source_spec_sha256": hashlib.sha256(canonical_bytes()).hexdigest(),
        "proposed_scope": PROPOSED_BOUNDARY,
        "authorization_evidence": AUTHORIZATION_EVIDENCE,
        "outstanding_preconditions": [name for name, satisfied in AUTHORIZATION_EVIDENCE.items() if not satisfied],
        "scope_design_assessment": "NARROW_LOCAL_DATA_ONLY_SCOPE_DEFINED",
        "implementation_authorized": False,
        "data_ingestion_authorized": False,
        "h01_signals_authorized": False,
        "h01_backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "decision": "NO_GO_IMPLEMENTATION_UNTIL_EXPLICIT_SCOPED_APPROVAL_AND_SECURITY_REVIEW",
        "next_required_action": "Approve a separately reviewable local verifier implementation scope and obtain security review; no execution permission is conveyed by this PR",
    }


def require_local_verifier_implementation_authorization():
    raise PermissionError("BTC-026: local provenance verifier implementation not authorized")


def main():
    parser = argparse.ArgumentParser(description="BTC-026 permission review; no verifier implementation")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = review_decision()
    Path(args.output).write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"program": REVIEW_ID, "decision": report["decision"],
        "implementation_authorized": False}, indent=2))


if __name__ == "__main__":
    main()
