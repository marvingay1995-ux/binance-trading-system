import json
import unittest
from btc_engine.hypotheses import (
    RESEARCH_HYPOTHESES, REQUIRED_FOR_TESTING,
    registry_report, require_research_execution,
)


class HypothesisRegistryTests(unittest.TestCase):
    def test_registered_hypotheses(self):
        self.assertEqual(set(RESEARCH_HYPOTHESES), {"H01_TREND_CONDITION","H02_VOLATILITY_CONTROL"})

    def test_concepts_not_parameterized(self):
        for item in RESEARCH_HYPOTHESES.values():
            self.assertEqual(item["status"], "CONCEPT_ONLY_NOT_PARAMETERIZED")
            self.assertIsNone(item["entry_rule"])
            self.assertIsNone(item["exit_rule"])
            self.assertIsNone(item["parameters"])
            self.assertFalse(item["execution_code_authorized"])

    def test_no_promotions(self):
        r = registry_report()
        self.assertFalse(r["paper_authorized"])
        self.assertFalse(r["live_authorized"])
        self.assertEqual(r["default_decision"], "DO_NOT_TEST_OR_PROMOTE")

    def test_old_data_is_viewed(self):
        r = registry_report()
        self.assertEqual(r["earlier_data"], "ALREADY_EXAMINED_NOT_ELIGIBLE_AS_FRESH_HOLDOUT")
        self.assertEqual(len(r["retired_sma_baselines"]),2)

    def test_execution_rejected_for_known(self):
        for identifier in RESEARCH_HYPOTHESES:
            with self.assertRaises(PermissionError):
                require_research_execution(identifier)

    def test_execution_rejected_for_unknown(self):
        with self.assertRaises(ValueError):
            require_research_execution("arbitrary_idea")

    def test_require_independent_review(self):
        self.assertIn("independent_review_approval", REQUIRED_FOR_TESTING)
        self.assertIn("leakage_checks", REQUIRED_FOR_TESTING)

    def test_valid_json(self):
        self.assertEqual(json.loads(json.dumps(registry_report()))["program"],"BTC-019-v1")


if __name__ == "__main__":
    unittest.main()
