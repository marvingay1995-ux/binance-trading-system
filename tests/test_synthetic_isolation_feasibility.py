import json
import unittest

from btc_engine.synthetic_isolation_feasibility import (
    FEASIBILITY, PERMISSIONS, RESTRICTED, decision_record, require_market_data_or_trading,
)

class BTC054IsolationFeasibilityReviewTests(unittest.TestCase):
    def test_live_main_and_branch_ci_distinguished(self):
        record = decision_record()
        evidence = record["integrated_evidence"]
        self.assertEqual(evidence["main_tests_passed"], 305)
        self.assertEqual(evidence["feature_tests_passed"], 318)
        self.assertFalse(evidence["btc052_053_on_main_at_review"])
        self.assertEqual(evidence["integration_pr"], 43)

    def test_cannot_claim_actual_network_isolation(self):
        self.assertTrue(FEASIBILITY)
        self.assertFalse(any(item["verified_os_network_denial"] for item in FEASIBILITY.values()))
        self.assertEqual(FEASIBILITY["rootless_container_no_network"]["classification"], "CANDIDATE_NOT_IMPLEMENTED")

    def test_no_trading_and_real_files(self):
        self.assertTrue(PERMISSIONS["synthetic_only_test_research"])
        self.assertFalse(any(PERMISSIONS[k] for k in RESTRICTED))
        self.assertIn("REAL_DATA_NO_GO", decision_record()["decision"])
        with self.assertRaises(PermissionError):
            require_market_data_or_trading()

    def test_known_existing_runtime_limits_are_not_confused_with_network_sandbox(self):
        self.assertFalse(FEASIBILITY["existing_linux_rlimits"]["verified_os_network_denial"])
        self.assertEqual(FEASIBILITY["existing_python_instrumentation"]["classification"], "TEST_INSTRUMENTATION_ONLY")

    def test_serialization_and_repeatability(self):
        record = decision_record()
        self.assertEqual(json.loads(json.dumps(record, allow_nan=False)), record)
        self.assertEqual(decision_record(), record)

if __name__ == "__main__":
    unittest.main()
