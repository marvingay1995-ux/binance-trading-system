"""BTC-071: offline invented HTTP-response-envelope simulation ONLY.

No HTTP client or network implementation. The body must be one of BTC-069's
exact frozen invented JSON fixtures; this is NOT an external response parser.
"""
import hashlib
import json
from datetime import datetime, timezone
from types import MappingProxyType

from .r1_offline_synthetic_json import (
    PERIODS, SYNTHETIC_FIXTURES, _validate_json_klines, authorization_record,
)
from .r1_offline_parser_security_review import review_record as btc070_review

PROGRAM = "BTC-071-v1"
BASELINE_MAIN_SHA = "38f29cac5054bfe4f9dddb7ed68cf7fcc465371b"
MAIN_CI_RUN = 45181072519
MAIN_TESTS = 480
SYNTHETIC_AS_OF_MS = 1764072000000
MAX_ENVELOPE_BYTES = 8192
ALLOWED_HEADERS = frozenset(("content-type", "content-length"))
ALLOWED_CONTENT_TYPE = "application/json"
ALLOWED_STATUS = 200

def _validated_headers(headers, byte_count):
    if type(headers) is not dict or len(headers) != 2:
        raise ValueError("INVALID_SYNTHETIC_HEADERS")
    if any(type(k) is not str or k != k.lower() for k in headers):
        raise ValueError("INVALID_SYNTHETIC_HEADERS")
    if set(headers) != ALLOWED_HEADERS or any(type(v) is not str for v in headers.values()):
        raise ValueError("INVALID_SYNTHETIC_HEADERS")
    if headers["content-type"] != ALLOWED_CONTENT_TYPE:
        raise ValueError("INVALID_SYNTHETIC_CONTENT_TYPE")
    if headers["content-length"] != str(byte_count):
        raise ValueError("INVALID_SYNTHETIC_CONTENT_LENGTH")

def invented_response(interval):
    """Build an immutable-in-spirit synthetic envelope using fixed bytes only."""
    if interval not in PERIODS:
        raise ValueError("INVALID_INTERVAL")
    body = SYNTHETIC_FIXTURES[interval]
    return {"status": 200,
            "headers": {"content-type": "application/json",
                        "content-length": str(len(body))},
            "body": body}

def review_invented_response(interval, envelope=None, *, as_of_ms=SYNTHETIC_AS_OF_MS):
    """Never accept arbitrary response bytes or an authenticated HTTP object.

    The caller may supply a synthetic envelope for negative testing only.
    Successful parsing requires exact SHA256-matching frozen BTC-069 bytes.
    """
    if interval not in PERIODS:
        raise ValueError("INVALID_INTERVAL")
    if type(as_of_ms) is not int or as_of_ms != SYNTHETIC_AS_OF_MS:
        raise ValueError("UNAPPROVED_SYNTHETIC_CLOCK")
    if envelope is None:
        envelope = invented_response(interval)
    if type(envelope) is not dict or set(envelope) != {"status", "headers", "body"}:
        raise ValueError("INVALID_SYNTHETIC_ENVELOPE")
    if type(envelope["status"]) is not int or envelope["status"] != ALLOWED_STATUS:
        raise ValueError("SYNTHETIC_HTTP_STATUS_DENIED")
    body = envelope["body"]
    if type(body) is not bytes or len(body) > MAX_ENVELOPE_BYTES:
        raise ValueError("INVALID_SYNTHETIC_BODY")
    _validated_headers(envelope["headers"], len(body))
    expected = SYNTHETIC_FIXTURES[interval]
    if hashlib.sha256(body).digest() != hashlib.sha256(expected).digest():
        raise PermissionError("UNREGISTERED_BODY_DENIED")
    opens = _validate_json_klines(body, interval)
    # Only approved UTC synthetic as-of timestamp. Prevent unclosed candles
    # relative to this fixed clock; no wall-clock or live timestamp support.
    last_close_exclusive = opens[-1] + PERIODS[interval]
    if last_close_exclusive > as_of_ms:
        raise ValueError("SYNTHETIC_UNCLOSED_CANDLE")
    return {
        "program": PROGRAM,
        "fixture_interval": interval,
        "synthetic_only": True,
        "http_status": 200,
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "byte_count": len(body),
        "candle_count": len(opens),
        "synthetic_clock_utc": datetime.fromtimestamp(
            as_of_ms / 1000, timezone.utc).isoformat(),
        "last_close_exclusive_utc": datetime.fromtimestamp(
            last_close_exclusive / 1000, timezone.utc).isoformat(),
        "source_classification": "INVENTED_OFFLINE_ENVELOPE_NOT_HTTP_RESPONSE",
        "real_data_verified": False,
        "independent_security_reviewed": False,
        "network_or_order_authorized": False,
    }

def security_decision():
    prior = btc070_review()
    owner = authorization_record()
    if (prior["decision"] != "GO_OFFLINE_INVENTED_FIXTURE_TESTING_ONLY"
            or prior["network_fetch_authorized"] is not False
            or prior["real_data_ingestion_authorized"] is not False
            or owner["owner_decision"] != "APPROVE_OFFLINE_IMPLEMENTATION_ONLY"
            or owner["public_market_fetch_authorized"] is not False):
        raise PermissionError("BTC070_OR_OWNER_SCOPE_CHANGED")
    return {
        "program": PROGRAM,
        "baseline_main_sha": BASELINE_MAIN_SHA,
        "baseline_main_ci_run": MAIN_CI_RUN,
        "baseline_main_tests": MAIN_TESTS,
        "decision": "GO_FROZEN_INVENTED_HTTP_ENVELOPE_NEGATIVE_TESTS_ONLY",
        "envelopes": {i: review_invented_response(i) for i in sorted(PERIODS)},
        "independent_security_review_complete": False,
        "real_http_client_implemented": False,
        "tls_dns_redirect_controls_verified": False,
        "external_json_admission_authorized": False,
        "real_market_data_ingestion_authorized": False,
        "h01_backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_spot_authorized": False,
        "binance_credentials_authorized": False,
        "order_execution_authorized": False,
        "docker_execution_authorized": False,
        "spend_authorized": False,
        "next_gate": "Independent review of synthetic-only boundary and separate authorization for any external response processing or public endpoint access.",
    }

def require_network_or_order(*_args, **_kwargs):
    raise PermissionError("BTC071_NETWORK_AND_TRADING_NO_GO")

if __name__ == "__main__":
    print(json.dumps(security_decision(), sort_keys=True, indent=2))
