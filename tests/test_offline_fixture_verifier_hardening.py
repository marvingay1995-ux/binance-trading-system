"""BTC-047 synthetic-only filesystem and bounded-parser security regression tests."""
import io
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from btc_engine.offline_fixture_verifier import (
    SyntheticVerificationError, _csv_canonical, _safe_read,
    _zip_csv, verify_generated, write_report_new,
)
from btc_engine.synthetic_fixture_generator import BASE_CSV, generate


class BTC047SyntheticHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "invented"
        generate(str(self.root))

    def reject(self, code, operation, *args):
        with self.assertRaises(SyntheticVerificationError) as ctx:
            operation(*args)
        self.assertEqual(ctx.exception.code, code)

    def test_positive_fixture_hashes_unchanged(self):
        for name in ("golden.csv", "golden.zip"):
            with self.subTest(name=name):
                result = verify_generated(str(self.root), name)
                self.assertEqual(result["status"], "SYNTHETIC_INTEGRITY_ONLY")
                self.assertFalse(result["publisher_provenance_verified"])
                self.assertFalse(result["real_market_data_verified"])

    def test_reader_rejects_limit_below_file_size(self):
        size = (self.root / "golden.csv").stat().st_size
        self.reject("RAW_SIZE_EXCEEDED", _safe_read, str(self.root), "golden.csv", size - 1)
        self.assertEqual(_safe_read(str(self.root), "golden.csv", size), BASE_CSV)

    def test_reader_rejects_invalid_maximum(self):
        self.reject("RAW_SIZE_EXCEEDED", _safe_read, str(self.root), "golden.csv", 0)
        self.reject("RAW_SIZE_EXCEEDED", _safe_read, str(self.root), "golden.csv", 200001)

    def test_reader_requires_approved_file_basename(self):
        for filename in ("../golden.csv", "unknown.csv", "/tmp/golden.csv", "golden.jsonl"):
            self.reject("SYNTHETIC_FILE_NOT_ALLOWED", _safe_read, str(self.root), filename)

    def test_symlink_input_and_parent_rejected(self):
        target = self.root / "golden.csv"
        target.unlink()
        try:
            target.symlink_to(self.root / "golden.jsonl")
        except (NotImplementedError, OSError):
            self.skipTest("symlinks unavailable")
        self.reject("INPUT_SYMLINK_OR_SPECIAL", verify_generated, str(self.root), "golden.csv")
        alias = self.base / "linked-root"
        alias.symlink_to(self.root, target_is_directory=True)
        self.reject("INPUT_OUTSIDE_ROOT", verify_generated, str(alias), "golden.csv")

    def test_reader_nonregular_directory_rejected(self):
        target = self.root / "golden.csv"
        target.unlink()
        target.mkdir()
        self.reject("INPUT_SYMLINK_OR_SPECIAL", verify_generated, str(self.root), "golden.csv")

    def test_csv_line_over_limit_is_rejected_before_parsing(self):
        oversized = BASE_CSV.replace(b",100,105,", b"," + b"8" * 4097 + b",105,", 1)
        self.reject("ROW_TOO_LARGE", _csv_canonical, oversized)

    def test_quoted_multiline_csv_not_allowed_by_synthetic_contract(self):
        quoted = BASE_CSV.replace(b"100,105", b'"100\n",105', 1)
        self.reject("CSV_INVALID_ENCODING", _csv_canonical, quoted)

    def test_zip_claimed_length_exceeds_strict_synthetic_limit(self):
        raw = io.BytesIO()
        with zipfile.ZipFile(raw, "w", allowZip64=False) as z:
            info = zipfile.ZipInfo("invented.csv", date_time=(2020, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_STORED
            z.writestr(info, b"A" * 50)
        payload = bytearray(raw.getvalue())
        central = payload.find(b"PK\x01\x02")
        self.assertGreaterEqual(central, 0)
        # Central-directory uncompressed size: offset 24.
        payload[central + 24:central + 28] = (200001).to_bytes(4, "little")
        self.reject("ZIP_EXPANSION_EXCEEDED", _zip_csv, bytes(payload))

    def test_report_parent_symlink_rejected(self):
        report = verify_generated(str(self.root), "golden.csv")
        alias = self.base / "report-alias"
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.reject("REPORT_PATH_COLLISION", write_report_new, str(alias / "result.json"), report)
        self.assertFalse((self.root / "result.json").exists())

    def test_network_process_calls_not_required_for_validation(self):
        with patch("socket.socket", side_effect=AssertionError("network forbidden")), \
             patch("subprocess.Popen", side_effect=AssertionError("subprocess forbidden")):
            verify_generated(str(self.root), "golden.csv")
            verify_generated(str(self.root), "golden.zip")

    def test_historical_real_data_gate_untouched(self):
        from btc_engine.verifier_implementation_decision import decision_record
        self.assertEqual(decision_record()["decision"], "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")


if __name__ == "__main__":
    unittest.main()
