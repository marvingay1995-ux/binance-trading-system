"""BTC-048 synthetic-only hardening evidence checks.

Testing controlled invented bytes and controlled instrumentation ONLY.
Not a penetration test or evidence of secure general file processing.
"""
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from btc_engine.synthetic_fixture_generator import BASE_CSV, generate
from btc_engine.offline_fixture_verifier import (
    _safe_read, verify_generated, write_report_new, SyntheticVerificationError,
)

class BTC048HardeningEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "invented"
        generate(str(self.root))

    def reject(self, expected, fn, *args):
        with self.assertRaises(SyntheticVerificationError) as cm:
            fn(*args)
        self.assertEqual(cm.exception.code, expected)

    def test_bounded_read_chunks(self):
        original = os.read
        observed = []
        def bounded_read(fd, length):
            observed.append(length)
            self.assertLessEqual(length, 8192)
            return original(fd, length)
        with patch("btc_engine.offline_fixture_verifier.os.read", side_effect=bounded_read):
            result = _safe_read(str(self.root), "golden.csv")
        self.assertEqual(result, BASE_CSV)
        self.assertTrue(observed)

    def test_detects_same_file_size_with_changed_stat(self):
        real_fstat = os.fstat
        count = [0]
        def changed_stat(fd):
            item = real_fstat(fd)
            if stat.S_ISREG(item.st_mode):
                count[0] += 1
                if count[0] > 1:
                    # Python os.stat_result has no mtime_ns constructor arg;
                    # fake changed size in the last descriptor observation.
                    fields = list(item)
                    fields[6] = item.st_size + 1
                    return os.stat_result(fields)
            return item
        with patch("btc_engine.offline_fixture_verifier.os.fstat", side_effect=changed_stat):
            self.reject("INPUT_CHANGED", _safe_read, str(self.root), "golden.csv")

    def test_root_ancestor_symlink_is_refused(self):
        root_parent = Path(self.tmp.name)
        alias = root_parent / "aliased"
        try:
            alias.symlink_to(root_parent, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.reject("INPUT_OUTSIDE_ROOT", _safe_read, str(alias / "invented"), "golden.csv")

    def test_exact_known_fixtures_still_pass(self):
        for name in ("golden.csv", "golden.zip"):
            with self.subTest(name=name):
                report = verify_generated(str(self.root), name)
                self.assertEqual(report["status"], "SYNTHETIC_INTEGRITY_ONLY")
                self.assertFalse(report["publisher_provenance_verified"])
                self.assertFalse(report["real_market_data_verified"])
                self.assertFalse(report["trading_authorized"])

    def test_output_collision_does_not_overwrite(self):
        dest = Path(self.tmp.name) / "evidence.json"
        dest.write_bytes(b"sentinel")
        self.reject("REPORT_PATH_COLLISION", write_report_new, str(dest), {"test_only": True})
        self.assertEqual(dest.read_bytes(), b"sentinel")

    def test_unknown_file_still_denied(self):
        self.reject("SYNTHETIC_FILE_NOT_ALLOWED", verify_generated, str(self.root), "random.csv")

    def test_general_verifier_authorization_still_denied(self):
        from btc_engine.verifier_implementation_decision import decision_record
        self.assertEqual(decision_record()["decision"], "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")
        self.assertFalse(any(decision_record()["permissions"].values()))

if __name__ == "__main__":
    unittest.main()
