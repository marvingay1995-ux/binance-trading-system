"""BTC-037 expanded, bounded, synthetic-only fixture coverage.

This module creates controlled test bytes and verifies inventory/golden hashes.
It is NOT a validator of arbitrary exchange input or a security sandbox.
Non-materialized cases are explicitly tracked, not counted as tested.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

from .synthetic_fixture_generator import BASE_CSV, LABEL, MAX_GENERATED_BYTES, fixture_bytes, sha256
from .synthetic_fixture_spec import FAULT_CASES, CSV_SHA256, BOUNDS

VERSION = "BTC-037-v1"
SOURCE_COMMIT = "da139ff65d447d804359a7c1c82ebdb2e6fb0efe"

def _make_zip(data, *, name="synthetic.csv", symlink=False):
    info = zipfile.ZipInfo(name, date_time=(2020,1,1,0,0,0))
    info.create_system = 3
    info.external_attr = (0o120777 if symlink else 0o100644) << 16
    info.compress_type = zipfile.ZIP_STORED
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", allowZip64=False) as z:
        z.writestr(info, b"target.csv" if symlink else data)
    return out.getvalue()

def _corrupt_crc_zip(data):
    raw = bytearray(_make_zip(data))
    needle = data[:20]
    pos = raw.find(needle)
    if pos < 0:
        raise RuntimeError("test payload location not found")
    raw[pos] ^= 1
    return bytes(raw)

def expanded_fixture_bytes():
    """Create only small single-purpose synthetic samples; never extract ZIP."""
    lines = BASE_CSV.splitlines(keepends=True)
    csv_header, first, second = lines
    scenarios = {
        "S01": csv_header + first,
        "S02": BASE_CSV + second,
        "S03": BASE_CSV.replace(b"1778817600000", b"1778817600000001", 1),
        "S04": BASE_CSV.replace(b",100,105,", b",NaN,105,", 1),
        "S05": BASE_CSV.replace(b",103,1.5\n", b",103,-1.5\n", 1),
        "S06": csv_header + b"1778803200000," + b"9"*4100 + b",105,99,103,1.5\n",
        "S07": BASE_CSV.replace(b",103,1.5\n", b",104,1.5\n", 1),
        "S08": _make_zip(BASE_CSV, name="../escape.csv"),
        "S09": _make_zip(BASE_CSV, name="synthetic.csv", symlink=True),
        "S10": _corrupt_crc_zip(BASE_CSV),
        "S15": BASE_CSV.replace(b"1778817600000", b"1778832000000", 1),
    }
    # Explicitly preserve a self-declared *untrusted* metadata claim. This
    # must NEVER count as exchange provenance verification.
    scenarios["S16"] = json.dumps({
        "source_uri": "https://data.binance.vision/fake.csv",
        "raw_sha256": CSV_SHA256,
        "publisher_verified": False,
        "provenance": LABEL,
        "test_only": True,
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if set(scenarios) - set(FAULT_CASES):
        raise ValueError("unregistered scenario")
    if any(len(x) > min(MAX_GENERATED_BYTES, BOUNDS["raw_bytes"]) for x in scenarios.values()):
        raise ValueError("BTC-037 fixture exceeds local creation cap")
    return scenarios

# Contextual cases cannot be proved by mere bytes. No fake security verdicts.
CONTEXT_ONLY = {
    "S11": "Expansion-limit enforcement requires a separately authorized bounded verifier and controlled ZIP stress harness",
    "S12": "Unsupported compression requires an isolated malformed-archive parser test",
    "S13": "Input symlink protection requires filesystem and OS-specific verifier test",
    "S14": "Report overwrite protection requires an actual report-writing verifier",
    "S17": "Network/trading isolation requires a runtime guard and denial test",
    "S18": "100001-record refusal requires executable bounded streaming validation; avoid large files",
}

def coverage_report():
    cases = expanded_fixture_bytes()
    if set(cases) | set(CONTEXT_ONLY) != set(FAULT_CASES):
        raise ValueError("BTC-034 S01-S18 mapping incomplete")
    return {
        "program": VERSION,
        "baseline": SOURCE_COMMIT,
        "provenance": LABEL,
        "golden_csv_sha256": CSV_SHA256,
        "total_scenarios_registered": len(FAULT_CASES),
        "materialized_fixture_cases": {
            key: {
                "sha256": sha256(value),
                "byte_length": len(value),
                "expected_future_verifier_outcome": FAULT_CASES[key]["expected"],
                "evidence_status": "FIXTURE_BYTES_GENERATED_ONLY_NOT_VERIFIER_TESTED",
            }
            for key, value in sorted(cases.items())
        },
        "context_only_unexecuted": {
            key: {"reason": reason, "expected_future_verifier_outcome": FAULT_CASES[key]["expected"],
                  "evidence_status": "NOT_MATERIALIZED_NOT_TESTED"}
            for key, reason in sorted(CONTEXT_ONLY.items())
        },
        "tests_prove": [
            "deterministic synthetic byte generation and SHA-256 accounting",
            "small ZIP metadata cases and deliberately mismatched CRC test sample construction",
            "complete S01-S18 registry without claiming runtime verifier coverage",
        ],
        "tests_do_not_prove": [
            "actual ZIP/CSV verifier correctly rejects hostile inputs",
            "resource deadline and memory ceilings, filesystem race safety or no-network isolation",
            "authentic Binance market data or trading safety",
        ],
        "security_verdict": "VERIFIER_NOT_IMPLEMENTED_NO_SECURITY_PASS",
        "h01_backtesting_authorized": False,
        "real_market_data_processing_authorized": False,
        "trading_authorized": False,
    }

def main():
    parser = argparse.ArgumentParser(description="BTC-037 synthetic inventory only")
    parser.add_argument("--output", required=True, help="new absolute output directory")
    args = parser.parse_args()
    output = Path(args.output)
    if not output.is_absolute() or output.exists() or any(p.is_symlink() for p in output.parents):
        raise ValueError("output must be a new absolute path with no symlink parents")
    cases = expanded_fixture_bytes()
    report = coverage_report()
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    for key, data in sorted(cases.items()):
        with (output / (key + (".zip" if key in {"S08","S09","S10"} else ".json" if key=="S16" else ".csv"))).open("xb") as stream:
            stream.write(data)
    with (output / "manifest.json").open("x", encoding="utf-8") as stream:
        json.dump(report, stream, sort_keys=True, indent=2)
        stream.write("\n")
    print(json.dumps({"scenario_count": len(FAULT_CASES), "materialized": len(cases),
                      "context_only": len(CONTEXT_ONLY), "security_verdict": report["security_verdict"]},
                     sort_keys=True))

if __name__ == "__main__":
    main()
