"""BTC-032 security-contract remediation: declarative controls, NOT a verifier.

No CSV/ZIP processing, no input file opens, no market data, no network and no
strategy execution. Records requirements and validates only registry structure.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .spec_amendment import canonical_bytes as h01_spec_bytes
from .verifier_threat_contract import contract_report

VERSION = "BTC-032-v1-PROPOSED"
SOURCE_REVIEW_SHA = "75129d093ee2127a1af4d8243a8a216a450f9c38"
PARENT_CONTRACT_SHA = contract_report()["contract_sha256"]
H01_SPEC_SHA = hashlib.sha256(h01_spec_bytes()).hexdigest()

REMEDIATIONS = {
    "AI-SEC-01": {
        "severity": "HIGH", "status": "SPECIFIED_UNTESTED",
        "controls": [
            "Check raw regular file size before opening and cumulative streaming read <= 25000000 bytes.",
            "For ZIP, check central directory entries <= 1 and reject encrypted, nested, non-CSV and unsupported method; do not trust claimed uncompressed size.",
            "Enforce cumulative expanded bytes <= 50000000 while reading bounded chunks, ratio <= 100, CSV row bytes <= 4096, columns <= 16, records <= 100000.",
            "Deadline <= 30 seconds requires bounded cancellation strategy and externally enforced resource limits; no assurance from a clock check alone.",
            "Fail closed before parsing and immediately upon crossing each counter; reject exactly when > configured maximum.",
        ],
        "remaining": "Limits are proposals pending stress tests; memory/CPU enforcement is not implemented.",
    },
    "AI-SEC-02": {
        "severity": "HIGH", "status": "SPECIFIED_UNTESTED",
        "controls": [
            "Accept only a configured input root and regular files, reject input symlinks, special files and directory traversal.",
            "Open a single file descriptor with platform-specific no-follow checks; fstat and verify opened identity, hash/parse same snapshot, detect changes.",
            "ZIP must have exactly one flat regular UTF-8 CSV member; reject path separators, drive prefixes, absolute names, symlinks, duplicate entries, invalid encoding and nested archive members.",
            "No extraction. Write reports only in a protected output root using a unique name, exclusive create and atomic rename or equivalent safe no-overwrite pattern.",
        ],
        "remaining": "OS-specific no-follow, hardlink and TOCTOU mitigation require review and executable negative tests.",
    },
    "AI-SEC-03": {
        "severity": "HIGH", "status": "SPECIFIED_UNTESTED",
        "controls": [
            "Record content_integrity_verified and publisher_provenance_verified as independent evidence booleans, both default false.",
            "Publisher provenance true only after externally corroborated source identity/checksum or independently audited retrieval chain bound to the raw bytes.",
            "A valid CSV and matching self-declared SHA cannot imply provider authenticity. Forged URL with internally consistent candles => CONTENT_VALID_SOURCE_UNVERIFIED.",
        ],
        "remaining": "No trusted publisher provenance or market data has been collected.",
    },
    "AI-SEC-04": {
        "severity": "MEDIUM", "status": "SCHEMA_DRAFT_NOT_HASHED_FROM_DATA",
        "controls": [
            "Canonical schema version candle4h-v1: five numeric OHLCV fields plus open_time_ms, in precisely that order.",
            "Raw CSV input must declare timestamp_unit as milliseconds or microseconds; reject fractional microsecond-to-millisecond conversions.",
            "Canonical open time must be integer milliseconds and UTC aligned to 14400000; keep raw row order and reject unsorted/duplicate input rather than sorting it.",
            "Numeric fields require finite base-10 decimals, no whitespace surprises, normalise signed zero to 0 and remove redundant trailing decimal zeros.",
            "Proposed canonical serialization is UTF-8 JSON Lines with sorted=False, keys in published order, no extra keys, '\\n' line terminators; freeze golden digests before real processing.",
        ],
        "remaining": "CSV column mapping, locale/encoding/BOM and full decimal representation require independent review before implementation.",
    },
    "AI-SEC-05": {
        "severity": "MEDIUM", "status": "SPECIFIED_UNTESTED",
        "controls": [
            "Synthetic fixtures use explicit injected clock tagged SYNTHETIC_ONLY; cannot count as real prospective evidence.",
            "Real finality uses a trusted non-manifest clock: candle open + 14400000ms must be <= current time, with explicit safety margin as future reviewed parameter.",
            "Report separate candle_integrity_valid and prospective_minimum_complete; 60 complete days from 2026-12-01 cannot end before 2027-01-30T00:00:00Z.",
        ],
        "remaining": "No trusted clock source or data finality tests have been implemented.",
    },
    "AI-SEC-06": {
        "severity": "MEDIUM", "status": "FIXTURE_MATRIX_EXPANDED_ON_PAPER",
        "controls": [
            "Split compound F08-F12 into single-fault cases with stable expected codes; preserve original F01-F15 mapping.",
            "Add ZIP metadata/data descriptor/compression/encoding, quoted-field, CSV injection, output collision and numeric grammar cases.",
            "Record boundary below/at/above each size and time limit; don't claim registry tests as executed adversarial fixtures.",
        ],
        "remaining": "Synthetic fixture bytes, golden digests and executable malicious-input tests do not yet exist.",
    },
    "AI-SEC-07": {
        "severity": "MEDIUM", "status": "SPECIFIED_UNTESTED",
        "controls": [
            "Future local verifier must run without Binance credentials and in a network-restricted runtime; separate from archive downloader/backtester.",
            "Disallow network, subprocess launching, exchange modules and strategy imports; add negative runtime tests to demonstrate the boundary.",
        ],
        "remaining": "Boolean policy fields are not a sandbox or runtime enforcement.",
    },
    "AI-SEC-08": {
        "severity": "MEDIUM", "status": "SPECIFIED_UNTESTED",
        "controls": [
            "Document exact commit, contract digest, review identity, evidence location, independent attribution check, findings and explicit owner decision separately.",
            "Never convert AI review, PR merge, complete-looking reviewer form or repository CI into security signoff.",
        ],
        "remaining": "No independent human signoff or implementation approval was obtained.",
    },
}
ERROR_CODES = [
    "RAW_SIZE_EXCEEDED", "ZIP_ENTRY_COUNT", "ZIP_EXPANSION_EXCEEDED",
    "ZIP_RATIO_EXCEEDED", "ZIP_UNSAFE_MEMBER", "ZIP_BAD_CRC",
    "ZIP_ENCRYPTED", "ZIP_UNSUPPORTED_COMPRESSION", "ZIP_NESTED",
    "INPUT_SYMLINK_OR_SPECIAL", "INPUT_OUTSIDE_ROOT", "INPUT_CHANGED",
    "ROW_TOO_LARGE", "RECORD_COUNT_EXCEEDED", "CSV_FIELD_COUNT", "CSV_INVALID_ENCODING",
    "CSV_INJECTION_UNSAFE_OUTPUT", "TIMESTAMP_UNIT_INVALID",
    "TIMESTAMP_PRECISION_LOSS", "UTC_4H_MISALIGNED",
    "CANDLE_DUPLICATE_OR_GAP", "OHLCV_INVALID", "CANDLE_NOT_FINAL",
    "DATA_PARTITION_INVALID", "HASH_MISMATCH", "REPORT_PATH_COLLISION",
    "RUNTIME_CAPABILITY_DENIED", "RESOURCE_DEADLINE_EXCEEDED",
]
TEST_CASES = {
    "B01": ("raw bytes limit: below, equal and above", "RAW_SIZE_EXCEEDED"),
    "B02": ("expanded bytes limit: below, equal and above", "ZIP_EXPANSION_EXCEEDED"),
    "B03": ("compression ratio limit: below, equal and above", "ZIP_RATIO_EXCEEDED"),
    "B04": ("row byte limit: below, equal and above", "ROW_TOO_LARGE"),
    "B05": ("record count limit: below, equal and above", "RECORD_COUNT_EXCEEDED"),
    "B06": ("deadline boundary and cancel", "RESOURCE_DEADLINE_EXCEEDED"),
    "N01": ("symlink or special file entry", "INPUT_SYMLINK_OR_SPECIAL"),
    "N02": ("path traversal or outside input root", "INPUT_OUTSIDE_ROOT"),
    "N03": ("file changes between hash and parse", "INPUT_CHANGED"),
    "N04": ("ZIP absolute, backslash, UTF-8 path or member symlink", "ZIP_UNSAFE_MEMBER"),
    "N05": ("ZIP duplicate entry, extra member or nested archive", "ZIP_ENTRY_COUNT"),
    "N06": ("ZIP incorrect CRC", "ZIP_BAD_CRC"),
    "N07": ("ZIP encryption flag", "ZIP_ENCRYPTED"),
    "N08": ("ZIP unsupported compression method", "ZIP_UNSUPPORTED_COMPRESSION"),
    "N09": ("quoted CSV field exceeds row limit", "ROW_TOO_LARGE"),
    "N10": ("CSV BOM/encoding invalid under declared policy", "CSV_INVALID_ENCODING"),
    "N11": ("CSV formula injection in report/export", "CSV_INJECTION_UNSAFE_OUTPUT"),
    "N12": ("millisecond/microsecond precision mismatch", "TIMESTAMP_PRECISION_LOSS"),
    "N13": ("duplicated/omitted/out-of-order 4h candle", "CANDLE_DUPLICATE_OR_GAP"),
    "N14": ("nonfinite, huge exponent, negative or inconsistent OHLCV", "OHLCV_INVALID"),
    "N15": ("candle unclosed at trusted clock", "CANDLE_NOT_FINAL"),
    "N16": ("warmup/prospective overlap", "DATA_PARTITION_INVALID"),
    "N17": ("raw digest disagrees with bytes", "HASH_MISMATCH"),
    "N18": ("output report name exists or directory unsafe", "REPORT_PATH_COLLISION"),
    "N19": ("network, Binance or strategy import attempted", "RUNTIME_CAPABILITY_DENIED"),
}
EXPECTED_STATUS = {
    "format_validated": False,
    "content_integrity_verified": False,
    "publisher_provenance_verified": False,
    "prospective_minimum_complete": False,
    "synthetic_fixture_executed": False,
    "independent_security_review_verified": False,
    "local_verifier_implementation_authorized": False,
    "h01_backtesting_authorized": False,
    "paper_trading_authorized": False,
    "live_trading_authorized": False,
}


def remediation_report():
    if set(REMEDIATIONS) != {f"AI-SEC-{i:02d}" for i in range(1, 9)}:
        raise ValueError("incomplete BTC-031 findings registry")
    if any(v["status"] == "TESTED_OR_APPROVED" for v in REMEDIATIONS.values()):
        raise PermissionError("unsupported approval status")
    if any(EXPECTED_STATUS.values()):
        raise PermissionError("BTC-032 cannot change authorization or evidence status")
    error_codes = set(ERROR_CODES)
    if len(error_codes) != len(ERROR_CODES):
        raise ValueError("error codes must be unique")
    if not all(expected in error_codes for _,expected in TEST_CASES.values()):
        raise ValueError("unknown expected test error")
    return {
        "program": VERSION,
        "reviewed_commit": SOURCE_REVIEW_SHA,
        "btc027_contract_sha256": PARENT_CONTRACT_SHA,
        "h01_v2_spec_sha256": H01_SPEC_SHA,
        "remediations": REMEDIATIONS,
        "error_codes_proposed": ERROR_CODES,
        "test_cases_proposed_not_executed": {key: list(value) for key, value in TEST_CASES.items()},
        "evidence_and_authorization": EXPECTED_STATUS,
        "decision": "CONTRACT_IMPROVED_NO_VERIFIER_IMPLEMENTATION_AUTHORIZED",
        "limitations": [
            "This is a revised specification and test plan, not a security fix to implemented file I/O.",
            "No local file verifier, synthetic ZIP/CSV attacks, market data validation or strategy backtest was run.",
            "Independent security certification and product-owner implementation approval are not present.",
        ]
    }


def main():
    parser=argparse.ArgumentParser(description="BTC-032 security remediation design; no verifier")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    result=remediation_report()
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({"program":VERSION,"findings":len(REMEDIATIONS),
                      "decision":result["decision"]},indent=2))


if __name__=="__main__":
    main()
