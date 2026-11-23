"""BTC-067 R1 owner authorization and independent HTTPS review evidence register.

This is a NO-GO review record, not a mechanism for self-attested approval.
No network access, authentic market-data parsing, strategy or trading.
"""
import json

from .readonly_https_approval_gate import (
    REQUIRED_EVIDENCE as BTC066_EVIDENCE,
    approval_and_security_decision,
)
from .readonly_btcusdt_data_scope import scope_proposal
from .verifier_implementation_decision import decision_record as historical_decision

VERSION = "BTC-067-v1"
MAIN_SHA = "58ee992b1033f746f62d82eeb6c4cb6f3c19a67b"
MAIN_RUN = 45178090083
MAIN_TESTS = 434
SCOPE = {
    "asset": "BTCUSDT",
    "intervals": ("1h", "4h"),
    "source": "https://data-api.binance.vision",
    "route": "/api/v3/klines",
    "method": "GET",
    "max_candles_per_request_proposed": 500,
    "max_requests_per_minute_proposed": 1,
    "account_keys_permitted": False,
    "strategy_execution_permitted": False,
}
REVIEW_CHECKS = (
    "reviewer_identity_and_independence",
    "dated_attestable_security_assessment",
    "tls_hostname_and_certificate_verification",
    "dns_redirect_and_endpoint_allowlist",
    "request_rate_timeout_and_response_size_bounds",
    "json_schema_timestamp_utc_and_candle_finality_negative_tests",
    "provenance_raw_hash_source_url_and_error_audit",
    "terms_local_eligibility_retention_and_credential_isolation",
)
OWNER_DECISION_FIELDS = (
    "dated_owner_identity",
    "explicit_only_R1_keyless_BTCUSDT_1h_4h_scope",
    "specified_limits_and_endpoint",
    "explicit_no_account_no_backtest_no_orders",
)
MISSING = "NOT_EVIDENCED"
NO_GO = "NO_GO_R1_OWNER_AND_INDEPENDENT_SECURITY_APPROVAL_NOT_EVIDENCED"

def decision_record(owner_evidence=None, security_evidence=None):
    """Claims are accepted for review indexing but never authenticated here."""
    for evidence in (owner_evidence, security_evidence):
        if evidence is not None and not isinstance(evidence, dict):
            raise ValueError("INVALID_EVIDENCE_RECORD")
    old = historical_decision()
    b65 = scope_proposal()
    b66 = approval_and_security_decision()
    if old["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(old["permissions"].values()):
        raise PermissionError("HISTORICAL_NO_GO_CHANGED")
    if b65["network_fetch_authorized"] is not False or any(b66["permissions"].values()):
        raise PermissionError("PRIOR_PUBLIC_DATA_DENIAL_CHANGED")
    if b66["owner_authorization_verified"] is not False or b66["independent_security_review_verified"] is not False:
        raise PermissionError("PRIOR_APPROVAL_GATE_CHANGED")
    if not set(BTC066_EVIDENCE).issubset(b66["required_approved_evidence"]):
        raise PermissionError("BTC066_EVIDENCE_CONTRACT_CHANGED")
    return {
        "program": VERSION,
        "baseline_main_sha": MAIN_SHA,
        "baseline_ci_run": MAIN_RUN,
        "baseline_ci_tests": MAIN_TESTS,
        "decision": NO_GO,
        "owner_decision": "NOT_RECORDED",
        "owner_evidence_fields": {key: MISSING for key in OWNER_DECISION_FIELDS},
        "owner_claim_present_but_not_verified": bool(owner_evidence),
        "independent_reviewer": "NOT_IDENTIFIED",
        "security_review_findings": {key: MISSING for key in REVIEW_CHECKS},
        "security_claim_present_but_not_verified": bool(security_evidence),
        "scope": {**SCOPE, "intervals": list(SCOPE["intervals"])},
        "required_btc066_evidence": {key: MISSING for key in BTC066_EVIDENCE},
        "owner_authorization_verified": False,
        "independent_security_review_verified": False,
        "public_fetch_authorized": False,
        "https_client_implementation_authorized": False,
        "authentic_market_data_ingestion_authorized": False,
        "h01_backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_spot_trading_authorized": False,
        "binance_credentials_authorized": False,
        "orders_authorized": False,
        "docker_execution_authorized": False,
        "next_step": "Obtain attributable R1-only owner approval and identifiable independent HTTPS security assessment; separately decide whether a bounded offline-only HTTPS client implementation may begin.",
    }

def require_r1_fetch(*_args, **_kwargs):
    raise PermissionError("BTC067_PUBLIC_DATA_FETCH_NO_GO")

if __name__ == "__main__":
    print(json.dumps(decision_record(), sort_keys=True, indent=2))
