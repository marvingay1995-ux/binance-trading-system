"""BTC-069 offline synthetic BTCUSDT parser authorization and negative tests."""
import json
import unittest
from unittest.mock import patch

from btc_engine.r1_offline_synthetic_json import (
    PERIODS, SYNTHETIC_FIXTURES, _validate_json_klines,
    authorization_record, require_live_fetch_or_order, review_frozen_fixture,
)

class BTC069OfflineSyntheticJSONTests(unittest.TestCase):
    def test_explicit_owner_scope_recorded_and_no_real_operations(self):
        r = authorization_record()
        self.assertEqual(r["owner_decision"], "APPROVE_OFFLINE_IMPLEMENTATION_ONLY")
        self.assertTrue(r["offline_invented_fixture_implementation_authorized"])
        for k in ("public_market_fetch_authorized", "authentic_data_ingestion_authorized",
                  "h01_backtesting_authorized", "paper_trading_authorized",
                  "live_spot_authorized", "api_credentials_authorized",
                  "docker_execution_authorized", "spend_authorized"):
            self.assertFalse(r[k])

    def test_frozen_1h_4h_fixture_integrity(self):
        for interval in ("1h", "4h"):
            with self.subTest(interval=interval):
                r=review_frozen_fixture(interval)
                self.assertEqual(r["candle_count"], 3)
                self.assertTrue(r["synthetic_only"])
                self.assertFalse(r["publisher_verified"])
                self.assertFalse(r["signal_or_pnl_calculated"])
                self.assertEqual(r["provenance"],"IN_MODULE_INVENTED_FIXTURE_NOT_BINANCE")

    def test_altered_fixture_rejected_at_external_boundary(self):
        for interval in PERIODS:
            payload=SYNTHETIC_FIXTURES[interval]
            with self.assertRaisesRegex(PermissionError,"NOT_A_FROZEN_SYNTHETIC_FIXTURE"):
                review_frozen_fixture(interval,payload+b" ")

    def test_real_or_unregistered_payload_rejected(self):
        with self.assertRaisesRegex(PermissionError,"NOT_A_FROZEN_SYNTHETIC_FIXTURE"):
            review_frozen_fixture("1h",b'[]')
        with self.assertRaises(ValueError):
            review_frozen_fixture("15m")
        with self.assertRaises(PermissionError):
            review_frozen_fixture("1h","not bytes")

    def test_bad_json_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_JSON"):
            _validate_json_klines(b"{","1h")

    def test_duplicate_missing_candle_fails(self):
        data=json.loads(SYNTHETIC_FIXTURES["1h"])
        data[1][0]=data[0][0]
        with self.assertRaisesRegex(ValueError,"MISSING_DUPLICATED_OR_UNSORTED_CANDLE"):
            _validate_json_klines(json.dumps(data).encode(),"1h")

    def test_nonfinite_and_invalid_ohlc_fail(self):
        data=json.loads(SYNTHETIC_FIXTURES["4h"])
        data[0][2]="nan"
        with self.assertRaisesRegex(ValueError,"INVALID_DECIMAL_FIELD"):
            _validate_json_klines(json.dumps(data).encode(),"4h")
        data=json.loads(SYNTHETIC_FIXTURES["4h"])
        data[0][2]="90"
        with self.assertRaisesRegex(ValueError,"INCONSISTENT_OHLC"):
            _validate_json_klines(json.dumps(data).encode(),"4h")

    def test_malformed_shape_and_limits(self):
        with self.assertRaisesRegex(ValueError,"INVALID_CANDLE_COUNT"):
            _validate_json_klines(b"[]","1h")
        with self.assertRaisesRegex(ValueError,"INVALID_FIXTURE_INPUT"):
            _validate_json_klines(b"0"*9000,"1h")
        with self.assertRaisesRegex(ValueError,"INVALID_KLINE_SHAPE"):
            _validate_json_klines(b'[["x"]]',"1h")

    def test_wrong_timestamp_units_rejected(self):
        rows=json.loads(SYNTHETIC_FIXTURES["1h"])
        rows[0][0] *= 1000
        with self.assertRaisesRegex(ValueError,"INVALID_TIME_OR_TRADES"):
            _validate_json_klines(json.dumps(rows).encode(),"1h")

    def test_no_process_network_or_filesystem_access(self):
        with patch("socket.socket",side_effect=AssertionError("network")):
            with patch("subprocess.run",side_effect=AssertionError("process")):
                self.assertFalse(authorization_record()["public_market_fetch_authorized"])

    def test_no_fake_approval_for_fetch_or_order(self):
        with self.assertRaisesRegex(PermissionError,"BTC069_REAL_DATA_AND_TRADING_NO_GO"):
            require_live_fetch_or_order(owner_approved=True,independent_review=True)

    def test_stable_json_record(self):
        a=authorization_record()
        self.assertEqual(a,json.loads(json.dumps(a,allow_nan=False)))
        self.assertEqual(a,authorization_record())

if __name__=="__main__": unittest.main()
