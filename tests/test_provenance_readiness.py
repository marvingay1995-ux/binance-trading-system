import copy
import hashlib
import json
import unittest

from btc_engine.provenance_readiness import (
    CAPABILITIES, REQUIRED_EVIDENCE, assessment_report, require_verifier_authorization
)
from btc_engine.spec_amendment import canonical_bytes


class ProvenanceReadinessTests(unittest.TestCase):
    def test_all_required_checks_outstanding(self):
        r=assessment_report()
        self.assertEqual(len(REQUIRED_EVIDENCE), 12)
        self.assertEqual(set(r["not_satisfied"]),set(REQUIRED_EVIDENCE))
        self.assertTrue(all(v["status"] != "VERIFIED" for v in REQUIRED_EVIDENCE.values()))

    def test_no_authenticity_from_manifest(self):
        r=assessment_report()
        self.assertFalse(r["manifest_shape_is_authenticity_proof"])
        self.assertFalse(r["hash_format_is_content_verification"])
        self.assertFalse(r["source_url_is_provider_authentication"])

    def test_all_authorization_flags_false(self):
        r=assessment_report()
        self.assertFalse(r["file_verifier_implementation_authorized"])
        self.assertFalse(r["h01_backtesting_authorized"])
        self.assertFalse(r["paper_trading_authorized"])
        self.assertFalse(r["live_trading_authorized"])
        self.assertFalse(any(CAPABILITIES.values()))

    def test_stable_sha(self):
        r=assessment_report()
        self.assertEqual(r["reviewed_spec_sha256"],hashlib.sha256(canonical_bytes()).hexdigest())

    def test_registered_boundaries(self):
        r=assessment_report()["data_scope"]
        self.assertEqual(r["warmup_candles"],1200)
        self.assertEqual(r["warmup_start"],"2026-05-15T00:00:00Z")
        self.assertEqual(r["prospective_start"],r["warmup_end_exclusive"])

    def test_negative_controls_registered(self):
        proof=REQUIRED_EVIDENCE["EVID-11"]["proof"]
        self.assertIn("mismatched hashes",proof)
        self.assertIn("fail closed",proof)

    def test_explicit_denial(self):
        with self.assertRaises(PermissionError):
            require_verifier_authorization()

    def test_no_mutation_and_finite_json(self):
        saved=copy.deepcopy(REQUIRED_EVIDENCE)
        report=assessment_report()
        json.dumps(report,allow_nan=False)
        self.assertEqual(saved,REQUIRED_EVIDENCE)


if __name__=="__main__":
    unittest.main()
