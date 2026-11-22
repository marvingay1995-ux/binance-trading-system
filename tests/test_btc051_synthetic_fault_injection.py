"""BTC-051 deterministic synthetic-only fault injection against actual entry points.

These tests model exceptions, not a hostile operating system. They do not
authorize real exchange files, exchange APIs, strategy logic or trading.
"""
import errno
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from btc_engine.offline_fixture_verifier import (
    SyntheticVerificationError, _safe_read, verify_generated, write_report_new,
)
from btc_engine.synthetic_fixture_generator import BASE_CSV, generate
from btc_engine.synthetic_isolation_probe import probe_generated


class BTC051SyntheticFaultInjection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "fixtures"
        generate(str(self.root))

    def reject(self, code, fn, *args, **kwargs):
        with self.assertRaises(SyntheticVerificationError) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(ctx.exception.code, code)

    def test_read_eio_is_stable_failure_and_fds_close(self):
        real_open, real_close = os.open, os.close
        opened, closed = [], []
        def observe_open(*args, **kwargs):
            fd = real_open(*args, **kwargs)
            opened.append(fd)
            return fd
        def observe_close(fd):
            closed.append(fd)
            return real_close(fd)
        with patch("btc_engine.offline_fixture_verifier.os.open", side_effect=observe_open), \
             patch("btc_engine.offline_fixture_verifier.os.close", side_effect=observe_close), \
             patch("btc_engine.offline_fixture_verifier.os.read", side_effect=OSError(errno.EIO, "simulated read failure")):
            self.reject("INPUT_IO_ERROR", _safe_read, str(self.root), "golden.csv")
        self.assertEqual(len(opened), 2)
        self.assertCountEqual(opened, closed)
        self.assertEqual(verify_generated(str(self.root), "golden.csv")["status"], "SYNTHETIC_INTEGRITY_ONLY")

    def test_fstat_eio_refused_and_open_descriptors_closed(self):
        actual = os.fstat
        real_open, real_close = os.open, os.close
        opened, closed = [], []
        def open_instrument(*a, **kw):
            fd = real_open(*a, **kw)
            opened.append(fd)
            return fd
        def close_instrument(fd):
            closed.append(fd)
            return real_close(fd)
        count = [0]
        def fail_second_stat(fd):
            count[0] += 1
            if count[0] == 2:
                raise OSError(errno.EIO, "synthetic fstat failure")
            return actual(fd)
        with patch("btc_engine.offline_fixture_verifier.os.open", side_effect=open_instrument), \
             patch("btc_engine.offline_fixture_verifier.os.close", side_effect=close_instrument), \
             patch("btc_engine.offline_fixture_verifier.os.fstat", side_effect=fail_second_stat):
            self.reject("INPUT_IO_ERROR", _safe_read, str(self.root), "golden.csv")
        self.assertEqual(len(opened), 2)
        self.assertCountEqual(opened, closed)

    def test_open_eio_refused_without_leaking_root_fd(self):
        actual_open, actual_close = os.open, os.close
        opened, closed = [], []
        def fail_file_open(path, *args, **kwargs):
            if path == "golden.csv":
                raise OSError(errno.EIO, "simulated file open failure")
            fd = actual_open(path, *args, **kwargs)
            opened.append(fd)
            return fd
        def close_trace(fd):
            closed.append(fd)
            return actual_close(fd)
        with patch("btc_engine.offline_fixture_verifier.os.open", side_effect=fail_file_open), \
             patch("btc_engine.offline_fixture_verifier.os.close", side_effect=close_trace):
            self.reject("INPUT_IO_ERROR", _safe_read, str(self.root), "golden.csv")
        self.assertEqual(len(opened), 1)
        self.assertEqual(opened, closed)

    def test_zero_length_read_reports_changed_input(self):
        with patch("btc_engine.offline_fixture_verifier.os.read", return_value=b""):
            self.reject("INPUT_CHANGED", _safe_read, str(self.root), "golden.csv")

    def test_subprocess_timeout_is_stable_refusal(self):
        with patch("btc_engine.synthetic_isolation_probe.subprocess.run",
                   side_effect=subprocess.TimeoutExpired(cmd="controlled-fixture-only", timeout=0.01)):
            with self.assertRaisesRegex(RuntimeError, "^SYNTHETIC_CHILD_TIMEOUT$"):
                probe_generated(str(self.root), "golden.csv")

    def test_subprocess_start_eio_is_stable_refusal(self):
        with patch("btc_engine.synthetic_isolation_probe.subprocess.run",
                   side_effect=OSError(errno.EIO, "synthetic launch failure")):
            with self.assertRaisesRegex(RuntimeError, "^SYNTHETIC_CHILD_START_FAILED$"):
                probe_generated(str(self.root), "golden.csv")

    def test_nonzero_child_exit_refused(self):
        completed = subprocess.CompletedProcess(args=["controlled"], returncode=1, stdout="", stderr="failure")
        with patch("btc_engine.synthetic_isolation_probe.subprocess.run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "^SYNTHETIC_CHILD_FAILED$"):
                probe_generated(str(self.root), "golden.csv")

    def test_invalid_child_json_refused(self):
        completed = subprocess.CompletedProcess(args=["controlled"], returncode=0, stdout="not JSON", stderr="")
        with patch("btc_engine.synthetic_isolation_probe.subprocess.run", return_value=completed):
            with self.assertRaisesRegex(RuntimeError, "^SYNTHETIC_CHILD_OUTPUT_INVALID$"):
                probe_generated(str(self.root), "golden.csv")

    def test_child_cannot_claim_network_isolation_or_trading(self):
        import json
        for payload in (
            {"status":"SYNTHETIC_INTEGRITY_ONLY", "os_network_isolation_verified":True,
             "trading_authorized":False, "real_market_data_verified":False},
            {"status":"SYNTHETIC_INTEGRITY_ONLY", "os_network_isolation_verified":False,
             "trading_authorized":True, "real_market_data_verified":False},
        ):
            with self.subTest(payload=payload):
                completed = subprocess.CompletedProcess(args=["controlled"], returncode=0, stdout=json.dumps(payload), stderr="")
                with patch("btc_engine.synthetic_isolation_probe.subprocess.run", return_value=completed):
                    with self.assertRaisesRegex(RuntimeError, "^SYNTHETIC_CHILD_OUTPUT_INVALID$"):
                        probe_generated(str(self.root), "golden.csv")

    def test_report_collision_preserves_original(self):
        output = Path(self.tmp.name) / "report.json"
        output.write_text("SENTINEL")
        self.reject("REPORT_PATH_COLLISION", write_report_new, str(output), {"synthetic_only":True})
        self.assertEqual(output.read_text(), "SENTINEL")

    def test_report_unwritable_destination_does_not_enable_market_processing(self):
        dest = Path(self.tmp.name) / "missing-directory" / "report.json"
        with self.assertRaises((FileNotFoundError, SyntheticVerificationError)):
            write_report_new(str(dest), {"synthetic_only":True})
        self.assertFalse(dest.exists())
        self.assertFalse(any(__import__("btc_engine.verifier_implementation_decision", fromlist=["decision_record"]).decision_record()["permissions"].values()))


if __name__ == "__main__":
    unittest.main()
