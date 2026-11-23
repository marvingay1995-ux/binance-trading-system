"""BTC-065: proposal-only, keyless public BTCUSDT candle research.

The contract generates no requests and grants no access. Separate, attributable
scope approval and suitable security review are required before any live fetch.
"""
import json

from .trading_readiness_critical_path import critical_path_decision
from .verifier_implementation_decision import decision_record as historic

VERSION = "BTC-065-v1"
BASELINE_MAIN_SHA = "76ea2274965c8bce8facd3ac57d5facc35fc33f2"
BASELINE_RUN = 45176833564
BASELINE_TESTS = 414

# Static metadata only; these are NOT download instructions or active requests.
CANDIDATE = {
    "type": "KEYLESS_SPOT_PUBLIC_REST",
    "origin": "https://data-api.binance.vision",
    "method": "GET",
    "path": "/api/v3/klines",
    "symbol": "BTCUSDT",
    "intervals": ["1h", "4h"],
    "max_rows_per_request_proposed": 500,
    "max_requests_proposed_per_minute": 1,
    "request_key_or_signed_auth": False,
    "default_timestamp_unit": "MILLISECONDS",
    "region_legal_access_and_rate_policy_pending_review": True,
}
ALTERNATE = {
    "type": "PUBLISHED_SPOT_ARCHIVE",
    "origin": "https://data.binance.vision",
    "considered_for_initial_gate": False,
    "zip_csv_risk_review_required": True,
    "published_spot_from_2025_timestamp_unit": "MICROSECONDS",
    "checksum_file_is_not_independent_publisher_authentication": True,
}
REQUIRED_BEFORE_FETCH = (
    "dated attributable owner approval for exact R1 keyless read-only endpoint, symbol and intervals",
    "independent security assessment of bounded HTTPS JSON ingestion and safe logging",
    "approved terms, regional access policy, published weights and rate limits checked at implementation",
    "host allowlist, TLS certificate checks, no redirects to unapproved origins and no credential headers",
    "strict response byte cap, timeout, rows and timestamp/schema validation",
    "provenance log of request parameters, response time, status, source URI, raw SHA256 and byte count",
    "UTC completed-candle checks, no missing/duplicate bars, no future/unfinished bars",
    "revisions and independent provenance corroboration reported as unverified when absent",
    "exact data retention/deletion policy and separated storage with no secrets",
)
DENIED = (
    "network data fetches, archives/downloads or real input parsing under BTC-065",
    "account API keys, private endpoints, authentication, subscriptions or websockets",
    "H01 research implementation or retrospective/forward backtesting",
    "paper, testnet, live Spot, leverage, futures or automated orders",
    "container execution, privileges, cloud provisioning and spending",
)

def scope_proposal():
    old = historic()
    p = critical_path_decision()
    if old["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(old["permissions"].values()):
        raise PermissionError("BTC028_NO_GO_CHANGED")
    if p["public_data_access_authorized"] is not False or p["orders_authorized"] is not False:
        raise PermissionError("BTC064_AUTHORITY_CHANGED")
    if CANDIDATE["request_key_or_signed_auth"] or CANDIDATE["method"] != "GET":
        raise PermissionError("KEYLESS_CONTRACT_CHANGED")
    return {
        "program": VERSION,
        "reviewed_main_sha": BASELINE_MAIN_SHA,
        "reviewed_main_ci_run": BASELINE_RUN,
        "reviewed_main_tests": BASELINE_TESTS,
        "decision": "PROPOSAL_COMPLETE_R1_APPROVAL_NOT_GRANTED",
        "preferred_source_candidate": dict(CANDIDATE, intervals=list(CANDIDATE["intervals"])),
        "alternate_source": dict(ALTERNATE),
        "required_before_first_request": list(REQUIRED_BEFORE_FETCH),
        "prohibited": list(DENIED),
        "owner_approval_recorded": False,
        "independent_security_review_complete": False,
        "publisher_authenticity_verified": False,
        "network_fetch_authorized": False,
        "real_data_ingestion_authorized": False,
        "backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "account_api_access_authorized": False,
        "docker_execution_authorized": False,
        "next": "BTC-066: explicit R1 read-only public data approval and independent HTTPS JSON ingestion security gate; do not fetch or backtest until approved",
    }

def require_public_fetch(*_args, **_kwargs):
    raise PermissionError("BTC065_PUBLIC_DATA_FETCH_NOT_AUTHORIZED")

if __name__ == "__main__":
    print(json.dumps(scope_proposal(), sort_keys=True, indent=2))
