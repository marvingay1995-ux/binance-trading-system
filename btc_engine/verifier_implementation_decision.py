"""BTC-028 fixed, non-executing verifier implementation decision.

Only an evidence-linked later review can change the authorization state.
No file ingestion, hash verification of market data, trading or H01 backtest.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .verifier_threat_contract import AUTHORITY, contract_report
from .verifier_authorization_review import AUTHORIZATION_EVIDENCE
from .spec_amendment import canonical_bytes

DECISION_VERSION = "BTC-028-v1"
REQUIRED_APPROVAL_EVIDENCE = {
    "product_owner_explicit_scope_approval": {
        "status": "MISSING",
        "required_proof": "Dated, attributable product-owner approval naming a local-file-only verifier and exact implementation constraints",
    },
    "independent_security_reviewer_signoff": {
        "status": "MISSING",
        "required_proof": "Identified reviewer and signed assessment covering ZIP/CSV, path and TOCTOU risks, resource caps and no-network isolation",
    },
    "fixture_acceptance_and_limits": {
        "status": "MISSING",
        "required_proof": "Reviewer acceptance of F01-F15 synthetic fixture behaviors, numeric input ceilings and adversarial resource stress approach",
    },
    "immutable_contract_acceptance": {
        "status": "NOT_SIGNED",
        "required_proof": "Reviewed BTC-027 contract SHA256 and H01-v2 specification SHA256 explicitly recorded in signed decision",
    },
    "data_source_integrity": {
        "status": "NOT_EVIDENCED",
        "required_proof": "Local candle-file hash and source authenticity are separate future evidence tasks; their absence must never be described as verified",
    },
}
FUTURE_SCOPE = {
    "may_be_considered_after_new_explicit_approval": [
        "Build an offline-only local CSV/ZIP candle-file verifier using bounded reads and deterministic digests",
        "Build and run synthetic negative-control fixtures F01 through F15",
        "Report integrity checks, checksum matches, and unresolved publisher authenticity independently",
    ],
    "always_outside_this_decision": [
        "Binance API/network or authenticated account access",
        "H01 trading signals or strategy backtesting",
        "Paper trading, testnet execution or live Spot orders",
        "Parameter optimization, trade recommendations or strategy return calculations",
    ],
}


def decision_record():
    # The historical BTC-026/027 records are read-only and explicitly deny implementation.
    if any(AUTHORITY.values()):
        raise PermissionError("BTC-027 authorization flags unexpectedly changed")
    if any(AUTHORIZATION_EVIDENCE[k] for k in (
        "exact_scoped_change_request_approved_by_product_owner",
        "independent_security_review_completed",
        "local_file_threat_model_reviewed",
        "negative_control_acceptance_plan_approved",
    )):
        raise PermissionError("BTC-026 evidence assertions unexpectedly changed")
    threat = contract_report()
    threat_hash = threat["contract_sha256"]
    h01_spec_hash = hashlib.sha256(canonical_bytes()).hexdigest()
    missing = [key for key,value in REQUIRED_APPROVAL_EVIDENCE.items()
               if value["status"] in ("MISSING","NOT_SIGNED")]
    return {
        "program": DECISION_VERSION,
        "review_classification": "INTERNAL_DECISION_RECORD_NOT_EXTERNAL_SECURITY_AUDIT",
        "btc027_contract_sha256": threat_hash,
        "h01_v2_spec_sha256": h01_spec_hash,
        "decision": "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION",
        "reason": "Explicit scoped product-owner approval and independent security acceptance have not been evidenced",
        "required_approval_evidence": REQUIRED_APPROVAL_EVIDENCE,
        "missing_authorization_preconditions": missing,
        "future_scope": FUTURE_SCOPE,
        "permissions": {
            "local_verifier_implementation": False,
            "local_real_market_data_ingestion": False,
            "h01_signal_implementation": False,
            "h01_backtesting": False,
            "paper_trading": False,
            "live_trading": False,
            "auto_trade_orders": False,
        },
        "interpretation": [
            "Merging BTC-028 records the denial; a PR merge is not implementation approval.",
            "No actual candle file was verified or processed in this decision.",
            "The synthetic fixture registry is a specification and is not proof of hostile-file testing.",
            "Only a new, separately evidenced and signed decision can approve narrow verifier implementation.",
        ],
    }


def require_verifier_implementation():
    raise PermissionError("BTC-028: local-file verifier implementation denied; approval evidence missing")


def main():
    p=argparse.ArgumentParser(description="BTC-028 review decision only")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    record=decision_record()
    Path(args.output).write_text(json.dumps(record,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"program":DECISION_VERSION,"decision":record["decision"],
                      "missing_preconditions":record["missing_authorization_preconditions"]},indent=2))


if __name__=="__main__":
    main()
