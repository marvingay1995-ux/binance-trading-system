"""BTC-036 deterministic, small, invented-only CSV/ZIP fixtures.

No exchange data, network clients, market-file verifier, strategy or trading.
All generated artifacts are visibly labeled as synthetic and stay under a
caller-supplied, newly created directory. The inputs are fixed in source.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import zipfile

from .synthetic_fixture_spec import (
    BOUNDS, CSV_SHA256, GOLDEN_CSV, GOLDEN_JSONL, JSONL_SHA256,
)

LABEL = "SYNTHETIC_NOT_BINANCE_DATA"
MAX_GENERATED_BYTES = 200_000
BASE_CSV = GOLDEN_CSV.encode("utf-8")
BASE_JSONL = GOLDEN_JSONL.encode("utf-8")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _zip_bytes(data, name="invented.csv"):
    if len(data) > MAX_GENERATED_BYTES:
        raise ValueError("synthetic fixture exceeds strict local creation cap")
    info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    info.flag_bits = 0
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, mode="w", allowZip64=False) as archive:
        archive.writestr(info, data)
    result = stream.getvalue()
    if len(result) > MAX_GENERATED_BYTES:
        raise ValueError("generated ZIP exceeds local cap")
    return result


def fixture_bytes():
    """Return controlled, deterministic bytes. These are NOT hostile ZIP bombs."""
    if sha256(BASE_CSV) != CSV_SHA256 or sha256(BASE_JSONL) != JSONL_SHA256:
        raise ValueError("BTC-034 golden reference mismatch")
    cases = {
        "golden.csv": BASE_CSV,
        "golden.jsonl": BASE_JSONL,
        "golden.zip": _zip_bytes(BASE_CSV),
        "duplicate_timestamp.csv": BASE_CSV + BASE_CSV.splitlines(keepends=True)[2],
        "nan_ohlc.csv": BASE_CSV.replace(b",100,105,", b",NaN,105,", 1),
        "negative_volume.csv": BASE_CSV.replace(b",103,1.5\n", b",103,-1.5\n", 1),
        "changed_bytes.csv": BASE_CSV.replace(b",103,1.5\n", b",104,1.5\n", 1),
        "unsafe_member.zip": _zip_bytes(BASE_CSV, "../escape.csv"),
        "unclosed_candle.csv": BASE_CSV.replace(b"1778817600000", b"1778832000000", 1),
    }
    if len(cases) != 9 or any(len(v) > MAX_GENERATED_BYTES for v in cases.values()):
        raise ValueError("fixture inventory violates bounded contract")
    return cases


def manifest_for(cases):
    if set(cases) != set(fixture_bytes()):
        raise ValueError("unexpected fixture name set")
    return {
        "provenance": LABEL,
        "purpose": "offline synthetic fixture generation only; no real market-data verification",
        "btc034_golden_csv_sha256": CSV_SHA256,
        "btc034_golden_jsonl_sha256": JSONL_SHA256,
        "cases": {
            name: {
                "sha256": sha256(data),
                "bytes": len(data),
                "provenance": LABEL,
            }
            for name, data in sorted(cases.items())
        },
        "negative_fixture_status": "GENERATED_NOT_VERIFIER_TESTED",
        "out_of_scope": ["Binance API", "real candles", "H01 backtesting", "orders"],
    }


def generate(output):
    """Create an entirely new directory, never overwriting existing files."""
    root = Path(output)
    if root.is_symlink() or root.exists():
        raise FileExistsError("synthetic fixture destination must not exist")
    # No parent-relative escapes, no known symlink parents.
    if not root.is_absolute():
        raise ValueError("absolute output path required")
    for parent in root.parents:
        if parent.is_symlink():
            raise ValueError("symlink parent forbidden")
    cases = fixture_bytes()
    manifest = manifest_for(cases)
    root.mkdir(mode=0o700, parents=False, exist_ok=False)
    for name, data in cases.items():
        target = root / name
        with target.open("xb") as f:
            f.write(data)
    with (root / "manifest.json").open("x", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="BTC-036 synthetic-only offline fixture generator")
    parser.add_argument("--output", required=True, help="new absolute directory; must not already exist")
    args = parser.parse_args()
    report = generate(args.output)
    print(json.dumps({"provenance": report["provenance"],
                      "fixtures": len(report["cases"]), "status": "SYNTHETIC_GENERATED_ONLY"}, sort_keys=True))


if __name__ == "__main__":
    main()
