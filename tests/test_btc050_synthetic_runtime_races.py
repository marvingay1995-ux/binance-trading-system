"""BTC-050 synthetic process limits and deterministic filesystem race tests."""
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from btc_engine.synthetic_fixture_generator import generate, BASE_CSV
from btc_engine.offline_fixture_verifier import (
    _safe_read, verify_generated, SyntheticVerificationError,
)
from btc_engine.synthetic_isolation_probe import probe_generated


class BTC050SyntheticIsolationAndRaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "synthetic"
        generate(str(self.root))

    def test_known_synthetic_fixtures_in_bounded_child(self):
        for name in ("golden.csv", "golden.zip"):
            with self.subTest(fixture=name):
                record = probe_generated(str(self.root), name)
                self.assertEqual(record["result"]["status"], "SYNTHETIC_INTEGRITY_ONLY")
                self.assertFalse(record["os_network_isolation_verified"])
                self.assertFalse(record["real_data_authorized"])
                self.assertFalse(record["result"]["trading_authorized"])
                if sys.platform.startswith("linux"):
                    self.assertEqual(record["limits"]["linux_cpu_seconds"], 4)

    def test_child_rejects_unknown_fixture_without_spawn(self):
        with patch("btc_engine.synthetic_isolation_probe.subprocess.run", side_effect=AssertionError("must not spawn")):
            with self.assertRaisesRegex(ValueError, "SYNTHETIC_FILE_NOT_ALLOWED"):
                probe_generated(str(self.root), "arbitrary.csv")

    def test_child_refuses_non_absolute_root(self):
        with self.assertRaisesRegex(ValueError, "INPUT_OUTSIDE_ROOT"):
            probe_generated("relative/path", "golden.csv")

    def test_child_timeout_configuration_is_capped(self):
        with self.assertRaisesRegex(ValueError, "INVALID_TIMEOUT"):
            probe_generated(str(self.root), "golden.csv", timeout=10)
        with self.assertRaisesRegex(ValueError, "INVALID_TIMEOUT"):
            probe_generated(str(self.root), "golden.csv", timeout=0)

    def test_python_instrumentation_is_not_os_network_sandbox(self):
        rec = probe_generated(str(self.root), "golden.csv")
        self.assertTrue(rec["result"]["python_network_instrumentation_only"])
        self.assertFalse(rec["result"]["os_network_isolation_verified"])

    @unittest.skipUnless(os.name == "posix" and hasattr(os, "O_NOFOLLOW"), "POSIX no-follow only")
    def test_file_substituted_by_symlink_before_open_is_refused(self):
        """Deterministic open-time race simulation, not a probabilistic attack."""
        real_open = os.open
        source = self.root / "golden.csv"
        outside = self.base / "outside"
        outside.write_bytes(BASE_CSV)
        swapped = [False]

        def swap_before_open(path, flags, *args, **kwargs):
            if path == "golden.csv" and kwargs.get("dir_fd") is not None and not swapped[0]:
                swapped[0] = True
                source.unlink()
                source.symlink_to(outside)
            return real_open(path, flags, *args, **kwargs)

        with patch("btc_engine.offline_fixture_verifier.os.open", side_effect=swap_before_open):
            with self.assertRaises(SyntheticVerificationError) as ctx:
                _safe_read(str(self.root), "golden.csv")
        self.assertTrue(swapped[0])
        self.assertEqual(ctx.exception.code, "INPUT_SYMLINK_OR_SPECIAL")
        self.assertEqual(outside.read_bytes(), BASE_CSV)

    @unittest.skipUnless(os.name == "posix" and hasattr(os, "O_NOFOLLOW"), "POSIX no-follow only")
    def test_root_replaced_by_symlink_before_directory_open_is_refused(self):
        real_open = os.open
        replacement = self.base / "moved_root"
        attack_root = self.root
        switched = [False]

        def switch_root(path, flags, *args, **kwargs):
            if Path(path) == attack_root and not switched[0]:
                switched[0] = True
                attack_root.rename(replacement)
                attack_root.symlink_to(replacement, target_is_directory=True)
            return real_open(path, flags, *args, **kwargs)

        with patch("btc_engine.offline_fixture_verifier.os.open", side_effect=switch_root):
            with self.assertRaises(SyntheticVerificationError) as ctx:
                _safe_read(str(self.root), "golden.csv")
        self.assertTrue(switched[0])
        self.assertEqual(ctx.exception.code, "INPUT_SYMLINK_OR_SPECIAL")

    def test_real_market_verifier_and_trading_denials_preserved(self):
        from btc_engine.verifier_implementation_decision import decision_record
        record = decision_record()
        self.assertEqual(record["decision"], "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")
        self.assertFalse(any(record["permissions"].values()))


if __name__ == "__main__":
    unittest.main()
