import json
import unittest
from btc_engine.synthetic_isolation_strategy import (
    CANDIDATES, PERMISSIONS, REQUIRED_CONTROLS, OBSERVED,
    choose_environment, require_verified_isolation_or_real_data,
)

class BTC057IsolationStrategyTests(unittest.TestCase):
    def test_actual_host_denial_not_recast_as_success(self):
        result = choose_environment()
        self.assertEqual(result["observed_runner"]["btc056_reason"], "UNPRIVILEGED_NAMESPACE_DENIED")
        self.assertEqual(result["decision"], "NO_GO_OS_ISOLATION_ENFORCEMENT_CURRENT_RUNNER")
        self.assertIsNone(result["environment_selected"])
        self.assertFalse(result["verified_full_isolation"])

    def test_containers_and_vms_not_claimed_provisioned(self):
        self.assertTrue(all(v["feasibility"].endswith("UNVERIFIED") or v["feasibility"] == "REJECT_FOR_NEXT_PROOF"
                            for v in CANDIDATES.values()))
        self.assertFalse(PERMISSIONS["container_or_vm_provisioning"])

    def test_fake_positive_evidence_does_not_override_gate(self):
        record = choose_environment({"os_network_isolation_verified":True, "trading_authorized":True})
        self.assertFalse(record["real_data_authorized"])
        self.assertFalse(record["trading_authorized"])
        self.assertFalse(record["verified_full_isolation"])
        self.assertTrue(record["additional_evidence_supplied_but_not_authenticated"])

    def test_controls_cover_network_fs_process_resources(self):
        whole = " ".join(REQUIRED_CONTROLS).lower()
        for term in ("ipv6", "read-only", "non-root", "cpu", "descendant", "collision"):
            self.assertIn(term, whole)

    def test_no_scope_expansion(self):
        for key in ("real_data_ingestion","os_sandbox_declared_secure",
                    "privileged_runner_changes","h01_research_or_backtest","trading_orders"):
            self.assertFalse(PERMISSIONS[key])
        with self.assertRaises(PermissionError):
            require_verified_isolation_or_real_data()

    def test_stable_serializable_evidence(self):
        self.assertEqual(json.loads(json.dumps(choose_environment(), allow_nan=False)), choose_environment())
        self.assertEqual(choose_environment()["merged_main_tests"],342)

    def test_invalid_evidence_rejected(self):
        with self.assertRaises(ValueError):
            choose_environment("simulated evidence")

if __name__ == "__main__":
    unittest.main()
