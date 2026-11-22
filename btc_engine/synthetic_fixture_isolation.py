"""BTC-038 bounded synthetic-only isolation probes for S11-S14, S17-S18.

These probes deliberately operate on tiny invented inputs and test harness
behavior, not a real-data verifier. No exchange calls or trading functionality.
"""
import io
import json
import struct
import zipfile
from pathlib import Path

from .synthetic_fixture_coverage import coverage_report
from .synthetic_fixture_generator import BASE_CSV, LABEL, _zip_bytes
from .synthetic_fixture_spec import FAULT_CASES

VERSION = "BTC-038-v1"
CASES = ("S11", "S12", "S13", "S14", "S17", "S18")
MAX_SAMPLE_BYTES = 16_384

class SyntheticLimitExceeded(ValueError):
    pass


def make_small_compressed_zip():
    """Only 256 invented A bytes, never a ZIP bomb."""
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=False) as z:
        info = zipfile.ZipInfo("invented.txt", date_time=(2020, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, b"A" * 256)
    value = out.getvalue()
    if len(value) > MAX_SAMPLE_BYTES:
        raise SyntheticLimitExceeded("sample too large")
    return value


def capped_synthetic_zip_read(data, expanded_cap=128):
    """Minimal test-only counter, NOT safe parsing of untrusted ZIP files."""
    if not isinstance(data, bytes) or len(data) > MAX_SAMPLE_BYTES:
        raise SyntheticLimitExceeded("raw synthetic sample limit")
    if not 1 <= expanded_cap <= 4096:
        raise ValueError("test-only cap out of range")
    count = 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if len(archive.infolist()) != 1:
            raise ValueError("one test member expected")
        with archive.open(archive.infolist()[0]) as member:
            while True:
                chunk = member.read(min(32, expanded_cap + 1 - count))
                if not chunk:
                    break
                count += len(chunk)
                if count > expanded_cap:
                    raise SyntheticLimitExceeded("synthetic expansion ceiling exceeded")
    return count


def make_unsupported_method_zip():
    """Set the method to 99 in both ZIP headers of a tiny synthetic archive."""
    raw = bytearray(_zip_bytes(BASE_CSV))
    local = raw.find(b"PK\x03\x04")
    central = raw.find(b"PK\x01\x02")
    if local < 0 or central < 0 or len(raw) > MAX_SAMPLE_BYTES:
        raise ValueError("invalid tiny synthetic seed")
    # ZIP local method is at offset 8, central directory method at offset 10.
    struct.pack_into("<H", raw, local + 8, 99)
    struct.pack_into("<H", raw, central + 10, 99)
    return bytes(raw)


def test_only_input_symlink_guard(path):
    """Basic test-only refusal; NOT an atomic no-follow open defense."""
    target = Path(path)
    if target.is_symlink():
        raise ValueError("synthetic input symlink refused")
    return True


def test_only_record_budget(records, maximum=100):
    """Consumes a bounded iterable without materializing a giant data set."""
    if not 1 <= maximum <= 1000:
        raise ValueError("test-only record maximum invalid")
    count = 0
    for _ in records:
        count += 1
        if count > maximum:
            raise SyntheticLimitExceeded("synthetic record count exceeded")
    return count


def remaining_case_report():
    parent = coverage_report()
    expected = set(CASES)
    if set(parent["context_only_unexecuted"]) != expected:
        raise ValueError("BTC-037 dependency changed")
    return {
        "program": VERSION,
        "provenance": LABEL,
        "cases": {
            "S11": {"probe": "small compressed ZIP with 128-byte cap", "status": "TEST_HARNESS_ONLY"},
            "S12": {"probe": "unsupported compression method 99 in tiny synthetic ZIP headers", "status": "ZIP_LIBRARY_ONLY"},
            "S13": {"probe": "temporary filesystem symlink checked for refusal", "status": "TEST_HARNESS_ONLY_PLATFORM_DEPENDENT"},
            "S14": {"probe": "synthetic generator refuses an existing output directory", "status": "GENERATOR_ONLY"},
            "S17": {"probe": "socket and subprocess APIs forbidden during fixture computation", "status": "TEST_ISOLATION_ONLY"},
            "S18": {"probe": "iterator exceeds a tiny 100-record cap", "status": "TEST_HARNESS_ONLY"},
        },
        "registered_expected_future_verifier_outcomes": {key: FAULT_CASES[key]["expected"] for key in CASES},
        "unverified": [
            "real verifier file or ZIP handling",
            "actual 50 MB decompression, 100001-record and 30-second deadline limits",
            "atomic TOCTOU-resistant filesystem protection or operating-system network sandbox",
            "real Binance provenance or H01 strategies",
        ],
        "security_verdict": "SYNTHETIC_HARNESS_CHECKS_ONLY_VERIFIER_NOT_IMPLEMENTED",
        "real_market_data_authorized": False,
        "h01_backtesting_authorized": False,
        "trading_authorized": False,
    }
