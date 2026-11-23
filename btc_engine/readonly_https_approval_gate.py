"""BTC-066: pre-execution owner-decision and HTTPS ingestion-security gate.

NO requests, HTTP client, dataset parsing, strategy or orders. Review of
request structure is not approval to fetch. Approval evidence is missing.
"""
import json
from urllib.parse import parse_qs, urlsplit

from .readonly_btcusdt_data_scope import scope_proposal
from .verifier_implementation_decision import decision_record as historic

VERSION = "BTC-066-v1"
MAIN_SHA = "67adc7ddfd2f63a16f86491099eebec1805537de"
MAIN_CI = 45177402725
MAIN_TESTS = 424
HOST = "data-api.binance.vision"
PATH = "/api/v3/klines"
ALLOWED_INTERVALS = frozenset(("1h", "4h"))
MAX_ROWS = 500
MAX_REQUESTS_PER_MINUTE = 1
REQUIRED_EVIDENCE = (
    "attributable_dated_owner_approval_for_R1_only",
    "independent_identified_security_reviewer_signed_review",
    "region_and_data_terms_approved",
    "bounded_https_client_threat_model_accepted",
    "fixture_based_json_schema_and_timestamp_negative_tests_passed",
    "source_integrity_and_provenance_logging_reviewed",
    "data_storage_retention_and_secrets_boundary_reviewed",
)
DENIED_FEATURES = (
    "http_calls", "real_market_data_ingestion", "authenticated_binance_api",
    "h01_strategy_backtests", "paper_trading", "live_trading",
    "order_execution", "docker_execution",
)


def validate_proposed_url(url):
    """Offline parse/deny-listing of an R1 draft URL. Never fetch it.

    This is a *proposal validator*, not a security boundary for HTTP clients.
    The future client must independently pin TLS, redirects, DNS/target and
    request metadata, and enforce size, timing and rate controls.
    """
    if not isinstance(url, str) or len(url) > 300 or any(ord(c) < 33 for c in url):
        return False
    try:
        p = urlsplit(url)
        if (p.scheme != "https" or p.netloc != HOST or p.hostname != HOST or
                p.username is not None or p.password is not None or
                p.port is not None or p.path != PATH or p.fragment):
            return False
        query = parse_qs(p.query, keep_blank_values=True, strict_parsing=True,
                         max_num_fields=6, separator="&")
        if set(query) != {"symbol", "interval", "limit"} or any(len(v) != 1 for v in query.values()):
            return False
        limit = query["limit"][0]
        return (query["symbol"] == ["BTCUSDT"] and
                query["interval"][0] in ALLOWED_INTERVALS and
                limit.isascii() and limit.isdecimal() and
                str(int(limit)) == limit and 1 <= int(limit) <= MAX_ROWS)
    except (ValueError, TypeError, OverflowError):
        return False


def approval_and_security_decision(owner_claim=None, review_claim=None):
    """Unverified caller assertions cannot override pending independent review."""
    for claim in (owner_claim, review_claim):
        if claim is not None and not isinstance(claim, dict):
            raise ValueError("INVALID_EVIDENCE_CLAIM")
    earlier = historic()
    proposal = scope_proposal()
    if earlier["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(earlier["permissions"].values()):
        raise PermissionError("BTC028_REVIEW_CHANGED")
    if proposal["network_fetch_authorized"] is not False or proposal["account_api_access_authorized"] is not False:
        raise PermissionError("BTC065_AUTHORITY_CHANGED")
    candidate = proposal["preferred_source_candidate"]
    if (candidate["origin"] != "https://" + HOST or candidate["path"] != PATH or
            candidate["symbol"] != "BTCUSDT" or candidate["intervals"] != ["1h", "4h"] or
            candidate["request_key_or_signed_auth"] is not False):
        raise PermissionError("R1_SCOPE_CHANGED")
    return {
        "program": VERSION,
        "reviewed_main_sha": MAIN_SHA,
        "reviewed_main_ci_run": MAIN_CI,
        "reviewed_main_tests": MAIN_TESTS,
        "decision": "R1_APPROVAL_AND_HTTPS_SECURITY_GATE_PENDING_NO_GO",
        "example_urls_checked_offline": {
            i: validate_proposed_url("https://" + HOST + PATH +
                                     "?symbol=BTCUSDT&interval=" + i + "&limit=500")
            for i in sorted(ALLOWED_INTERVALS)
        },
        "owner_claim_supplied_but_not_authenticated": bool(owner_claim),
        "security_claim_supplied_but_not_authenticated": bool(review_claim),
        "required_approved_evidence": {name: "MISSING_OR_NOT_INDEPENDENTLY_VERIFIED"
                                       for name in REQUIRED_EVIDENCE},
        "request_limit_proposed": MAX_ROWS,
        "max_requests_per_minute_proposed": MAX_REQUESTS_PER_MINUTE,
        "publisher_authenticity_verified": False,
        "independent_security_review_verified": False,
        "owner_authorization_verified": False,
        "future_https_client_implemented": False,
        "future_client_redirect_tls_dns_controls_verified": False,
        "future_client_byte_time_rate_bounds_verified": False,
        "future_client_utc_schema_checks_verified": False,
        "permissions": {name: False for name in DENIED_FEATURES},
        "next_action": "Seek explicit dated owner R1-only decision and identifiable independent review before narrowly authorizing an HTTPS JSON client implementation or any genuine candle retrieval.",
    }


def require_public_data_access(*_args, **_kwargs):
    raise PermissionError("BTC066_PUBLIC_DATA_ACCESS_NO_GO")


if __name__ == "__main__":
    print(json.dumps(approval_and_security_decision(), sort_keys=True, indent=2))
