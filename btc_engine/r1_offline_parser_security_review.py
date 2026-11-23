"""BTC-070: offline parser negative-control review and evidence decision.

Review-only checks of BTC-069 using invented fixtures. This is NOT a signed
independent security assessment, data ingestion authorization or execution gate.
"""
import json

from .r1_offline_synthetic_json import (
    authorization_record, review_frozen_fixture, SYNTHETIC_FIXTURES
)
from .r1_evidence_reconciliation import reconcile_decision
from .verifier_implementation_decision import decision_record as historic

PROGRAM = "BTC-070-v1"
REVIEWED_MAIN = "ccf23abbc5a33d117c073c88e0e15c935b523458"
MAIN_RUN = 45180387857
MAIN_TESTS = 468

COVERED_NEGATIVE_CONTROLS = (
    "modified_frozen_fixture_bytes_rejected",
    "external_or_unregistered_payload_rejected",
    "unsupported_interval_rejected",
    "invalid_json_and_wrong_kline_shape_rejected",
    "zero_or_oversized_payload_rejected",
    "nonfinite_numeric_value_rejected",
    "nonpositive_or_inconsistent_ohlc_rejected",
    "duplicate_or_missing_open_times_rejected",
    "wrong_timestamp_unit_rejected",
    "invalid_timestamp_or_trade_count_rejected",
    "invalid_taker_volume_or_ignored_field_rejected",
    "no_network_or_process_actions",
    "historical_denials_and_live_order_refusal",
)
OPEN_SECURITY_GAPS = (
    "INDEPENDENT_REVIEWER_NOT_IDENTIFIED_OR_SIGNED",
    "NO_BOUNDED_LIVE_HTTPS_CLIENT_IMPLEMENTED",
    "TLS_DNS_REDIRECT_AND_REQUEST_RATE_NOT_TESTED",
    "NO_EXTERNAL_JSON_ADMISSION_AUTHORIZED",
    "UTC_FINALITY_VS_WALL_CLOCK_NOT_IMPLEMENTED",
    "JSON_DUPLICATE_KEYS_AND_NESTING_LIMITS_NOT_TESTED_FOR_EXTERNAL_SOURCES",
    "PRECISE_DECIMAL_RULES_NOT_VERIFIED_FOR_AUTHENTIC_EXCHANGE_VALUES",
    "PUBLISHER_PROVENANCE_NOT_AUTHENTICATED",
    "REAL_DATA_INGESTION_AND_STRATEGY_GATES_STILL_DENIED",
)

def review_record():
    historic_decision = historic()
    prior = reconcile_decision()
    implemented = authorization_record()
    if (historic_decision["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or
            any(historic_decision["permissions"].values())):
        raise PermissionError("HISTORIC_BTC028_NO_GO_CHANGED")
    if prior["public_data_fetch_authorized"] is not False:
        raise PermissionError("BTC068_REAL_DATA_GATE_CHANGED")
    if implemented["owner_decision"] != "APPROVE_OFFLINE_IMPLEMENTATION_ONLY":
        raise PermissionError("BTC069_OWNER_SCOPE_CHANGED")
    approved = "offline_invented_fixture_implementation_authorized"
    restricted = ("independent_security_review_complete", "public_market_fetch_authorized",
                  "authentic_data_ingestion_authorized", "h01_backtesting_authorized",
                  "paper_trading_authorized", "live_spot_authorized",
                  "api_credentials_authorized", "docker_execution_authorized",
                  "spend_authorized")
    if implemented[approved] is not True or any(implemented[key] is not False for key in restricted):
        raise PermissionError("BTC069_SCOPE_EXCEEDED")
    reports = {key: review_frozen_fixture(key) for key in sorted(SYNTHETIC_FIXTURES)}
    if any(not r["synthetic_only"] or r["publisher_verified"] for r in reports.values()):
        raise PermissionError("NON_SYNTHETIC_EVIDENCE_CLAIM")
    return {
        "program": PROGRAM,
        "reviewed_main_sha": REVIEWED_MAIN,
        "merged_main_ci_run": MAIN_RUN,
        "merged_main_ci_tests": MAIN_TESTS,
        "decision": "GO_OFFLINE_INVENTED_FIXTURE_TESTING_ONLY",
        "negative_controls_designed_and_tested": list(COVERED_NEGATIVE_CONTROLS),
        "residual_findings": list(OPEN_SECURITY_GAPS),
        "review_classification": "INTERNAL_TEST_REVIEW_NOT_INDEPENDENT_SIGNOFF",
        "independent_reviewer_identified": False,
        "independent_security_signoff": False,
        "frozen_fixture_reports": reports,
        "owner_offline_only_approval_recorded": True,
        "network_fetch_authorized": False,
        "external_json_ingestion_authorized": False,
        "real_data_ingestion_authorized": False,
        "h01_backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_spot_authorized": False,
        "orders_authorized": False,
        "docker_execution_authorized": False,
        "next_critical_gate": "Seek independent review of the offline parser and separately decide whether a bounded offline-only HTTP-response simulator is within approved scope; do not activate real data or strategies.",
    }

def require_authentic_data_or_trade(*_args, **_kwargs):
    raise PermissionError("BTC070_AUTHENTIC_DATA_AND_TRADING_NO_GO")

if __name__ == "__main__":
    print(json.dumps(review_record(), sort_keys=True, indent=2))
