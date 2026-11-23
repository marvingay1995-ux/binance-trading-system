"""BTC-061 explicit fail-closed contract review tests; no runtime calls."""
import json
import unittest
from unittest.mock import patch

from btc_engine.synthetic_docker_readiness_decision import (
    EVIDENCE_GATES, MANDATORY_FLAGS, OBSERVED_GATE_STATUS, PROHIBITED_FLAGS,
    readiness_decision, require_execution_authorization, verify_static_contract,
)

class BTC061DockerReadinessTests(unittest.TestCase):
    def test_static_contract_complete_without_execution_authorization(self):
        result=readiness_decision()
        self.assertTrue(result["verification"]["static_contract_checks_passed"])
        self.assertEqual(result["decision"],"NO_GO_DOCKER_SYNTHETIC_EXECUTION_NOT_READY")
        self.assertTrue(result["static_contract_accepted"])
        self.assertFalse(result["docker_execution_authorized"])

    def test_merged_main_and_branch_evidence_not_conflated(self):
        result=readiness_decision()
        self.assertFalse(result["btc060_on_main_at_review"])
        self.assertEqual(result["snapshot_main_tests"],366)
        self.assertEqual(result["btc060_branch_tests"],374)
        self.assertEqual(result["btc060_branch_ci_run"],45171490604)

    def test_every_unverified_gate_reported_missing(self):
        result=readiness_decision()
        self.assertEqual(set(result["missing_independently_verified_evidence"]),set(EVIDENCE_GATES))
        self.assertEqual(set(result["evidence_gate_status"]),set(EVIDENCE_GATES))
        self.assertFalse(any(OBSERVED_GATE_STATUS.values()))

    def test_flags_incomplete_refused_even_if_contract_claimed(self):
        original=tuple(MANDATORY_FLAGS)
        with patch("btc_engine.synthetic_docker_readiness_decision.REQUIRED_DOCKER_FLAGS",original[:-1]):
            with self.assertRaisesRegex(PermissionError,"BTC060_CONTRACT_INCOMPLETE_OR_UNSAFE"):
                verify_static_contract()

    def test_prohibited_flag_refused(self):
        with patch("btc_engine.synthetic_docker_readiness_decision.REQUIRED_DOCKER_FLAGS",
                   tuple(MANDATORY_FLAGS)+("--privileged",)):
            with self.assertRaisesRegex(PermissionError,"BTC060_CONTRACT_INCOMPLETE_OR_UNSAFE"):
                verify_static_contract()
        self.assertIn("--privileged",PROHIBITED_FLAGS)

    def test_mutated_execution_authority_refused(self):
        from btc_engine.synthetic_docker_isolation_contract import contract_record
        altered=contract_record()
        altered["docker_execution_authorized"]=True
        with patch("btc_engine.synthetic_docker_readiness_decision.contract_record",return_value=altered):
            with self.assertRaisesRegex(PermissionError,"BTC060_CONTRACT_AUTHORITY_CHANGED"):
                verify_static_contract()

    def test_no_container_or_network_activity(self):
        with patch("subprocess.run",side_effect=AssertionError("never execute")), \
             patch("subprocess.Popen",side_effect=AssertionError("never spawn")), \
             patch("socket.socket",side_effect=AssertionError("never create socket")):
            self.assertEqual(readiness_decision()["decision"],"NO_GO_DOCKER_SYNTHETIC_EXECUTION_NOT_READY")

    def test_arbitrary_approval_claims_cannot_override(self):
        for kw in ({},{"approved":True},{"owner_approved":True,"runtime_verified":True}):
            with self.subTest(kw=kw):
                with self.assertRaisesRegex(PermissionError,"BTC061_DOCKER_EXECUTION_NO_GO"):
                    require_execution_authorization(**kw)

    def test_real_data_and_trading_always_denied(self):
        result=readiness_decision()
        for key in ("docker_run_allowed","sandbox_security_certified",
                    "os_network_isolation_verified","real_market_data_authorized",
                    "h01_backtesting_authorized","trading_authorized"):
            self.assertFalse(result[key])

    def test_deterministic_json_report(self):
        result=readiness_decision()
        self.assertEqual(result,json.loads(json.dumps(result,allow_nan=False)))
        self.assertEqual(result,readiness_decision())

if __name__=="__main__":
    unittest.main()
