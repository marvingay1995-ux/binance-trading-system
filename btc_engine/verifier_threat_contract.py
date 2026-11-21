"""BTC-027 proposed threat model and synthetic fixture *contracts*, not a verifier.

No market data is opened, ZIP parsed, candles evaluated or account accessed.
Tests ensure the specification remains fail-closed; they do not validate a
production security boundary or grant implementation permission.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .spec_amendment import canonical_bytes

VERSION = "BTC-027-v1"
LIMITS = {
    "max_raw_input_bytes": 25_000_000,
    "max_zip_entries": 1,
    "max_uncompressed_bytes": 50_000_000,
    "max_compression_ratio": 100,
    "max_candle_records": 100_000,
    "max_row_bytes": 4096,
    "max_field_count": 16,
    "max_name_bytes": 128,
    "maximum_processing_seconds": 30,
    "timestamp_units": ["milliseconds", "microseconds"],
    "accepted_file_types": ["csv", "zip_containing_single_csv"],
}
TRUST_BOUNDARIES = {
    "local_input": "UNTRUSTED_BYTES",
    "file_path": "UNTRUSTED_PATH",
    "manifest": "UNTRUSTED_CLAIMS",
    "publisher_url": "UNVERIFIED_PROVENANCE_CLAIM",
    "expected_sha256": "CLAIM_UNTIL_CORROBORATED",
    "reviewer_approval": "EXTERNAL_HUMAN_ACTION_REQUIRED",
    "output_report": "DATA_INTEGRITY_ONLY_NOT_SOURCE_AUTHENTICATION",
}
THREATS = [
    {"id": "T01", "threat": "ZIP traversal, absolute names and symlink entries", "mitigation": "never extract; allow one flat CSV member; reject path separators, drive prefixes, symlinks, duplicate names"},
    {"id": "T02", "threat": "ZIP bomb, huge rows, many entries, unbounded memory", "mitigation": "bound raw bytes, uncompressed bytes, ratio, entry count, row length, record count and elapsed time; stream carefully"},
    {"id": "T03", "threat": "ZIP corruption, encryption, nested archives and malformed CSV", "mitigation": "reject encrypted/nested members, CRC failure, non-CSV entries, unexpected columns or missing fields"},
    {"id": "T04", "threat": "Symlinked paths, device files, FIFOs, TOCTOU substitution", "mitigation": "reject nonregular input and symlinks, open safely once, hash and parse same opened content, limit allowed root"},
    {"id": "T05", "threat": "Timestamp unit confusion and duplicate or missing 4h candles", "mitigation": "explicit per-file millisecond/microsecond selection, exact UTC 4h opens and continuity"},
    {"id": "T06", "threat": "Nonfinite, negative or inconsistent OHLCV", "mitigation": "decimal numeric parsing, finite positive prices, low <= open/close <= high, finite nonnegative volume"},
    {"id": "T07", "threat": "Unclosed candle, warmup/forward overlap and calendar boundary mistakes", "mitigation": "verify candle finality against trusted collection time and exact registered UTC partitions"},
    {"id": "T08", "threat": "Tampered bytes, fabricated manifest hash or provider identity", "mitigation": "recompute raw/canonical SHA256, bind report to bytes, never infer source authenticity from a URL or digest alone"},
    {"id": "T09", "threat": "Resource exhaustion, output overwrite or report confusion", "mitigation": "minimal output privilege, unique report name, atomic write, deterministic schema, refuse collisions"},
    {"id": "T10", "threat": "Capability creep to remote fetch, trading or H01 signals", "mitigation": "no network, credentials, exchange packages, strategy indicators, order or PnL paths; separate explicit authorization"},
]
FIXTURE_CASES = [
    {"id": "F01", "case": "one valid warmup partition 1200 synthetic contiguous 4h bars", "expected": "PASS_INTEGRITY_ONLY"},
    {"id": "F02", "case": "valid prospective synthetic partition with 360 fully closed 4h bars", "expected": "PASS_INTEGRITY_ONLY"},
    {"id": "F03", "case": "1199 warmup bars", "expected": "REJECT"},
    {"id": "F04", "case": "duplicate or out-of-order UTC timestamp", "expected": "REJECT"},
    {"id": "F05", "case": "missing intermediate 4h bar", "expected": "REJECT"},
    {"id": "F06", "case": "millisecond/microsecond confusion or implicit unit inference", "expected": "REJECT"},
    {"id": "F07", "case": "NaN, infinity, negative volume or inconsistent OHLC", "expected": "REJECT"},
    {"id": "F08", "case": "mismatched actual-byte SHA256 or changed file after hash", "expected": "REJECT"},
    {"id": "F09", "case": "path traversal, absolute ZIP entry or symlink", "expected": "REJECT"},
    {"id": "F10", "case": "ZIP bomb, oversized expanded size, too many entries or zip nesting", "expected": "REJECT"},
    {"id": "F11", "case": "encrypted or malformed CSV/ZIP, inconsistent CRC", "expected": "REJECT"},
    {"id": "F12", "case": "unfinished bar, future collection timestamp or prospective/warmup overlap", "expected": "REJECT"},
    {"id": "F13", "case": "untrusted manifest claims VERIFIED_BY_PROVIDER without corroboration", "expected": "SOURCE_UNVERIFIED"},
    {"id": "F14", "case": "unapproved invocation of H01 signals, backtest, network or orders", "expected": "REJECT"},
    {"id": "F15", "case": "repeat identical synthetic file and immutable config", "expected": "DETERMINISTIC_REPORT"},
]
AUTHORITY = {
    "threat_model_independently_reviewed": False,
    "product_owner_explicit_verifier_implementation_approval": False,
    "negative_control_plan_approved": False,
    "local_verifier_implementation_authorized": False,
    "real_market_data_processing_authorized": False,
    "h01_strategy_backtesting_authorized": False,
    "paper_trading_authorized": False,
    "live_trading_authorized": False,
}


def contract_report():
    if not all(isinstance(n, int) and n > 0 for k,n in LIMITS.items() if k.startswith("max_") or k=="maximum_processing_seconds"):
        raise ValueError("invalid safety resource limits")
    if set(item["id"] for item in FIXTURE_CASES) != {f"F{i:02d}" for i in range(1, 16)}:
        raise ValueError("fixture registry inconsistent")
    if set(item["id"] for item in THREATS) != {f"T{i:02d}" for i in range(1, 11)}:
        raise ValueError("threat registry inconsistent")
    if any(AUTHORITY.values()):
        raise PermissionError("authorization claims cannot be set in BTC-027")
    contract = {
        "program": VERSION,
        "status": "SECURITY_THREAT_AND_FIXTURE_CONTRACT_DRAFT",
        "reference_spec_sha256": hashlib.sha256(canonical_bytes()).hexdigest(),
        "proposed_resource_limits": LIMITS,
        "trust_boundaries": TRUST_BOUNDARIES,
        "threats": THREATS,
        "synthetic_fixture_contracts_not_executed": FIXTURE_CASES,
        "authority": AUTHORITY,
        "decision": "NO_GO_VERIFIER_IMPLEMENTATION_PENDING_SEPARATE_APPROVAL_AND_SECURITY_REVIEW",
        "limitations": [
            "Chosen limits are proposals; they need independent security review and realistic capacity testing.",
            "No real ZIP/CSV parsing, candle validation, dataset authentication, strategy simulation or network operation was performed.",
            "A passing contract unit test is not an executed negative-control fixture against an actual verifier.",
        ],
    }
    canonical = json.dumps(contract,sort_keys=True,separators=(",",":"),ensure_ascii=True)
    return {"contract": contract, "contract_sha256": hashlib.sha256(canonical.encode("ascii")).hexdigest()}


def main():
    parser=argparse.ArgumentParser(description="BTC-027 proposal only; no verifier")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    report=contract_report()
    Path(args.output).write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"program": VERSION,"decision":report["contract"]["decision"],
                      "threats":len(THREATS),"fixtures":len(FIXTURE_CASES)},indent=2))


if __name__=="__main__":
    main()
