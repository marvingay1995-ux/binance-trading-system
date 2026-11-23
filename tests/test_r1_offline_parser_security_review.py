"""BTC-070 additional negative controls for frozen invented JSON candles."""
import json
import unittest
from unittest.mock import patch

from btc_engine.r1_offline_synthetic_json import (
    PERIODS, SYNTHETIC_FIXTURES, _validate_json_klines,
    review_frozen_fixture, require_live_fetch_or_order
)
from btc_engine.r1_offline_parser_security_review import (
    OPEN_SECURITY_GAPS, review_record, require_authentic_data_or_trade
)

def payload(interval):
    return json.loads(SYNTHETIC_FIXTURES[interval])

def raw(rows):
    return json.dumps(rows, separators=(",", ":")).encode("ascii")

class BTC070OfflineParserNegativeControls(unittest.TestCase):
    def test_review_bound_to_merged_main_and_scope(self):
        d=review_record()
        self.assertEqual(d["merged_main_ci_tests"],468)
        self.assertEqual(d["reviewed_main_sha"],"ccf23abbc5a33d117c073c88e0e15c935b523458")
        self.assertEqual(d["decision"],"GO_OFFLINE_INVENTED_FIXTURE_TESTING_ONLY")
        self.assertTrue(d["owner_offline_only_approval_recorded"])
        self.assertFalse(d["independent_security_signoff"])

    def test_whitespace_and_modified_bytes_fail_public_gateway(self):
        for interval in PERIODS:
            frozen=SYNTHETIC_FIXTURES[interval]
            for changed in (frozen+b" ", frozen[:-1], b"\n"+frozen):
                with self.subTest(interval=interval,size=len(changed)):
                    with self.assertRaises(PermissionError):
                        review_frozen_fixture(interval,changed)

    def test_wrong_interval_and_fixture_cross_use_fail(self):
        for wrong in ("1m","15m","1d","",None):
            with self.subTest(wrong=wrong):
                with self.assertRaises(ValueError):
                    review_frozen_fixture(wrong)
        with self.assertRaises(PermissionError):
            review_frozen_fixture("4h",SYNTHETIC_FIXTURES["1h"])

    def test_empty_and_five_candle_arrays_rejected(self):
        for rows in ([], payload("1h")+payload("1h")[:2]):
            with self.assertRaises(ValueError):
                _validate_json_klines(raw(rows),"1h")

    def test_bool_timestamps_and_trade_count_rejected(self):
        for index in (0,6,8):
            rows=payload("1h")
            rows[0][index]=True
            with self.subTest(index=index):
                with self.assertRaisesRegex(ValueError,"INVALID_TIME_OR_TRADES"):
                    _validate_json_klines(raw(rows),"1h")

    def test_missing_timestamp_and_unsorted_rejected(self):
        for shift in (PERIODS["4h"],-PERIODS["4h"]):
            rows=payload("4h")
            rows[1][0]+=shift
            rows[1][6]=rows[1][0]+PERIODS["4h"]-1
            with self.subTest(shift=shift):
                with self.assertRaisesRegex(ValueError,"MISSING_DUPLICATED_OR_UNSORTED_CANDLE"):
                    _validate_json_klines(raw(rows),"4h")

    def test_negative_volume_and_taker_excess_rejected(self):
        for i,value,expected in ((5,"-1","INVALID_DECIMAL_FIELD"),
                                 (9,"11","TAKER_VOLUME_EXCEEDS_VOLUME"),
                                 (10,"1001","TAKER_VOLUME_EXCEEDS_VOLUME")):
            rows=payload("1h")
            rows[0][i]=value
            with self.subTest(index=i):
                with self.assertRaisesRegex(ValueError,expected):
                    _validate_json_klines(raw(rows),"1h")

    def test_bad_ignored_field_rejected(self):
        rows=payload("1h")
        rows[0][11]="unexpected"
        with self.assertRaisesRegex(ValueError,"INVALID_IGNORED_FIELD"):
            _validate_json_klines(raw(rows),"1h")

    def test_nan_infinity_and_zero_prices_rejected(self):
        for value,expected in (("inf","INVALID_DECIMAL_FIELD"),
                               ("nan","INVALID_DECIMAL_FIELD"),
                               ("0","NONPOSITIVE_PRICE")):
            rows=payload("4h")
            rows[0][1]=value
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError,expected):
                    _validate_json_klines(raw(rows),"4h")

    def test_open_residuals_are_not_certified(self):
        d=review_record()
        self.assertIn("UTC_FINALITY_VS_WALL_CLOCK_NOT_IMPLEMENTED",OPEN_SECURITY_GAPS)
        self.assertIn("PRECISE_DECIMAL_RULES_NOT_VERIFIED_FOR_AUTHENTIC_EXCHANGE_VALUES",OPEN_SECURITY_GAPS)
        self.assertFalse(d["independent_reviewer_identified"])
        self.assertFalse(d["real_data_ingestion_authorized"])

    def test_no_operations_and_denial_enforced(self):
        with patch("subprocess.run",side_effect=AssertionError("process forbidden")), \
             patch("socket.socket",side_effect=AssertionError("network forbidden")):
            r=review_record()
        for key in ("network_fetch_authorized","external_json_ingestion_authorized",
                    "real_data_ingestion_authorized","h01_backtesting_authorized",
                    "paper_trading_authorized","live_spot_authorized",
                    "orders_authorized","docker_execution_authorized"):
            self.assertFalse(r[key])
        with self.assertRaises(PermissionError):
            require_authentic_data_or_trade(approved=True)
        with self.assertRaises(PermissionError):
            require_live_fetch_or_order(approved=True)

    def test_report_repeatable_json_and_fixture_count(self):
        r=review_record()
        self.assertEqual(r,json.loads(json.dumps(r,allow_nan=False)))
        self.assertEqual(r,review_record())
        self.assertEqual(set(r["frozen_fixture_reports"]),{"1h","4h"})

if __name__=="__main__":
    unittest.main()
