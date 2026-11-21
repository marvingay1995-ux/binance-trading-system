import copy
import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone

from btc_engine.spec_amendment import AMENDMENT, audit_amendment, canonical_bytes
from btc_engine.trend_registration import PROTOCOL


class SpecAmendmentTests(unittest.TestCase):
    def test_declared_spec_no_permissions(self):
        report = audit_amendment()
        self.assertFalse(any(report["permissions"].values()))
        self.assertEqual(report["audit_decision"], "REVIEW_REQUIRED_NO_SIMULATION_OR_TRADING")

    def test_1200_four_hour_bars_exact_dates(self):
        p = AMENDMENT["provenance"]
        first = datetime.fromisoformat(p["initial_warmup_first_open_utc"].replace("Z","+00:00"))
        start = datetime.fromisoformat(p["first_eligible_evaluation_open_utc"].replace("Z","+00:00"))
        last = datetime.fromisoformat(p["last_warmup_open_utc"].replace("Z","+00:00"))
        self.assertEqual(start-first,timedelta(hours=1200*4))
        self.assertEqual(start-last,timedelta(hours=4))

    def test_completed_bar_index_invariant(self):
        s = AMENDMENT["bar_index_contract"]
        self.assertIn("closes[i-1200:i]", s["sma_1200"])
        self.assertIn("closes[i-1]", s["latest_completed_close"])
        self.assertIn("close[i]",s["same_bar_ordering"])
        self.assertTrue(s["one_decision_per_bar"])

    def test_passive_comparator_definitions(self):
        c = AMENDMENT["passive_comparator"]
        self.assertEqual(c["rebalancing"],"NONE")
        self.assertIn("fee-inclusive",c["allocation"])
        self.assertIn("liquidate",c["terminal_comparison"])

    def test_risk_ceiling_not_promised(self):
        r = AMENDMENT["risk_design"]
        self.assertFalse(r["risk_ceiling_is_guaranteed"])
        self.assertFalse(r["paper_or_live_risk_engine_ready"])

    def test_no_mutation_of_original(self):
        self.assertEqual(PROTOCOL["trend"]["lookback_complete_bars"],1200)
        self.assertEqual(PROTOCOL["position"]["target_exposure_fraction_of_current_equity"],.20)
        self.assertEqual(PROTOCOL["controls"]["research_backtest_authorized"],False)

    def test_mutated_contract_rejected(self):
        s = copy.deepcopy(AMENDMENT)
        s["permissions"]["paper_trading"] = True
        with self.assertRaises(ValueError):
            audit_amendment(s)

    def test_mutated_strategy_rejected(self):
        s = copy.deepcopy(AMENDMENT)
        s["immutable_h01_parameters"]["lookback_completed_bars"] = 100
        with self.assertRaises(ValueError):
            audit_amendment(s)

    def test_hash_reproducible(self):
        self.assertEqual(audit_amendment()["specification_hash_sha256"],hashlib.sha256(canonical_bytes()).hexdigest())
        json.dumps(AMENDMENT,allow_nan=False)


if __name__ == "__main__":
    unittest.main()
