"""BTC-071: invented envelope negative tests. Zero network/authentic data."""
import json
import unittest
from unittest.mock import patch

from btc_engine.r1_offline_http_response import (
    SYNTHETIC_AS_OF_MS, PERIODS, invented_response, review_invented_response,
    security_decision, require_network_or_order
)

class BTC071OfflineHTTPResponseTests(unittest.TestCase):
    def test_exact_1h_4h_envelopes_only(self):
        for i in ("1h","4h"):
            with self.subTest(i=i):
                r=review_invented_response(i)
                self.assertTrue(r["synthetic_only"])
                self.assertEqual(r["candle_count"],3)
                self.assertFalse(r["real_data_verified"])
                self.assertFalse(r["network_or_order_authorized"])

    def test_wrong_status_and_bool_status_denied(self):
        for status in (False,True,201,301,400,500):
            env=invented_response("1h")
            env["status"]=status
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValueError,"SYNTHETIC_HTTP_STATUS_DENIED"):
                    review_invented_response("1h",env)

    def test_content_type_and_length_must_match(self):
        for key,value in (("content-type","text/html"),
                          ("content-type","application/json; charset=utf-8"),
                          ("content-length","99999")):
            env=invented_response("1h")
            env["headers"][key]=value
            with self.subTest(key=key,value=value):
                with self.assertRaises(ValueError):
                    review_invented_response("1h",env)

    def test_reject_unexpected_headers_and_redirects(self):
        for key,value in (("location","https://evil.example"),
                          ("set-cookie","session=a"),
                          ("content-encoding","gzip"),
                          ("authorization","Bearer secret"),
                          ("transfer-encoding","chunked")):
            env=invented_response("4h")
            env["headers"][key]=value
            with self.subTest(key=key):
                with self.assertRaisesRegex(ValueError,"INVALID_SYNTHETIC_HEADERS"):
                    review_invented_response("4h",env)

    def test_body_not_registered_even_with_valid_metadata(self):
        env=invented_response("1h")
        env["body"]=env["body"]+b" "
        env["headers"]["content-length"]=str(len(env["body"]))
        with self.assertRaisesRegex(PermissionError,"UNREGISTERED_BODY_DENIED"):
            review_invented_response("1h",env)

    def test_other_interval_cannot_be_substituted(self):
        env=invented_response("4h")
        with self.assertRaisesRegex(PermissionError,"UNREGISTERED_BODY_DENIED"):
            review_invented_response("1h",env)

    def test_no_arbitrary_json_or_nonbytes(self):
        for body in (b'[]',None,"[]",b'{}',b"0"*9000):
            env=invented_response("1h")
            env["body"]=body
            if isinstance(body,bytes):
                env["headers"]["content-length"]=str(len(body))
            with self.subTest(bodytype=str(type(body)),size=len(body) if isinstance(body,bytes) else -1):
                with self.assertRaises((ValueError, PermissionError)):
                    review_invented_response("1h",env)

    def test_untrusted_clock_not_accepted(self):
        for stamp in (True,0,SYNTHETIC_AS_OF_MS+1,SYNTHETIC_AS_OF_MS*1000):
            with self.subTest(stamp=stamp):
                with self.assertRaisesRegex(ValueError,"UNAPPROVED_SYNTHETIC_CLOCK"):
                    review_invented_response("1h",as_of_ms=stamp)

    def test_malformed_envelope_rejected(self):
        for env in ({},[],{"status":200,"body":b"[]","headers":{},"extra":3}):
            with self.assertRaises(ValueError):
                review_invented_response("1h",env)

    def test_unapproved_interval_rejected(self):
        for interval in ("1m","1d",None):
            with self.assertRaises(ValueError):
                review_invented_response(interval)

    def test_no_network_file_or_process_calls(self):
        with patch("socket.socket",side_effect=AssertionError("socket")), \
             patch("subprocess.run",side_effect=AssertionError("process")), \
             patch("builtins.open",side_effect=AssertionError("file")):
            self.assertFalse(security_decision()["real_market_data_ingestion_authorized"])

    def test_preserve_no_go_and_unsigned_review(self):
        record=security_decision()
        self.assertEqual(record["decision"],"GO_FROZEN_INVENTED_HTTP_ENVELOPE_NEGATIVE_TESTS_ONLY")
        for key in ("independent_security_review_complete","real_http_client_implemented",
                    "tls_dns_redirect_controls_verified","external_json_admission_authorized",
                    "real_market_data_ingestion_authorized","h01_backtesting_authorized",
                    "paper_trading_authorized","live_spot_authorized",
                    "binance_credentials_authorized","order_execution_authorized",
                    "docker_execution_authorized","spend_authorized"):
            self.assertFalse(record[key])
        with self.assertRaises(PermissionError):
            require_network_or_order(approved=True)

    def test_serialization_stability(self):
        record=security_decision()
        self.assertEqual(record,json.loads(json.dumps(record,allow_nan=False)))
        self.assertEqual(record,security_decision())
        self.assertEqual(record["baseline_main_tests"],480)

if __name__=="__main__":
    unittest.main()
