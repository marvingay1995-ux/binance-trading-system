import hashlib
import json
import unittest

from btc_engine.offline_verifier_readiness import (
    BLOCKERS, CONDITIONS, DENIALS, readiness_record, require_offline_verifier_implementation,
)
from btc_engine.verifier_implementation_decision import decision_record

class OfflineVerifierReadinessTests(unittest.TestCase):
    def test_no_go_and_baseline(self):
        r = readiness_record()
        self.assertEqual(r["decision"], "NO_GO_OFFLINE_VERIFIER_IMPLEMENTATION")
        self.assertEqual(r["reviewed_main_sha"], "da139ff65d447d804359a7c1c82ebdb2e6fb0efe")
        self.assertEqual(r["reviewed_btc038_branch_sha"], "2d32328b96a43fda9d336dd70b7533c2b142acc9")

    def test_all_permissions_denied(self):
        self.assertFalse(any(DENIALS.values()))
        with self.assertRaises(PermissionError):
            require_offline_verifier_implementation()

    def test_precise_dependency(self):
        e = readiness_record()["evidence"]
        self.assertFalse(e["btc037_pr26_main_merged"])
        self.assertTrue(e["btc038_pr27_merged_to_btc037_branch"])
        self.assertEqual(e["btc038_branch_ci_tests_passed"], 225)

    def test_synthetic_evidence_not_production_security(self):
        e = readiness_record()["evidence"]
        self.assertEqual(e["btc037_materialized_synthetic_scenarios"], 12)
        self.assertEqual(e["btc038_bounded_probe_scenarios"], 6)
        self.assertFalse(e["tested_against_real_verifier"])
        self.assertFalse(e["data_source_authenticity_verified"])

    def test_unresolved_conditions(self):
        self.assertEqual(len(BLOCKERS), 6)
        self.assertEqual(len(CONDITIONS), 5)

    def test_btc028_no_go_retained(self):
        self.assertEqual(decision_record()["decision"], "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")

    def test_json_deterministic(self):
        a = readiness_record()
        self.assertEqual(json.loads(json.dumps(a, allow_nan=False)), a)
        self.assertEqual(a, readiness_record())

if __name__ == "__main__":
    unittest.main()
