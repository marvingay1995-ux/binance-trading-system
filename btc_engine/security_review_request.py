"""BTC-029: attributable security-review evidence request, not an approval.

This module generates a deterministic unsigned request and verifies the
presence of required *fields*, but never authenticates signatures or changes
permissions. No market data, files, backtests, API access or orders.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .verifier_implementation_decision import decision_record
from .verifier_threat_contract import contract_report
from .spec_amendment import canonical_bytes

REQUEST_ID = "BTC-029-v1"
REQUIRED_REVIEW_RECORD_FIELDS = (
    "reviewer_identity",
    "reviewer_organization_or_independent_role",
    "reviewed_repository_commit",
    "reviewed_btc027_contract_sha256",
    "reviewed_h01_v2_spec_sha256",
    "review_utc_timestamp",
    "independent_review_evidence_uri",
    "decision",
    "threats_reviewed",
    "fixture_cases_reviewed",
    "resource_limits_decision",
    "documented_residual_risks",
    "reviewer_signature_or_attestation",
)
ALLOWED_REVIEW_OUTCOMES = ("APPROVE_SCOPE_FOR_SEPARATE_OWNER_DECISION", "REJECT", "NEEDS_CHANGES")


def request_package():
    previous = decision_record()
    contract = contract_report()
    h01_spec_digest = hashlib.sha256(canonical_bytes()).hexdigest()
    if previous["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION":
        raise PermissionError("BTC-028 permission guard changed")
    if contract["contract_sha256"] != previous["btc027_contract_sha256"]:
        raise ValueError("BTC-027 evidence changed")
    if h01_spec_digest != previous["h01_v2_spec_sha256"]:
        raise ValueError("H01-v2 evidence changed")
    return {
        "program": REQUEST_ID,
        "status": "REVIEW_REQUEST_PREPARED_NOT_SUBMITTED",
        "source_btc028_decision": previous["decision"],
        "reviewed_btc027_contract_sha256": contract["contract_sha256"],
        "reviewed_h01_v2_spec_sha256": h01_spec_digest,
        "reviewer_request": {
            "scope": "STRICTLY_LOCAL_READ_ONLY_BTCUSDT_4H_CSV_ZIP_DATA_INTEGRITY_VERIFIER",
            "requested_assessment": [
                "Check ZIP/CSV parser threat T01-T10, symlink/TOCTOU, input path and decompression risks",
                "Review draft 25MB raw, 50MB expanded, 100:1 compression, 1-entry, 100000-record and 30-second limits",
                "Review 15 synthetic fixture expected outcomes F01-F15 including failure and source authenticity handling",
                "Review hard no-network/no-account/no-H01-simulation/no-order capability isolation",
                "Document residual risks, changes, independently verifiable evidence and a signed review outcome"
            ],
            "fixed_threat_ids": [item["id"] for item in contract["contract"]["threats"]],
            "fixed_fixture_ids": [item["id"] for item in contract["contract"]["synthetic_fixture_contracts_not_executed"]],
            "required_signed_record_fields": list(REQUIRED_REVIEW_RECORD_FIELDS),
            "allowed_review_outcomes": list(ALLOWED_REVIEW_OUTCOMES),
            "reviewer_assigned": False,
            "request_sent": False,
        },
        "owner_authorization": {
            "explicit_attributable_scope_decision_received": False,
            "signature_or_approval_provenance_verified": False,
            "approval_request_not_same_as_approval": True,
        },
        "authorizations": {
            "local_verifier_implementation": False,
            "process_real_market_data_with_new_verifier": False,
            "h01_signal_implementation": False,
            "h01_backtesting": False,
            "paper_trading": False,
            "live_trading": False,
            "automated_orders": False,
        },
        "decision": "SECURITY_EVIDENCE_REQUEST_READY_NO_IMPLEMENTATION_APPROVAL",
        "notes": [
            "No reviewer was contacted, assigned or recorded by this program.",
            "A schema-complete review record is still untrusted until independently corroborated.",
            "Source file hashes and publisher authenticity remain distinct later evidence tasks.",
            "A successful merge or CI test is not permission to implement the verifier.",
        ],
    }


def validate_proposed_review_fields(record):
    """Inspect only shape; never interpret a submitted record as approval."""
    if not isinstance(record, dict):
        raise ValueError("review record must be an object")
    if set(record) != set(REQUIRED_REVIEW_RECORD_FIELDS):
        raise ValueError("review record fields missing or unexpected")
    if record["decision"] not in ALLOWED_REVIEW_OUTCOMES:
        raise ValueError("unrecognized reviewer decision")
    for name in REQUIRED_REVIEW_RECORD_FIELDS:
        if name == "decision":
            continue
        if not isinstance(record[name], str) or not record[name].strip():
            raise ValueError("blank or invalid reviewer field: " + name)
    return {
        "review_record_shape": "VALID_BUT_UNAUTHENTICATED",
        "signature_verified": False,
        "independent_review_verified": False,
        "implementation_authorized": False,
        "decision": "AWAIT_AUTHENTICATED_HUMAN_REVIEW_AND_SEPARATE_OWNER_APPROVAL",
    }


def require_implementation_authorization():
    raise PermissionError("BTC-029 request is not signed approval for verifier implementation")


def main():
    parser = argparse.ArgumentParser(description="BTC-029 review request only")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = request_package()
    Path(args.output).write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"program": REQUEST_ID, "decision": report["decision"],
                      "request_sent": False, "implementation_authorized": False}, indent=2))


if __name__ == "__main__":
    main()
