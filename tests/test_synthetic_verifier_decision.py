import json
import unittest

from btc_engine.synthetic_verifier_decision import (
    BASELINE_SHA, EXCLUSIONS, FILES_AFTER_SEPARATE_APPROVAL,
    MISSING_EVIDENCE, PERMISSIONS, decision_record, require_implementation,
)


class SyntheticVerifierDecisionTests(unittest.TestCase):
    def test_exact_baseline_and_files(self):
        record = decision_record()
        self.assertEqual(record["reviewed_main_commit"], BASELINE_SHA)
        self.assertEqual(record["proposed_files"], list(FILES_AFTER_SEPARATE_APPROVAL))

    def test_permissions_fail_closed(self):
        self.assertFalse(any(PERMISSIONS.values()))
        self.assertFalse(any(MISSING_EVIDENCE.values()))
        with self.assertRaises(PermissionError):
            require_implementation()

    def test_no_real_market_or_trading(self):
        exclusions = " ".join(EXCLUSIONS).lower()
        for term in ("real exchange", "binance api", "h01", "automated orders"):
            self.assertIn(term, exclusions)

    def test_json_deterministic(self):
        record = decision_record()
        self.assertEqual(record, json.loads(json.dumps(record, allow_nan=False)))
        self.assertEqual(record, decision_record())


if __name__ == "__main__":
    unittest.main()
