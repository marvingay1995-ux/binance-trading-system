import json
import unittest

from btc_engine.synthetic_evidence_acceptance import (
    RISKS, RESTRICTED_KEYS, PERMISSIONS, evidence_acceptance_record,
    require_real_data_or_trading,
)


class BTC052SyntheticEvidenceDecisionTests(unittest.TestCase):
    def test_risk_register_preserves_all_eight(self):
        self.assertEqual(set(RISKS), {f"R48-{i:02d}" for i in range(1, 9)})
        self.assertTrue(all(v["status"].startswith("OPEN") for v in RISKS.values()))

    def test_no_real_market_data_or_trading(self):
        record = evidence_acceptance_record()
        self.assertEqual(record["decision"], "CONDITIONAL_ACCEPT_SYNTHETIC_ONLY_EVIDENCE_REAL_DATA_NO_GO")
        self.assertTrue(all(not PERMISSIONS[k] for k in RESTRICTED_KEYS))
        with self.assertRaises(PermissionError):
            require_real_data_or_trading()

    def test_review_explicitly_conditional_on_main_integration(self):
        integration = evidence_acceptance_record()["integration"]
        self.assertFalse(integration["btc051_on_main_at_review"])
        self.assertTrue(integration["requires_merge_and_fresh_main_ci"])
        self.assertEqual(evidence_acceptance_record()["btc051_branch_tests_passed"], 305)

    def test_no_security_certification_claim(self):
        record = evidence_acceptance_record()
        self.assertIn("NOT_INDEPENDENT_SECURITY_CERTIFICATION", record["classification"])
        self.assertTrue(any("OS-enforced" in item for item in record["not_accepted"]))
        self.assertTrue(any("Binance" in item for item in record["not_accepted"]))

    def test_json_deterministic_and_serializable(self):
        record = evidence_acceptance_record()
        self.assertEqual(record, json.loads(json.dumps(record, allow_nan=False)))
        self.assertEqual(record, evidence_acceptance_record())


if __name__ == "__main__":
    unittest.main()
