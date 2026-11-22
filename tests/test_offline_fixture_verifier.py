import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from btc_engine.offline_fixture_verifier import (
    SyntheticVerificationError, verify_generated, write_report_new,
)
from btc_engine.synthetic_fixture_generator import generate, LABEL
from btc_engine.synthetic_fixture_spec import CSV_SHA256, JSONL_SHA256


class SyntheticOnlyOfflineVerifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "generated"
        generate(str(self.root))

    def test_golden_csv_known_source_bytes(self):
        result = verify_generated(str(self.root), "golden.csv")
        self.assertEqual(result["canonical_sha256"], JSONL_SHA256)
        self.assertEqual(result["raw_sha256"], CSV_SHA256)
        self.assertTrue(result["content_integrity_verified"])
        self.assertFalse(result["publisher_provenance_verified"])
        self.assertFalse(result["trading_authorized"])
        self.assertEqual(result["provenance"], LABEL)

    def test_golden_zip_known_source_bytes(self):
        result = verify_generated(str(self.root), "golden.zip")
        self.assertEqual(result["canonical_sha256"], JSONL_SHA256)
        self.assertEqual(result["status"], "SYNTHETIC_INTEGRITY_ONLY")

    def test_modified_bytes_refused(self):
        (self.root / "golden.csv").write_bytes(b"changed")
        with self.assertRaisesRegex(SyntheticVerificationError, "HASH_MISMATCH"):
            verify_generated(str(self.root), "golden.csv")

    def test_unknown_file_refused(self):
        with self.assertRaisesRegex(SyntheticVerificationError, "SYNTHETIC_FILE_NOT_ALLOWED"):
            verify_generated(str(self.root), "changed_bytes.csv")

    def test_symlink_refused(self):
        path = self.root / "golden.csv"
        path.unlink()
        try:
            path.symlink_to(self.root / "golden.jsonl")
        except (OSError, NotImplementedError):
            self.skipTest("symlinks not supported")
        with self.assertRaisesRegex(SyntheticVerificationError, "INPUT_SYMLINK_OR_SPECIAL"):
            verify_generated(str(self.root), "golden.csv")

    def test_outside_root_and_relative_refused(self):
        with self.assertRaisesRegex(SyntheticVerificationError, "INPUT_OUTSIDE_ROOT"):
            verify_generated("relative/directory", "golden.csv")
        with self.assertRaises(SyntheticVerificationError):
            verify_generated(str(self.root), "../golden.csv")

    def test_report_created_once_no_overwrite(self):
        report = verify_generated(str(self.root), "golden.csv")
        dest = Path(self.tmp.name) / "evidence.json"
        digest = write_report_new(str(dest), report)
        self.assertEqual(json.loads(dest.read_text()), report)
        self.assertEqual(len(digest), 64)
        with self.assertRaisesRegex(SyntheticVerificationError, "REPORT_PATH_COLLISION"):
            write_report_new(str(dest), report)

    def test_offline_no_network_process_for_known_fixtures(self):
        with patch("socket.socket", side_effect=AssertionError("network forbidden")), \
             patch("subprocess.Popen", side_effect=AssertionError("process forbidden")):
            verify_generated(str(self.root), "golden.csv")
            verify_generated(str(self.root), "golden.zip")

    def test_existing_historical_denial_untouched(self):
        from btc_engine.verifier_implementation_decision import decision_record
        self.assertEqual(decision_record()["decision"], "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")


if __name__ == "__main__":
    unittest.main()
