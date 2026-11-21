import copy
import hashlib
import json
import unittest

from btc_engine.trend_registration import (
    PROTOCOL, canonical_bytes, specification_report, validate_registration
)


class TrendSpecificationTests(unittest.TestCase):
    def test_research_only_contract(self):
        self.assertTrue(validate_registration(PROTOCOL))
        self.assertFalse(PROTOCOL["controls"]["new_signal_implementation_allowed"])
        self.assertFalse(PROTOCOL["controls"]["research_backtest_authorized"])
        self.assertFalse(PROTOCOL["controls"]["paper_trading_authorized"])
        self.assertFalse(PROTOCOL["controls"]["live_trading_authorized"])

    def test_200_day_warmup(self):
        self.assertEqual(PROTOCOL["trend"]["lookback_complete_bars"], 200*6)
        self.assertEqual(PROTOCOL["trend"]["signal_observation"], "LATEST_COMPLETED_4H_BAR_ONLY")

    def test_no_lookahead_in_rule_text(self):
        self.assertIn("next bar open", PROTOCOL["trend"]["entry"])
        self.assertIn("next bar open", PROTOCOL["trend"]["exit"])

    def test_position_risk_design(self):
        self.assertLessEqual(PROTOCOL["position"]["target_exposure_fraction_of_current_equity"],
                             PROTOCOL["position"]["maximum_exposure_fraction"])
        self.assertLessEqual(PROTOCOL["position"]["maximum_exposure_fraction"], .30)

    def test_cost_stress_and_comparators(self):
        self.assertEqual(PROTOCOL["research_execution_assumptions"]["stress_multipliers"], [1,2,3])
        self.assertEqual(len(PROTOCOL["evaluation"]["comparators"]), 2)

    def test_reject_spec_mutation(self):
        changed = copy.deepcopy(PROTOCOL)
        changed["trend"]["lookback_complete_bars"] = 300
        with self.assertRaises(ValueError):
            validate_registration(changed)

    def test_reject_backtest_authorization(self):
        changed = copy.deepcopy(PROTOCOL)
        changed["controls"]["research_backtest_authorized"] = True
        with self.assertRaises(ValueError):
            validate_registration(changed)

    def test_hash_stable(self):
        r = specification_report()
        self.assertEqual(r["canonical_sha256"],hashlib.sha256(canonical_bytes()).hexdigest())
        self.assertEqual(json.loads(json.dumps(r))["decision"],"REVIEW_ONLY_DO_NOT_SIMULATE_OR_TRADE")


if __name__ == "__main__":
    unittest.main()
