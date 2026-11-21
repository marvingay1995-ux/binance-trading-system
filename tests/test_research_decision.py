import json
import unittest
from btc_engine.research_decision import (
    DECISIONS, SOURCE_RUN, decision_report, require_promotion_authorization,
)


class ResearchDecisionTests(unittest.TestCase):
    def test_evidence_reference(self):
        self.assertEqual(SOURCE_RUN, 44915102425)
        self.assertEqual(len(DECISIONS), 2)

    def test_both_rejected_as_candidates(self):
        for item in DECISIONS.values():
            self.assertTrue(item["benchmark_only"])
            self.assertEqual(item["status"], "RETIRED_FROM_TRADING_CONSIDERATION")

    def test_higher_costs_are_worse(self):
        for item in DECISIONS.values():
            self.assertLess(item["double_cost_holdout_return_pct"], item["holdout_return_pct"])
            self.assertLess(item["triple_cost_holdout_return_pct"], item["double_cost_holdout_return_pct"])

    def test_promotion_denied(self):
        for strategy in DECISIONS:
            for target in ("paper", "live"):
                with self.subTest(strategy=strategy, target=target):
                    with self.assertRaises(PermissionError):
                        require_promotion_authorization(strategy, target)

    def test_unknown_strategy_fails_closed(self):
        with self.assertRaises(ValueError):
            require_promotion_authorization("unregistered_candidate", "live")

    def test_unknown_target_fails_closed(self):
        with self.assertRaises(ValueError):
            require_promotion_authorization("sma_5_20_4h_baseline", "testnet")

    def test_no_authorization_in_report(self):
        report = decision_report()
        self.assertFalse(report["paper_trading_authorized"])
        self.assertFalse(report["live_trading_authorized"])
        self.assertFalse(report["automated_execution_authorized"])
        self.assertEqual(report["qualification_policy"]["prospective_4h_registration"],
                         "COMPARISON_BENCHMARK_ONLY")

    def test_serializable(self):
        report = json.loads(json.dumps(decision_report(), allow_nan=False))
        self.assertEqual(report["program"], "BTC-018")


if __name__ == "__main__":
    unittest.main()
