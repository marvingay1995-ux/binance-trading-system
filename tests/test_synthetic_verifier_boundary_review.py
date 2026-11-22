import json
import unittest

from btc_engine.synthetic_verifier_boundary_review import (
    BASELINE_SHA, PERMISSIONS, REVIEW_FINDINGS, review_record,
    require_real_data_verification,
)

class BTC046BoundaryReviewTests(unittest.TestCase):
    def test_baseline_and_reconciled_tests(self):
        r = review_record()
        self.assertEqual(r["reviewed_main_commit"], BASELINE_SHA)
        self.assertEqual(r["main_tests_passed"], 262)
        self.assertEqual(r["ci_run_id"], 45036068026)

    def test_real_data_no_go(self):
        self.assertEqual(review_record()["decision"], "SYNTHETIC_ONLY_EVIDENCE_ACCEPTED_REAL_DATA_BOUNDARY_NO_GO")
        self.assertTrue(PERMISSIONS["synthetic_only_fixture_verification"])
        self.assertFalse(any(v for k,v in PERMISSIONS.items() if k != "synthetic_only_fixture_verification"))
        with self.assertRaises(PermissionError):
            require_real_data_verification()

    def test_evidence_is_precisely_limited(self):
        tested = review_record()["tested"]
        self.assertTrue(tested["public_entrypoint_tamper_refusals"])
        self.assertTrue(tested["direct_csv_zip_parser_negative_tests"])
        self.assertFalse(tested["production_limits_or_os_sandbox"])
        self.assertFalse(tested["arbitrary_or_real_exchange_candle_files"])

    def test_review_findings_complete(self):
        self.assertEqual(set(REVIEW_FINDINGS), {f"B46-{i:02d}" for i in range(1,7)})
        self.assertTrue(all(x["status"].startswith("OPEN") for x in REVIEW_FINDINGS.values()))

    def test_json_serializable_and_repeatable(self):
        a = review_record()
        self.assertEqual(json.loads(json.dumps(a, allow_nan=False)), a)
        self.assertEqual(a, review_record())

if __name__ == "__main__":
    unittest.main()
