"""BTC-053 synthetic report-commit and isolation regression tests.

Only invented BTC-036 fixtures; no real data or trading.
"""
import errno
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from btc_engine.offline_fixture_verifier import (
    SyntheticVerificationError, verify_generated, write_report_new,
)
from btc_engine.synthetic_fixture_generator import generate


@unittest.skipUnless(os.name == "posix", "POSIX staged hardlink publication only")
class BTC053ReportHardening(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.fixtures = self.base / "synthetic"
        self.reports = self.base / "reports"
        self.reports.mkdir(mode=0o700)
        generate(str(self.fixtures))
        self.result = verify_generated(str(self.fixtures), "golden.csv")

    def reject(self, code, fn):
        with self.assertRaises(SyntheticVerificationError) as caught:
            fn()
        self.assertEqual(caught.exception.code, code)

    def assert_no_temp(self):
        self.assertEqual(list(self.reports.glob(".btc053-*")), [])

    def test_success_is_exclusive_and_no_staging_left(self):
        target = self.reports / "report.json"
        digest = write_report_new(str(target), self.result)
        self.assertEqual(len(digest), 64)
        self.assertIn("SYNTHETIC_INTEGRITY_ONLY", target.read_text())
        self.assert_no_temp()
        self.reject("REPORT_PATH_COLLISION", lambda: write_report_new(str(target), self.result))
        self.assert_no_temp()

    def test_preexisting_report_preserved(self):
        target = self.reports / "report.json"
        target.write_bytes(b"NEVER OVERWRITE")
        self.reject("REPORT_PATH_COLLISION", lambda: write_report_new(str(target), self.result))
        self.assertEqual(target.read_bytes(), b"NEVER OVERWRITE")
        self.assert_no_temp()

    def test_preexisting_symlink_refused_without_mutation(self):
        outside = self.base / "outside"
        outside.write_bytes(b"UNCHANGED")
        (self.reports / "report.json").symlink_to(outside)
        self.reject("REPORT_PATH_COLLISION", lambda: write_report_new(str(self.reports / "report.json"), self.result))
        self.assertEqual(outside.read_bytes(), b"UNCHANGED")
        self.assert_no_temp()

    def test_parent_symlink_refused(self):
        alias = self.base / "alias"
        alias.symlink_to(self.reports, target_is_directory=True)
        self.reject("REPORT_PATH_COLLISION", lambda: write_report_new(str(alias / "report.json"), self.result))
        self.assertFalse((self.reports / "report.json").exists())

    def test_partial_write_failure_cleans_stage_without_publishing(self):
        original = os.write
        calls = [0]
        def fail_write(fd, data):
            calls[0] += 1
            if calls[0] == 1:
                return original(fd, data[:min(len(data), 3)])
            raise OSError(errno.ENOSPC, "injected disk full")
        target = self.reports / "report.json"
        with patch("btc_engine.offline_fixture_verifier.os.write", side_effect=fail_write):
            self.reject("REPORT_IO_ERROR", lambda: write_report_new(str(target), self.result))
        self.assertFalse(target.exists())
        self.assert_no_temp()

    def test_link_failure_keeps_destination_absent_and_removes_temp(self):
        target = self.reports / "report.json"
        with patch("btc_engine.offline_fixture_verifier.os.link", side_effect=OSError(errno.EIO, "link refused")):
            self.reject("REPORT_IO_ERROR", lambda: write_report_new(str(target), self.result))
        self.assertFalse(target.exists())
        self.assert_no_temp()

    def test_unlinked_output_path_collision_race_is_fail_closed(self):
        target = self.reports / "report.json"
        real_link = os.link
        def race_link(source, dest, **kwargs):
            target.write_bytes(b"RACER")
            return real_link(source, dest, **kwargs)
        with patch("btc_engine.offline_fixture_verifier.os.link", side_effect=race_link):
            self.reject("REPORT_PATH_COLLISION", lambda: write_report_new(str(target), self.result))
        self.assertEqual(target.read_bytes(), b"RACER")
        self.assert_no_temp()

    def test_historical_no_go_and_false_provenance(self):
        from btc_engine.verifier_implementation_decision import decision_record
        self.assertFalse(self.result["publisher_provenance_verified"])
        self.assertFalse(self.result["trading_authorized"])
        self.assertEqual(decision_record()["decision"], "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")


if __name__ == "__main__":
    unittest.main()
