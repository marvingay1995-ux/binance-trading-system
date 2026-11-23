import json
import unittest
from unittest.mock import patch
from btc_engine.readonly_r1_owner_security_decision import (
    NO_GO, OWNER_DECISION_FIELDS, REVIEW_CHECKS, SCOPE, decision_record, require_r1_fetch,
)

class BTC067OwnerSecurityDecisionTests(unittest.TestCase):
    def test_actual_decision_no_go(self):
        r=decision_record()
        self.assertEqual(r["decision"],NO_GO)
        self.assertEqual(r["owner_decision"],"NOT_RECORDED")
        self.assertEqual(r["independent_reviewer"],"NOT_IDENTIFIED")

    def test_research_scope_narrow(self):
        scope=decision_record()["scope"]
        self.assertEqual(scope["asset"],"BTCUSDT")
        self.assertEqual(scope["intervals"],["1h","4h"])
        self.assertEqual(scope["source"],"https://data-api.binance.vision")
        self.assertEqual(scope["method"],"GET")
        self.assertFalse(scope["account_keys_permitted"])

    def test_missing_owner_and_reviewer_evidence_reported(self):
        r=decision_record()
        self.assertEqual(set(r["owner_evidence_fields"]),set(OWNER_DECISION_FIELDS))
        self.assertEqual(set(r["security_review_findings"]),set(REVIEW_CHECKS))
        self.assertTrue(all(v=="NOT_EVIDENCED" for v in r["owner_evidence_fields"].values()))
        self.assertTrue(all(v=="NOT_EVIDENCED" for v in r["security_review_findings"].values()))

    def test_fake_owner_claim_cannot_be_approval(self):
        r=decision_record(owner_evidence={"approval":True,"date":"2026-11-23"})
        self.assertTrue(r["owner_claim_present_but_not_verified"])
        self.assertFalse(r["owner_authorization_verified"])
        self.assertFalse(r["public_fetch_authorized"])

    def test_fake_security_certificate_cannot_be_signoff(self):
        r=decision_record(security_evidence={"signed_off":True,"reviewer":"self"})
        self.assertTrue(r["security_claim_present_but_not_verified"])
        self.assertFalse(r["independent_security_review_verified"])
        self.assertFalse(r["https_client_implementation_authorized"])

    def test_no_operational_permissions(self):
        r=decision_record()
        for key in ("public_fetch_authorized", "https_client_implementation_authorized",
                    "authentic_market_data_ingestion_authorized", "h01_backtesting_authorized",
                    "paper_trading_authorized", "live_spot_trading_authorized",
                    "binance_credentials_authorized", "orders_authorized",
                    "docker_execution_authorized"):
            self.assertFalse(r[key])

    def test_no_process_or_network(self):
        with patch("socket.socket",side_effect=AssertionError("network")), \
             patch("subprocess.run",side_effect=AssertionError("process")):
            self.assertFalse(decision_record()["public_fetch_authorized"])

    def test_bad_claim_types_rejected(self):
        for claim in (True,"yes",[],42):
            with self.subTest(claim=claim):
                with self.assertRaises(ValueError): decision_record(owner_evidence=claim)
                with self.assertRaises(ValueError): decision_record(security_evidence=claim)

    def test_no_bypass_from_arguments(self):
        with self.assertRaisesRegex(PermissionError,"BTC067_PUBLIC_DATA_FETCH_NO_GO"):
            require_r1_fetch(approved=True,independently_reviewed=True)

    def test_prior_gate_mutation_detected(self):
        from btc_engine.readonly_https_approval_gate import approval_and_security_decision
        prior=approval_and_security_decision()
        prior["permissions"]["http_calls"]=True
        with patch("btc_engine.readonly_r1_owner_security_decision.approval_and_security_decision",return_value=prior):
            with self.assertRaisesRegex(PermissionError,"PRIOR_PUBLIC_DATA_DENIAL_CHANGED"):
                decision_record()

    def test_stable_serialization_and_ci_baseline(self):
        r=decision_record()
        self.assertEqual(json.loads(json.dumps(r,allow_nan=False)),r)
        self.assertEqual(decision_record(),r)
        self.assertEqual(r["baseline_ci_tests"],434)

if __name__=="__main__": unittest.main()
