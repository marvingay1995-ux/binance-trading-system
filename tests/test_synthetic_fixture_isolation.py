import io
import json
import socket
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from btc_engine.synthetic_fixture_coverage import expanded_fixture_bytes
from btc_engine.synthetic_fixture_generator import fixture_bytes, generate, LABEL
from btc_engine.synthetic_fixture_isolation import (
    CASES, SyntheticLimitExceeded, capped_synthetic_zip_read,
    make_small_compressed_zip, make_unsupported_method_zip,
    remaining_case_report, test_only_input_symlink_guard,
    test_only_record_budget,
)


class RemainingSyntheticSecurityProbeTests(unittest.TestCase):
    def test_s11_small_expansion_cap_refusal(self):
        data = make_small_compressed_zip()
        self.assertLess(len(data), 16_384)
        with self.assertRaises(SyntheticLimitExceeded):
            capped_synthetic_zip_read(data, expanded_cap=128)
        self.assertEqual(capped_synthetic_zip_read(data, expanded_cap=256), 256)
        with self.assertRaises(ValueError):
            capped_synthetic_zip_read(data, expanded_cap=0)

    def test_s12_tiny_unsupported_zip_method(self):
        raw = make_unsupported_method_zip()
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            self.assertEqual(archive.infolist()[0].compress_type, 99)
            with self.assertRaises(NotImplementedError):
                archive.read(archive.infolist()[0])
        # Python ZIP library behavior only; not verifier acceptance.

    def test_s13_symlink_refused_in_temporary_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            regular = root / "invented.csv"
            regular.write_bytes(b"synthetic-only")
            link = root / "link.csv"
            try:
                link.symlink_to(regular)
            except (OSError, NotImplementedError):
                self.skipTest("symlink unavailable")
            with self.assertRaises(ValueError):
                test_only_input_symlink_guard(link)
            self.assertTrue(test_only_input_symlink_guard(regular))

    def test_s14_existing_output_refusal_is_non_destructive(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "existing"
            destination.mkdir()
            sentinel = destination / "sentinel.txt"
            sentinel.write_text("keep")
            with self.assertRaises(FileExistsError):
                generate(str(destination))
            self.assertEqual(sentinel.read_text(), "keep")

    def test_s17_fixture_creation_does_not_use_socket_or_subprocess(self):
        with patch("socket.socket", side_effect=AssertionError("network call forbidden")), \
             patch("socket.create_connection", side_effect=AssertionError("network connection forbidden")), \
             patch("subprocess.Popen", side_effect=AssertionError("subprocess forbidden")):
            self.assertEqual(len(fixture_bytes()), 9)
            self.assertEqual(len(expanded_fixture_bytes()), 12)
            self.assertEqual(remaining_case_report()["provenance"], LABEL)
        # Monkeypatch is NOT an OS-level sandbox.

    def test_s18_small_record_budget_boundary(self):
        self.assertEqual(test_only_record_budget(range(99), maximum=100), 99)
        self.assertEqual(test_only_record_budget(range(100), maximum=100), 100)
        with self.assertRaises(SyntheticLimitExceeded):
            test_only_record_budget(range(101), maximum=100)

    def test_s18_does_not_consume_more_than_limit_plus_one(self):
        calls = []
        def values():
            for i in range(500):
                calls.append(i)
                yield i
        with self.assertRaises(SyntheticLimitExceeded):
            test_only_record_budget(values(), maximum=100)
        self.assertEqual(len(calls), 101)

    def test_report_retains_future_verifier_no_go(self):
        report = remaining_case_report()
        self.assertEqual(set(CASES), set(report["cases"]))
        self.assertEqual(len(report["cases"]), 6)
        self.assertTrue(all("VERIFIER" not in x["status"] for x in report["cases"].values()))
        self.assertFalse(report["real_market_data_authorized"])
        self.assertFalse(report["h01_backtesting_authorized"])
        self.assertFalse(report["trading_authorized"])
        self.assertEqual(report["security_verdict"], "SYNTHETIC_HARNESS_CHECKS_ONLY_VERIFIER_NOT_IMPLEMENTED")

    def test_report_deterministic(self):
        report = remaining_case_report()
        self.assertEqual(json.loads(json.dumps(report, sort_keys=True)), report)


if __name__ == "__main__":
    unittest.main()
