import hashlib
import json
import unittest

from btc_engine.synthetic_fixture_spec import contract_record
from btc_engine.synthetic_generator_authorization import (
    ALLOWED_ONLY_IF_SEPARATELY_APPROVED, APPROVAL_EVIDENCE, PROHIBITED,
    decision_record, require_synthetic_generator_implementation,
)


class SyntheticGeneratorAuthorizationTests(unittest.TestCase):
    def test_no_approval_fabrication(self):
        r = decision_record()
        self.assertFalse(any(APPROVAL_EVIDENCE.values()))
        self.assertEqual(r["decision"], "SCOPED_REQUEST_PREPARED_IMPLEMENTATION_NOT_AUTHORIZED")

    def test_permissions_fail_closed(self):
        self.assertFalse(any(decision_record()["permissions"].values()))
        with self.assertRaises(PermissionError):
            require_synthetic_generator_implementation()

    def test_no_real_market_or_strategy_scope(self):
        exclusions = " ".join(PROHIBITED).lower()
        for term in ("market data", "binance api", "h01 signals", "live"):
            self.assertIn(term, exclusions)
        self.assertTrue(all("synthetic" in s.lower() or "tests/" in s or "standard library" in s
                            for s in ALLOWED_ONLY_IF_SEPARATELY_APPROVED))

    def test_original_contract_fingerprint(self):
        original = contract_record()
        expected = hashlib.sha256(json.dumps(original, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest()
        self.assertEqual(decision_record()["btc034_contract_sha256"], expected)

    def test_serialization(self):
        x = decision_record()
        self.assertEqual(json.loads(json.dumps(x, allow_nan=False)), x)


if __name__ == "__main__":
    unittest.main()
