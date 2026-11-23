"""BTC-068: reconcile owner approval and independently reviewed HTTPS evidence.

A read-only review record. No HTTP client, file ingestion, signal generation,
orders, external reviewer claims, or Docker execution.
"""
import json

from .readonly_r1_owner_security_decision import (
    decision_record as btc067, OWNER_DECISION_FIELDS, REVIEW_CHECKS
)
from .readonly_https_approval_gate import REQUIRED_EVIDENCE as BTC066_EVIDENCE
from .verifier_implementation_decision import decision_record as btc028

PROGRAM = "BTC-068-v1"
BASELINE_SHA = "83d53a000036b54b2a8b8a818f2b333fd41f9d37"
BASELINE_CI_RUN = 45178615009
BASELINE_TESTS = 445
STATUS = "EVIDENCE_NOT_PRESENT"
OWNER_CHOICES = ("APPROVE_OFFLINE_IMPLEMENTATION_ONLY", "DECLINE", "DEFER")
REQUIRED_OWNER_BOUNDARIES = (
    "keyless_public_BTCUSDT_only",
    "1h_and_4h_only",
    "exact_data_api_origin_and_klines_path",
    "no_outbound_fetch_in_offline_phase",
    "no_keys_backtests_simulated_or_live_orders",
)
REQUIRED_REVIEW_AREAS = (
    "reviewer_independence_and_identity",
    "hostname_certificate_dns_redirect_policy",
    "bounded_headers_time_rate_and_payload_size",
    "json_schema_clock_units_and_candle_finality",
    "retries_status_errors_and_response_integrity",
    "storage_provenance_retention_and_no_secrets",
    "terms_and_regional_availability",
    "fixture_negative_tests_and_security_signoff",
)
OUT_OF_SCOPE = (
    "actual HTTP request or genuine candle retrieval",
    "Binance API credentials, account or orders",
    "H01 or replacement strategy backtests",
    "paper/testnet/live trading",
    "Docker execution, deployment or spending",
)

def reconcile_decision(owner_submission=None, security_submission=None):
    """Unverified submissions cannot become approvals by caller assertion."""
    for claim in (owner_submission, security_submission):
        if claim is not None and not isinstance(claim, dict):
            raise ValueError("INVALID_SUBMISSION")
    old = btc028()
    prior = btc067()
    if old["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(old["permissions"].values()):
        raise PermissionError("HISTORICAL_AUTHORIZATION_CHANGED")
    denied = ("public_fetch_authorized", "https_client_implementation_authorized",
              "authentic_market_data_ingestion_authorized",
              "h01_backtesting_authorized", "paper_trading_authorized",
              "live_spot_trading_authorized", "orders_authorized",
              "binance_credentials_authorized", "docker_execution_authorized")
    if prior["decision"] != "NO_GO_R1_OWNER_AND_INDEPENDENT_SECURITY_APPROVAL_NOT_EVIDENCED" or any(prior[key] is not False for key in denied):
        raise PermissionError("BTC067_AUTHORITY_CHANGED")
    if set(prior["owner_evidence_fields"]) != set(OWNER_DECISION_FIELDS) or set(prior["security_review_findings"]) != set(REVIEW_CHECKS):
        raise PermissionError("BTC067_EVIDENCE_SCHEMA_CHANGED")
    if set(prior["required_btc066_evidence"]) != set(BTC066_EVIDENCE):
        raise PermissionError("BTC066_EVIDENCE_SCHEMA_CHANGED")
    return {
        "program": PROGRAM,
        "baseline_main_sha": BASELINE_SHA,
        "baseline_main_ci_run": BASELINE_CI_RUN,
        "baseline_main_tests": BASELINE_TESTS,
        "decision": "NO_GO_PENDING_OWNER_CHOICE_AND_INDEPENDENT_SECURITY_EVIDENCE",
        "owner_choice_recorded": None,
        "owner_permitted_choices": list(OWNER_CHOICES),
        "owner_boundaries_for_later_approval": list(REQUIRED_OWNER_BOUNDARIES),
        "owner_claim_supplied_not_authenticated": bool(owner_submission),
        "owner_required_evidence": {k: STATUS for k in OWNER_DECISION_FIELDS},
        "reviewer_identity": None,
        "reviewer_independence_verified": False,
        "security_review_claim_supplied_not_authenticated": bool(security_submission),
        "security_required_evidence": {k: STATUS for k in REQUIRED_REVIEW_AREAS},
        "btc067_security_check_status": {k: STATUS for k in REVIEW_CHECKS},
        "btc066_evidence_status": {k: STATUS for k in BTC066_EVIDENCE},
        "review_status": "UNREVIEWED",
        "authorization_effect": "NONE",
        "scope_of_this_milestone": "RECORD_REQUIREMENTS_AND_NO_GO_ONLY",
        "out_of_scope": list(OUT_OF_SCOPE),
        "offline_https_client_implementation_authorized": False,
        "public_data_fetch_authorized": False,
        "real_data_ingestion_authorized": False,
        "backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "binance_credentials_authorized": False,
        "orders_authorized": False,
        "docker_execution_authorized": False,
        "next_decision": "Obtain explicit owner choice APPROVE_OFFLINE_IMPLEMENTATION_ONLY/DECLINE/DEFER for this exact bounded R1 scope, independently review implementation/security evidence, and only then make a separate implementation authorization decision.",
    }

def require_r1_action(*_args, **_kwargs):
    raise PermissionError("BTC068_R1_NO_GO_OWNER_AND_SECURITY_EVIDENCE_PENDING")

if __name__ == "__main__":
    print(json.dumps(reconcile_decision(), sort_keys=True, indent=2))
