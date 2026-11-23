"""BTC-066 URL scope, authority and fail-closed security regression checks."""
import json
import unittest
from unittest.mock import patch
from btc_engine.readonly_https_approval_gate import (
    HOST, REQUIRED_EVIDENCE, approval_and_security_decision,
    require_public_data_access, validate_proposed_url,
)

class BTC066ApprovalAndHttpsTests(unittest.TestCase):
    def test_valid_offline_examples_for_1h_4h_only(self):
        r=approval_and_security_decision()
        self.assertEqual(r["example_urls_checked_offline"],{"1h":True,"4h":True})
        self.assertEqual(r["request_limit_proposed"],500)
        self.assertEqual(r["max_requests_per_minute_proposed"],1)

    def test_reject_urls_outside_scope(self):
        prefix="https://"+HOST+"/api/v3/klines?"
        denied=(
            "http://"+HOST+"/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=500",
            "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=500",
            "https://"+HOST+".evil.test/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=500",
            prefix+"symbol=ETHUSDT&interval=1h&limit=500",
            prefix+"symbol=BTCUSDT&interval=1m&limit=500",
            prefix+"symbol=BTCUSDT&interval=1h&limit=501",
            prefix+"symbol=BTCUSDT&interval=1h&limit=0",
            prefix+"symbol=BTCUSDT&interval=1h&limit=01",
            prefix+"symbol=BTCUSDT&interval=1h&limit=500&limit=2",
            prefix+"symbol=BTCUSDT&interval=1h&limit=500&apiKey=secret",
            prefix+"symbol=BTCUSDT&interval=1h&limit=500#fragment",
            "https://user:pass@"+HOST+"/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=500",
            "https://"+HOST+":443/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=500",
            prefix+"symbol=BTCUSDT&interval=1h&limit=500\n",
        )
        for url in denied:
            with self.subTest(url=url):
                self.assertFalse(validate_proposed_url(url))

    def test_missing_review_blocks_authorization(self):
        d=approval_and_security_decision()
        self.assertTrue(all(v=="MISSING_OR_NOT_INDEPENDENTLY_VERIFIED"
                            for v in d["required_approved_evidence"].values()))
        self.assertEqual(set(d["required_approved_evidence"]),set(REQUIRED_EVIDENCE))
        self.assertFalse(d["owner_authorization_verified"])
        self.assertFalse(d["independent_security_review_verified"])

    def test_fake_owner_and_security_claims_do_not_authorize(self):
        d=approval_and_security_decision(owner_claim={"approved":True},
                                         review_claim={"passed":True})
        self.assertTrue(d["owner_claim_supplied_but_not_authenticated"])
        self.assertTrue(d["security_claim_supplied_but_not_authenticated"])
        self.assertFalse(any(d["permissions"].values()))
        with self.assertRaises(PermissionError):
            require_public_data_access(approved=True)

    def test_all_permissions_remain_closed(self):
        d=approval_and_security_decision()
        self.assertEqual(d["decision"],"R1_APPROVAL_AND_HTTPS_SECURITY_GATE_PENDING_NO_GO")
        self.assertFalse(any(d["permissions"].values()))
        self.assertFalse(d["future_https_client_implemented"])
        self.assertFalse(d["publisher_authenticity_verified"])

    def test_no_network_process_or_io(self):
        with patch("socket.socket",side_effect=AssertionError("network")), \
             patch("subprocess.run",side_effect=AssertionError("process")):
            self.assertFalse(approval_and_security_decision()["permissions"]["http_calls"])

    def test_invalid_claims_rejected(self):
        with self.assertRaises(ValueError): approval_and_security_decision(owner_claim=True)
        with self.assertRaises(ValueError): approval_and_security_decision(review_claim="passed")

    def test_changed_historical_authority_rejected(self):
        from btc_engine.verifier_implementation_decision import decision_record
        record=decision_record()
        record["permissions"]["live_trading"]=True
        with patch("btc_engine.readonly_https_approval_gate.historic",return_value=record):
            with self.assertRaisesRegex(PermissionError,"BTC028_REVIEW_CHANGED"):
                approval_and_security_decision()

    def test_changed_r1_authority_rejected(self):
        from btc_engine.readonly_btcusdt_data_scope import scope_proposal
        record=scope_proposal()
        record["network_fetch_authorized"]=True
        with patch("btc_engine.readonly_https_approval_gate.scope_proposal",return_value=record):
            with self.assertRaisesRegex(PermissionError,"BTC065_AUTHORITY_CHANGED"):
                approval_and_security_decision()

    def test_json_stable_report_and_main_baseline(self):
        a=approval_and_security_decision()
        self.assertEqual(a,json.loads(json.dumps(a,allow_nan=False)))
        self.assertEqual(a,approval_and_security_decision())
        self.assertEqual(a["reviewed_main_tests"],424)

if __name__=="__main__":
    unittest.main()
