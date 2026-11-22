"""BTC-034 specification and golden vectors only. No fixture generator or verifier.

Hard-coded invented reference data is not exchange market data. Computing
hashes over these literal constants is contract checking, not file ingestion.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .security_contract_acceptance import acceptance_report

VERSION = "BTC-034-v1"
SOURCE_COMMIT = "1c8ddb1f5af0760c60e30f5d5cf5849a9fc563f5"
SCHEMA = {
    "id": "synthetic-candle4h-v1",
    "column_order": ["open_time_ms", "open", "high", "low", "close", "volume"],
    "header": "open_time_ms,open,high,low,close,volume",
    "encoding": "UTF-8 no BOM",
    "line_ending": "LF",
    "delimiter": ",",
    "quoting": "not allowed in v1 numeric columns",
    "timezone": "UTC",
    "timestamp_units": "explicit milliseconds for the golden CSV; other inputs must declare units",
    "canonical_time": "integer milliseconds, exactly divisible by 14400000",
    "numeric_grammar": "ASCII unsigned finite base-10 decimal, no exponent or whitespace, optional decimal point, no leading +",
    "numeric_normalization": "remove redundant leading zeros and trailing fractional zeros; normalize zero to 0",
    "canonical_encoding": "UTF-8 JSON Lines, keys in column_order, no spaces, LF after every row, numbers except timestamp stored as normalized decimal strings",
    "canonical_order": "preserve input order; never sort to hide missing or duplicate times",
    "out_of_scope": ["authentic Binance CSV format and variable provider columns", "actual market data", "H01 indicators", "trades"],
}
GOLDEN_CSV = (
    "open_time_ms,open,high,low,close,volume\n"
    "1778803200000,100,105,99,103,1.5\n"
    "1778817600000,103,108,102,107,2\n"
)
GOLDEN_JSONL = (
    '{"open_time_ms":1778803200000,"open":"100","high":"105","low":"99","close":"103","volume":"1.5"}\n'
    '{"open_time_ms":1778817600000,"open":"103","high":"108","low":"102","close":"107","volume":"2"}\n'
)
CSV_SHA256 = "788537557c96f0792654995f4ddbbf8b1508f4e6972ed7aaa98afeb9c3e890ed"
JSONL_SHA256 = "1ae0a6a2014338e2005da5de366173f1c62a25d5e5624d68ac73a19d63b395b2"
FAULT_CASES = {
    "S01": {"mutation": "remove one warmup bar", "expected": "DATA_PARTITION_INVALID"},
    "S02": {"mutation": "duplicate a UTC open", "expected": "CANDLE_DUPLICATE_OR_GAP"},
    "S03": {"mutation": "replace one timestamp with a non-divisible microsecond value", "expected": "TIMESTAMP_PRECISION_LOSS"},
    "S04": {"mutation": "set OHLC to NaN", "expected": "OHLCV_INVALID"},
    "S05": {"mutation": "set negative volume", "expected": "OHLCV_INVALID"},
    "S06": {"mutation": "inflate a quoted CSV field over limit", "expected": "ROW_TOO_LARGE"},
    "S07": {"mutation": "modify one file byte but retain original checksum", "expected": "HASH_MISMATCH"},
    "S08": {"mutation": "ZIP member name ../escape.csv", "expected": "ZIP_UNSAFE_MEMBER"},
    "S09": {"mutation": "ZIP member is a symbolic link", "expected": "ZIP_UNSAFE_MEMBER"},
    "S10": {"mutation": "ZIP CRC mismatch", "expected": "ZIP_BAD_CRC"},
    "S11": {"mutation": "ZIP expansion above limit", "expected": "ZIP_EXPANSION_EXCEEDED"},
    "S12": {"mutation": "unsupported ZIP compression", "expected": "ZIP_UNSUPPORTED_COMPRESSION"},
    "S13": {"mutation": "input path is symlink", "expected": "INPUT_SYMLINK_OR_SPECIAL"},
    "S14": {"mutation": "output file already exists", "expected": "REPORT_PATH_COLLISION"},
    "S15": {"mutation": "future candle has not closed at trusted clock", "expected": "CANDLE_NOT_FINAL"},
    "S16": {"mutation": "self-declared Binance URL with valid local hashes", "expected": "CONTENT_VALID_SOURCE_UNVERIFIED"},
    "S17": {"mutation": "forbidden network or trading import", "expected": "RUNTIME_CAPABILITY_DENIED"},
    "S18": {"mutation": "record count above maximum", "expected": "RECORD_COUNT_EXCEEDED"},
}
BOUNDS = {
    "raw_bytes": 25_000_000, "expanded_zip_bytes": 50_000_000,
    "zip_entries": 1, "compression_ratio": 100, "records": 100_000,
    "row_bytes": 4096, "columns": 16, "wall_seconds": 30,
}
AUTHORIZATION = {
    "fixture_format_contract_recorded": True,
    "synthetic_fixture_generator_implementation": False,
    "synthetic_fixture_execution": False,
    "local_market_file_verifier": False,
    "real_market_data_ingestion": False,
    "h01_signal_or_backtest": False,
    "paper_trading": False,
    "live_trading": False,
    "binance_account_access": False,
}


def contract_record():
    if acceptance_report()["permissions"]["synthetic_fixture_generator_implementation_authorized"]:
        raise PermissionError("upstream scope gate changed")
    if hashlib.sha256(GOLDEN_CSV.encode("utf-8")).hexdigest() != CSV_SHA256:
        raise ValueError("synthetic CSV reference digest mismatch")
    if hashlib.sha256(GOLDEN_JSONL.encode("utf-8")).hexdigest() != JSONL_SHA256:
        raise ValueError("synthetic JSONL reference digest mismatch")
    if any(value for key, value in AUTHORIZATION.items() if key != "fixture_format_contract_recorded"):
        raise PermissionError("no implementation authority")
    return {
        "program": VERSION,
        "baseline_commit": SOURCE_COMMIT,
        "schema": SCHEMA,
        "golden_reference": {
            "invented_data_only": True,
            "row_count": 2,
            "csv_utf8_sha256": CSV_SHA256,
            "canonical_jsonl_sha256": JSONL_SHA256,
        },
        "fault_cases_proposed_not_executed": FAULT_CASES,
        "proposed_bounds_not_enforced": BOUNDS,
        "authorization": AUTHORIZATION,
        "decision": "SPECIFICATION_RECORDED_IMPLEMENTATION_AUTHORIZATION_WITHHELD",
        "limitations": [
            "Only literal in-code reference strings are hashed; no CSV/ZIP file was created, opened or tested.",
            "Security limits are not demonstrated, and real-data verifier code remains unimplemented.",
            "Separate explicit product-owner authorization is required for synthetic generator implementation.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="BTC-034 specification only")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rec = contract_record()
    Path(args.output).write_text(json.dumps(rec, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"program": VERSION, "decision": rec["decision"]}, indent=2))


if __name__ == "__main__":
    main()
