import hashlib
import json
import unittest

from btc_engine.verifier_implementation_decision import (
    REQUIRED_APPROVAL_EVIDENCE, decision_record, require_verifier_implementation,
)
from btc_engine.verifier_threat_contract import contract_report
from btc_engine.spec_amendment import canonical_bytes


class LocalVerifierDecisionTests(unittest.TestCase):
    def test_no_go_without_evidence(self):
        r=decision_record()
        self.assertEqual(r["decision"],"NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")
        self.assertIn("product_owner_explicit_scope_approval",r["missing_authorization_preconditions"])
        self.assertIn("independent_security_reviewer_signoff",r["missing_authorization_preconditions"])

    def test_permissions_all_false(self):
        r=decision_record()
        self.assertTrue(r["permissions"])
        self.assertFalse(any(r["permissions"].values()))

    def test_review_not_external_audit(self):
        r=decision_record()
        self.assertIn("NOT_EXTERNAL",r["review_classification"])
        self.assertFalse(any(item["status"] == "APPROVED" for item in REQUIRED_APPROVAL_EVIDENCE.values()))

    def test_contract_hash_bound(self):
        r=decision_record()
        self.assertEqual(r["btc027_contract_sha256"],contract_report()["contract_sha256"])
        self.assertEqual(r["h01_v2_spec_sha256"],hashlib.sha256(canonical_bytes()).hexdigest())

    def test_no_strategy_or_network_scope(self):
        outside=" ".join(decision_record()["future_scope"]["always_outside_this_decision"]).lower()
        for key in ("binance api","backtesting","paper trading","live spot orders"):
            self.assertIn(key,outside)

    def test_fails_closed(self):
        with self.assertRaises(PermissionError):
            require_verifier_implementation()

    def test_deterministic_and_serializable(self):
        a=decision_record()
        self.assertEqual(a,decision_record())
        self.assertEqual(json.loads(json.dumps(a,allow_nan=False))["program"],"BTC-028-v1")


if __name__=="__main__":
    unittest.main()
