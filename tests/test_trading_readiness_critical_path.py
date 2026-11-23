"""BTC-064 critical-path ordering and permission-denial regression tests."""
import json
import unittest
from unittest.mock import patch
from btc_engine.trading_readiness_critical_path import (
    HISTORICAL_STRATEGY, LIMITS, STAGES, critical_path_decision,
    require_market_or_trade_permission,
)

class BTC064CriticalPathTests(unittest.TestCase):
    def test_stage_order_and_authority_remain_closed(self):
        r=critical_path_decision()
        self.assertEqual([s["id"] for s in r["stages"]],["R1","R2","R3","R4"])
        self.assertTrue(all(s["authorized_now"] is False for s in r["stages"]))
        self.assertTrue(r["decision"].startswith("NO_GO"))

    def test_public_data_distinct_from_order_credentials(self):
        r=critical_path_decision()
        self.assertIn("no account or API key",r["stages"][0]["scope"])
        for key in ("public_data_access_authorized","local_real_data_ingestion_authorized",
                    "binance_credentials_authorized","orders_authorized"):
            self.assertFalse(r[key])

    def test_retired_strategy_never_promoted(self):
        r=critical_path_decision()
        self.assertEqual(r["retired_strategy"]["decision"],"RETIRED_BENCHMARK_ONLY")
        self.assertFalse(r["retired_strategy"]["paper_or_live_promotion_allowed"])
        self.assertTrue(r["retired_strategy"]["historical_windows_not_fresh_holdout"])

    def test_risk_policy_is_future_only(self):
        r=critical_path_decision()
        self.assertEqual(LIMITS["proposed_daily_loss_limit_percent"],2)
        self.assertEqual(LIMITS["proposed_max_spot_exposure_percent"],30)
        self.assertEqual(LIMITS["initial_orders_requiring_manual_approval"],20)
        self.assertFalse(r["orders_authorized"])
        self.assertFalse(r["profitability_demonstrated"])

    def test_docker_and_market_scope_independent(self):
        r=critical_path_decision()
        self.assertIn("Docker image provenance audit",r["not_required_before_R1"][0])
        self.assertFalse(r["docker_execution_authorized"])
        self.assertFalse(r["public_data_access_authorized"])

    def test_approval_claims_cannot_bypass(self):
        with self.assertRaisesRegex(PermissionError,"BTC064_MARKET_DATA_AND_TRADING_NO_GO"):
            require_market_or_trade_permission(public_data=True,live_trading=True)

    def test_no_external_network_or_process(self):
        with patch("subprocess.run",side_effect=AssertionError("NO PROCESS")), \
             patch("socket.socket",side_effect=AssertionError("NO NETWORK")):
            self.assertFalse(critical_path_decision()["live_trading_authorized"])

    def test_altered_historic_authority_fails(self):
        from btc_engine.verifier_implementation_decision import decision_record
        forged=decision_record()
        forged["permissions"]["live_trading"]=True
        with patch("btc_engine.trading_readiness_critical_path.btc028",return_value=forged):
            with self.assertRaisesRegex(PermissionError,"BTC028_HISTORIC_NO_GO_CHANGED"):
                critical_path_decision()

    def test_stage_mutation_detected(self):
        bad=tuple([dict(STAGES[0],authorized_now=True),*STAGES[1:]])
        with patch("btc_engine.trading_readiness_critical_path.STAGES",bad):
            with self.assertRaisesRegex(PermissionError,"UNAUTHORIZED_MARKET_STAGE"):
                critical_path_decision()

    def test_serializable_and_repeatable(self):
        a=critical_path_decision()
        self.assertEqual(json.loads(json.dumps(a,allow_nan=False)),a)
        self.assertEqual(a,critical_path_decision())
        self.assertEqual(a["reviewed_main_tests"],404)

if __name__=="__main__":
    unittest.main()
