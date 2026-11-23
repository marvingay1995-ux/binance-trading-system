import json
import unittest
from unittest.mock import patch

from btc_engine.r1_evidence_reconciliation import (
    OWNER_CHOICES, REQUIRED_OWNER_BOUNDARIES, REQUIRED_REVIEW_AREAS,
    reconcile_decision, require_r1_action,
)

class BTC068EvidenceReconciliationTests(unittest.TestCase):
    def test_no_go_for_unrecorded_owner_decision(self):
        r=reconcile_decision()
        self.assertEqual(r["decision"],"NO_GO_PENDING_OWNER_CHOICE_AND_INDEPENDENT_SECURITY_EVIDENCE")
        self.assertIsNone(r["owner_choice_recorded"])
        self.assertEqual(r["authorization_effect"],"NONE")

    def test_narrow_approval_choices_distinguish_offline_from_fetch(self):
        r=reconcile_decision()
        self.assertEqual(r["owner_permitted_choices"],list(OWNER_CHOICES))
        self.assertIn("no_outbound_fetch_in_offline_phase",r["owner_boundaries_for_later_approval"])
        self.assertFalse(r["offline_https_client_implementation_authorized"])
        self.assertFalse(r["public_data_fetch_authorized"])

    def test_missing_independent_reviewer_is_explicit(self):
        r=reconcile_decision()
        self.assertIsNone(r["reviewer_identity"])
        self.assertFalse(r["reviewer_independence_verified"])
        self.assertEqual(set(r["security_required_evidence"]),set(REQUIRED_REVIEW_AREAS))
        self.assertTrue(all(v=="EVIDENCE_NOT_PRESENT" for v in r["security_required_evidence"].values()))

    def test_fake_approval_or_reviewer_claim_does_not_authorize(self):
        r=reconcile_decision(
            owner_submission={"decision":"APPROVE_OFFLINE_IMPLEMENTATION_ONLY"},
            security_submission={"signed":True,"independent":True},
        )
        self.assertTrue(r["owner_claim_supplied_not_authenticated"])
        self.assertTrue(r["security_review_claim_supplied_not_authenticated"])
        self.assertFalse(r["offline_https_client_implementation_authorized"])
        self.assertFalse(r["public_data_fetch_authorized"])

    def test_all_operational_actions_explicitly_denied(self):
        r=reconcile_decision()
        for k in ("offline_https_client_implementation_authorized","public_data_fetch_authorized",
                  "real_data_ingestion_authorized","backtesting_authorized",
                  "paper_trading_authorized","live_trading_authorized",
                  "binance_credentials_authorized","orders_authorized","docker_execution_authorized"):
            self.assertFalse(r[k])

    def test_bad_submission_types_rejected(self):
        for claim in ("yes",True,[],7):
            with self.subTest(claim=claim):
                with self.assertRaises(ValueError): reconcile_decision(owner_submission=claim)
                with self.assertRaises(ValueError): reconcile_decision(security_submission=claim)

    def test_historical_btc028_gate_is_immutable(self):
        from btc_engine.verifier_implementation_decision import decision_record
        x=decision_record()
        self.assertEqual(x["decision"],"NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")
        self.assertFalse(any(x["permissions"].values()))

    def test_forged_prior_authorization_detected(self):
        from btc_engine.readonly_r1_owner_security_decision import decision_record
        x=decision_record()
        x["public_fetch_authorized"]=True
        with patch("btc_engine.r1_evidence_reconciliation.btc067",return_value=x):
            with self.assertRaisesRegex(PermissionError,"BTC067_AUTHORITY_CHANGED"):
                reconcile_decision()

    def test_no_network_or_process(self):
        with patch("socket.socket",side_effect=AssertionError("network")), \
             patch("subprocess.run",side_effect=AssertionError("command")):
            self.assertFalse(reconcile_decision()["public_data_fetch_authorized"])

    def test_arbitrary_claims_rejected_at_action_boundary(self):
        with self.assertRaisesRegex(PermissionError,"BTC068_R1_NO_GO_OWNER_AND_SECURITY_EVIDENCE_PENDING"):
            require_r1_action(owner_approved=True,security_accepted=True)

    def test_record_repeatable_and_json_safe(self):
        x=reconcile_decision()
        self.assertEqual(x,json.loads(json.dumps(x,allow_nan=False)))
        self.assertEqual(x,reconcile_decision())
        self.assertEqual(x["baseline_main_tests"],445)

if __name__=="__main__": unittest.main()
