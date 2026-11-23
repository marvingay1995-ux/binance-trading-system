"""BTC-069 offline-only BTCUSDT JSON kline fixture contract.

Only embedded, invented example bytes can be ingested. No URLs, sockets,
external files, network adapters, strategy calculations, or order functions.
The restricted fixture gateway refuses all unregistered input byte streams.
"""
import hashlib
import json
import math
from datetime import datetime, timezone

from .r1_pinned_fixture_integrity import assert_registered_invented_bytes
from .r1_evidence_reconciliation import reconcile_decision
from .verifier_implementation_decision import decision_record as historic

PROGRAM = "BTC-069-v1"
OWNER_DECISION = "APPROVE_OFFLINE_IMPLEMENTATION_ONLY"
APPROVAL_SOURCE = "Owner's explicit BTC-068 chat instruction on 2026-11-23"
APPROVAL_SCOPE = (
    "Offline module and tests using invented BTCUSDT 1h/4h JSON fixtures only. "
    "No Binance requests, authentic data, API keys, backtests, "
    "paper/live orders, Docker execution or spending."
)
MAX_PAYLOAD_BYTES = 8192
MAX_ROWS = 4
OPEN_MILLIS = 1763942400000  # Fixed synthetic timestamps, not a fetched market record
PERIODS = {"1h": 3600000, "4h": 14400000}

def _invented_rows(interval):
    step = PERIODS[interval]
    rows = []
    for i in range(3):
        open_ts = OPEN_MILLIS + i * step
        # Deliberately invented numbers: they are not BTC prices.
        price = 100 + i
        rows.append([open_ts, str(price), str(price + 2), str(price - 1),
                     str(price + 1), "10", open_ts + step - 1,
                     "1000", 1, "5", "500", "0"])
    return rows

# Bytes are generated only from fixed in-module invented literals; never from
# user-supplied URLs, files, archives, or authentic exchange responses.
SYNTHETIC_FIXTURES = {
    interval: json.dumps(_invented_rows(interval), separators=(",", ":"), ensure_ascii=True).encode("ascii")
    for interval in PERIODS
}
FIXTURE_SHA256 = {name: hashlib.sha256(payload).hexdigest()
                  for name, payload in SYNTHETIC_FIXTURES.items()}

def _finite_nonnegative_number(value):
    if type(value) is not str or not value or len(value) > 30:
        raise ValueError("INVALID_DECIMAL_FIELD")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("INVALID_DECIMAL_FIELD") from None
    if not math.isfinite(number) or number < 0:
        raise ValueError("INVALID_DECIMAL_FIELD")
    return number

def _validate_json_klines(raw, interval):
    """Internal structural validation, not an API to admit outside datasets."""
    if interval not in PERIODS or type(raw) is not bytes or len(raw) > MAX_PAYLOAD_BYTES:
        raise ValueError("INVALID_FIXTURE_INPUT")
    try:
        data = json.loads(raw)
    except (UnicodeError, ValueError, TypeError):
        raise ValueError("INVALID_JSON") from None
    if type(data) is not list or not (1 <= len(data) <= MAX_ROWS):
        raise ValueError("INVALID_CANDLE_COUNT")
    step = PERIODS[interval]
    prior = None
    result = []
    for row in data:
        if type(row) is not list or len(row) != 12:
            raise ValueError("INVALID_KLINE_SHAPE")
        opened, high, low, close = (
            _finite_nonnegative_number(row[i]) for i in (1, 2, 3, 4)
        )
        volume = _finite_nonnegative_number(row[5])
        quote_volume = _finite_nonnegative_number(row[7])
        taker_base = _finite_nonnegative_number(row[9])
        taker_quote = _finite_nonnegative_number(row[10])
        for number in (opened, high, low, close):
            if number <= 0:
                raise ValueError("NONPOSITIVE_PRICE")
        if high < max(opened, close, low) or low > min(opened, close):
            raise ValueError("INCONSISTENT_OHLC")
        if type(row[0]) is not int or type(row[6]) is not int or type(row[8]) is not int:
            raise ValueError("INVALID_TIME_OR_TRADES")
        if row[8] < 0 or row[0] % step != 0 or row[6] != row[0] + step - 1:
            raise ValueError("INVALID_TIME_OR_TRADES")
        if prior is not None and row[0] != prior + step:
            raise ValueError("MISSING_DUPLICATED_OR_UNSORTED_CANDLE")
        if taker_base > volume or taker_quote > quote_volume:
            raise ValueError("TAKER_VOLUME_EXCEEDS_VOLUME")
        if row[11] not in ("0", 0):
            raise ValueError("INVALID_IGNORED_FIELD")
        prior = row[0]
        result.append(row[0])
    return result

def review_frozen_fixture(interval, supplied_bytes=None):
    """Only frozen exact-match invented payloads are admitted. No external IO."""
    if interval not in PERIODS:
        raise ValueError("UNAPPROVED_INTERVAL")
    expected = SYNTHETIC_FIXTURES[interval]
    # Reject in-process fixture registry substitution before trusting defaults.
    assert_registered_invented_bytes(interval, expected)
    if supplied_bytes is None:
        supplied_bytes = expected
    if type(supplied_bytes) is not bytes or len(supplied_bytes) > MAX_PAYLOAD_BYTES:
        raise PermissionError("NOT_A_FROZEN_SYNTHETIC_FIXTURE")
    try:
        assert_registered_invented_bytes(interval, supplied_bytes)
    except PermissionError:
        raise PermissionError("NOT_A_FROZEN_SYNTHETIC_FIXTURE") from None
    opens = _validate_json_klines(supplied_bytes, interval)
    return {
        "fixture": interval,
        "synthetic_only": True,
        "bytes_sha256": assert_registered_invented_bytes(interval, supplied_bytes),
        "byte_count": len(supplied_bytes),
        "candle_count": len(opens),
        "first_open_utc": datetime.fromtimestamp(opens[0] / 1000, timezone.utc).isoformat(),
        "last_open_utc": datetime.fromtimestamp(opens[-1] / 1000, timezone.utc).isoformat(),
        "provenance": "IN_MODULE_INVENTED_FIXTURE_NOT_BINANCE",
        "publisher_verified": False,
        "signal_or_pnl_calculated": False,
    }

def authorization_record():
    previous = historic()
    pending = reconcile_decision()
    if previous["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(previous["permissions"].values()):
        raise PermissionError("HISTORICAL_NO_GO_CHANGED")
    if pending["public_data_fetch_authorized"] is not False:
        raise PermissionError("BTC068_ACCESS_GATE_CHANGED")
    return {
        "program": PROGRAM,
        "owner_decision": OWNER_DECISION,
        "owner_decision_evidence": APPROVAL_SOURCE,
        "owner_approval_scope": APPROVAL_SCOPE,
        "offline_invented_fixture_implementation_authorized": True,
        "independent_security_review_complete": False,
        "public_market_fetch_authorized": False,
        "authentic_data_ingestion_authorized": False,
        "h01_backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_spot_authorized": False,
        "api_credentials_authorized": False,
        "docker_execution_authorized": False,
        "spend_authorized": False,
        "fixture_reports": {name: review_frozen_fixture(name) for name in sorted(PERIODS)},
    }

def require_live_fetch_or_order(*_args, **_kwargs):
    raise PermissionError("BTC069_REAL_DATA_AND_TRADING_NO_GO")

if __name__ == "__main__":
    print(json.dumps(authorization_record(), sort_keys=True, indent=2))
