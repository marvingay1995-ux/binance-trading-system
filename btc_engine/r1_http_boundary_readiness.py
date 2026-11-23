"""BTC-072 evidence-backed synthetic HTTP boundary review and R1 decision.

Static code review + existing synthetic tests are not independent security
acceptance. No network, real market data, strategies, orders, or Docker actions.
"""
import json

from .r1_offline_http_response import (
    PROGRAM as BTC071_PROGRAM, invented_response, review_invented_response,
    security_decision as btc071_decision,
)
from .r1_offline_synthetic_json import (
    authorization_record, SYNTHETIC_FIXTURES, FIXTURE_SHA256,
)
from .verifier_implementation_decision import decision_record as historic_decision

PROGRAM = "BTC-072-v1"
REVIEWED_MAIN_SHA = "cfb8cdf6f45f73c4bf3e6a2f9d7488d15dffecba"
REVIEWED_MAIN_CI_RUN = 45184893342
REVIEWED_MAIN_TEST_COUNT = 493

GATES = (
    ("OWNER_R1_OFFLINE_ONLY_SCOPE", "SATISFIED_FOR_INVENTED_FIXTURES_ONLY"),
    ("FROZEN_INVENTED_ENVELOPE_NEGATIVE_TESTS", "SATISFIED_FOR_SYNTHETIC_ONLY"),
    ("FIXTURE_REGISTRY_IMMUTABILITY_AND_INTEGRITY", "NOT_VERIFIED"),
    ("EXTERNAL_JSON_ADMISSION_DESIGN_AND_LIMITS", "NOT_IMPLEMENTED"),
    ("STRICT_JSON_DUPLICATE_KEYS_DEPTH_AND_DECIMAL_CONTRACT", "NOT_VERIFIED"),
    ("CANDLE_FINALITY_WITH_TRUSTED_TIME_SOURCE", "NOT_VERIFIED"),
    ("TLS_CERT_DNS_REDIRECT_AND_IP_BOUNDARY", "NOT_IMPLEMENTED"),
    ("HTTP_BYTES_DECOMPRESSION_TIMEOUT_RETRY_AND_RATE_BOUNDS", "NOT_IMPLEMENTED"),
    ("PROVENANCE_RETENTION_TERMS_AND_REGION_POLICY", "NOT_VERIFIED"),
    ("IDENTIFIED_INDEPENDENT_SECURITY_SIGNOFF", "MISSING"),
    ("SEPARATE_OWNER_APPROVAL_FOR_REAL_PUBLIC_DATA", "NOT_GRANTED"),
)
FINDINGS = (
    {
        "id": "F072-01",
        "severity": "HIGH",
        "evidence": "BTC-071 uses SYNTHETIC_FIXTURES[interval] for digest comparison; the shared dict is mutable in-process",
        "resolution": "Use independently pinned immutable reference bytes/digests in any future reviewed boundary; do not rely on runtime-mutated fixture registries",
    },
    {
        "id": "F072-02",
        "severity": "HIGH",
        "evidence": "BTC-071 checks an in-memory envelope, not a real HTTP client or transport",
        "resolution": "Separately design and review endpoint, TLS, DNS, redirect, size, compression, timeout and rate controls before authorizing requests",
    },
    {
        "id": "F072-03",
        "severity": "HIGH",
        "evidence": "BTC-069 internal JSON parser accepts arbitrary bytes when called directly; BTC-071 gateway only admits exact invented fixtures",
        "resolution": "Do not expose or label internal parser as safe for external data; new authority, strict generic parser and hostile-response testing required",
    },
    {
        "id": "F072-04",
        "severity": "MEDIUM",
        "evidence": "BTC-069 numeric validation uses floats and BTC-071 finality relies on one fixed invented clock",
        "resolution": "Specify Decimal-safe fields, timestamp range and trustworthy clock/finality semantics before any authentic data acceptance",
    },
    {
        "id": "F072-05",
        "severity": "BLOCKING",
        "evidence": "No attributable independent review/signoff and no separate owner approval for authentic public market-data fetch",
        "resolution": "Obtain independently identifiable review of exact implementation and distinct narrow R1 public-fetch authorization",
    },
)

def readiness_record():
    historic = historic_decision()
    owner = authorization_record()
    earlier = btc071_decision()
    if historic["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(historic["permissions"].values()):
        raise PermissionError("HISTORICAL_BTC028_NO_GO_CHANGED")
    if owner["owner_decision"] != "APPROVE_OFFLINE_IMPLEMENTATION_ONLY":
        raise PermissionError("OFFLINE_OWNER_SCOPE_CHANGED")
    if (earlier["program"] != BTC071_PROGRAM or
            earlier["decision"] != "GO_FROZEN_INVENTED_HTTP_ENVELOPE_NEGATIVE_TESTS_ONLY" or
            earlier["real_market_data_ingestion_authorized"] is not False or
            earlier["order_execution_authorized"] is not False or
            earlier["independent_security_review_complete"] is not False):
        raise PermissionError("BTC071_GATE_CHANGED")
    if set(SYNTHETIC_FIXTURES) != {"1h", "4h"} or set(FIXTURE_SHA256) != {"1h", "4h"}:
        raise PermissionError("SYNTHETIC_FIXTURE_REGISTRY_CHANGED")
    simulated = {i: review_invented_response(i, invented_response(i)) for i in ("1h", "4h")}
    if any(v["synthetic_only"] is not True or v["real_data_verified"] is not False for v in simulated.values()):
        raise PermissionError("SYNTHETIC_BOUNDARY_BREACHED")
    return {
        "program": PROGRAM,
        "reviewed_main_sha": REVIEWED_MAIN_SHA,
        "reviewed_main_ci_run": REVIEWED_MAIN_CI_RUN,
        "reviewed_main_tests": REVIEWED_MAIN_TEST_COUNT,
        "decision": "NO_GO_EXTERNAL_DATA_R1_SECURITY_AND_APPROVAL_GATES_MISSING",
        "internal_synthetic_testing_remains_permitted": True,
        "review_classification": "INTERNAL_CODE_ASSESSMENT_NOT_INDEPENDENT_SIGNOFF",
        "gate_evidence": dict(GATES),
        "findings": [dict(x) for x in FINDINGS],
        "invented_fixture_checks": simulated,
        "independent_security_review_verified": False,
        "real_https_transport_implemented": False,
        "external_response_admission_authorized": False,
        "public_market_data_fetch_authorized": False,
        "authentic_data_ingestion_authorized": False,
        "backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_spot_trading_authorized": False,
        "exchange_credentials_authorized": False,
        "orders_authorized": False,
        "docker_execution_authorized": False,
        "recommended_next_action": "Remediate the in-process fixture-integrity weakness and prepare a bounded, offline-only hostile-JSON response parser proposal; submit exact code/evidence for independent review and obtain a new separate authorization before live public-data access.",
    }

def require_external_data_or_order(*_args, **_kwargs):
    raise PermissionError("BTC072_EXTERNAL_DATA_AND_TRADING_NO_GO")

if __name__ == "__main__":
    print(json.dumps(readiness_record(), indent=2, sort_keys=True))
