"""BTC-073 static synthetic fixture integrity and parser-boundary regressions."""
import json
import unittest
from unittest.mock import patch

from btc_engine.r1_pinned_fixture_integrity import (
    EXPECTED_SHA256, EXPECTED_SIZE, assert_registered_invented_bytes,
)
from btc_engine.r1_offline_synthetic_json import (
    SYNTHETIC_FIXTURES, review_frozen_fixture, _validate_json_klines,
)
from btc_engine.r1_offline_http_response import invented_response, review_invented_response


class BTC073FixturePinningTests(unittest.TestCase):
    def test_static_digests_match_frozen_invented_fixtures(self):
        for interval, data in SYNTHETIC_FIXTURES.items():
            with self.subTest(interval=interval):
                self.assertEqual(assert_registered_invented_bytes(interval, data),
                                 EXPECTED_SHA256[interval])
                self.assertEqual(len(data), EXPECTED_SIZE)

    def test_expected_digest_mapping_cannot_be_mutated(self):
        with self.assertRaises(TypeError):
            EXPECTED_SHA256["1h"] = "0" * 64

    def test_exact_length_but_modified_bytes_refused(self):
        for interval, data in SYNTHETIC_FIXTURES.items():
            forged = bytearray(data)
            forged[0] = 32
            with self.subTest(interval=interval):
                with self.assertRaises(PermissionError):
                    assert_registered_invented_bytes(interval, bytes(forged))

    def test_registry_substitution_rejected_by_both_gateways(self):
        for interval, original in SYNTHETIC_FIXTURES.items():
            tampered=json.loads(original)
            tampered[0][1]="103"
            tampered[0][2]="105"
            tampered[0][3]="102"
            tampered[0][4]="104"
            malicious=json.dumps(tampered, separators=(",", ":")).encode("ascii")
            with self.subTest(interval=interval):
                with patch.dict(SYNTHETIC_FIXTURES, {interval: malicious}):
                    with self.assertRaises(PermissionError):
                        review_frozen_fixture(interval)
                    with self.assertRaises(PermissionError):
                        invented_response(interval)
                    with self.assertRaises(PermissionError):
                        review_invented_response(interval)

    def test_original_registered_payload_accepted(self):
        for interval in ("1h","4h"):
            self.assertTrue(review_frozen_fixture(interval)["synthetic_only"])
            self.assertTrue(review_invented_response(interval)["synthetic_only"])

    def test_unknown_interval_and_nonbytes_refused(self):
        with self.assertRaises(ValueError):
            assert_registered_invented_bytes("15m", b"")
        for value in (None, bytearray(246), "abc", b""):
            with self.assertRaises(PermissionError):
                assert_registered_invented_bytes("1h", value)

    def test_direct_internal_parser_not_a_trusted_gateway(self):
        data=json.loads(SYNTHETIC_FIXTURES["1h"])
        data[0][1]="103"
        data[0][2]="105"
        data[0][3]="102"
        data[0][4]="104"
        altered=json.dumps(data,separators=(",", ":")).encode("ascii")
        # The internal validator is not an externally exposed ingestion interface.
        self.assertEqual(len(_validate_json_klines(altered,"1h")),3)
        with self.assertRaises(PermissionError):
            review_frozen_fixture("1h",altered)

    def test_no_network_or_process(self):
        with patch("socket.socket",side_effect=AssertionError("network")), \
             patch("subprocess.run",side_effect=AssertionError("process")), \
             patch("builtins.open",side_effect=AssertionError("disk")):
            self.assertTrue(review_invented_response("1h")["synthetic_only"])

    def test_no_real_data_or_trade_permission(self):
        from btc_engine.r1_offline_http_response import security_decision
        x=security_decision()
        for key in ("real_http_client_implemented","external_json_admission_authorized",
                    "real_market_data_ingestion_authorized","h01_backtesting_authorized",
                    "paper_trading_authorized","live_spot_authorized",
                    "order_execution_authorized","docker_execution_authorized"):
            self.assertFalse(x[key])

    def test_malformed_payload_raises_without_record_mutation(self):
        for interval, data in list(SYNTHETIC_FIXTURES.items()):
            with self.assertRaises(PermissionError):
                review_frozen_fixture(interval,data+b" ")
            self.assertEqual(SYNTHETIC_FIXTURES[interval],data)

if __name__ == "__main__":
    unittest.main()
