import copy
import hashlib
import json
import unittest

from btc_engine.verifier_authorization_review import (
    PROPOSED_BOUNDARY, AUTHORIZATION_EVIDENCE,
    review_decision, require_local_verifier_implementation_authorization,
)
from btc_engine.spec_amendment import canonical_bytes


class VerifierAuthorizationReviewTests(unittest.TestCase):
    def test_local_only_scope(self):
        scope=PROPOSED_BOUNDARY["implementation_limits"]
        self.assertTrue(scope["local_files_only"])
        self.assertTrue(scope["no_network"])
        self.assertTrue(scope["no_exchange"])
        self.assertTrue(scope["no_simulator_or_trade_logic"])

    def test_no_implementation_permission(self):
        r=review_decision()
        self.assertFalse(r["implementation_authorized"])
        self.assertFalse(r["data_ingestion_authorized"])
        self.assertIn("NO_GO",r["decision"])

    def test_all_strategy_trade_permissions_denied(self):
        r=review_decision()
        self.assertFalse(r["h01_signals_authorized"])
        self.assertFalse(r["h01_backtesting_authorized"])
        self.assertFalse(r["paper_trading_authorized"])
        self.assertFalse(r["live_trading_authorized"])

    def test_no_approval_fabrication(self):
        self.assertFalse(AUTHORIZATION_EVIDENCE["exact_scoped_change_request_approved_by_product_owner"])
        self.assertFalse(AUTHORIZATION_EVIDENCE["independent_security_review_completed"])
        self.assertIn("independent_security_review_completed",review_decision()["outstanding_preconditions"])

    def test_bad_input_not_promoted(self):
        r=review_decision()
        self.assertIn("blindly trusting manifest hashes", " ".join(r["proposed_scope"]["forbidden_without_new_independent_authorization"]))

    def test_fingerprint(self):
        self.assertEqual(review_decision()["source_spec_sha256"],hashlib.sha256(canonical_bytes()).hexdigest())

    def test_denied_runtime_guard(self):
        with self.assertRaises(PermissionError):
            require_local_verifier_implementation_authorization()

    def test_deterministic_document(self):
        x=copy.deepcopy(PROPOSED_BOUNDARY)
        self.assertEqual(json.loads(json.dumps(review_decision(), allow_nan=False))["program"],"BTC-026")
        self.assertEqual(x,PROPOSED_BOUNDARY)


if __name__=="__main__":
    unittest.main()
