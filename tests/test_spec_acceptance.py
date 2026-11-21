import copy
import hashlib
import json
import unittest

from btc_engine.spec_acceptance import (
    review_report, DESIGN_FINDINGS, AUTHORIZATION_CHECKS, require_offline_authorization,
)
from btc_engine.spec_amendment import AMENDMENT, canonical_bytes


class SpecificationAcceptanceTests(unittest.TestCase):
    def test_review_covers_eight_btc021_findings(self):
        self.assertEqual(set(DESIGN_FINDINGS), {
            "DATA-002","SIGNAL-001","SIZE-001","COMP-001",
            "RISK-002","EXEC-001","EVAL-001","AUTH-001",
        })

    def test_default_denies_all_execution(self):
        r = review_report()
        self.assertEqual(r["readiness_gate"], "BLOCKED")
        for flag in ("offline_research_implementation_authorized",
                     "offline_research_backtest_authorized",
                     "paper_trading_authorized","live_trading_authorized",
                     "may_auto_approve"):
            self.assertIs(r[flag], False)

    def test_no_independent_signoff_claim(self):
        r = review_report()
        self.assertFalse(r["evidence_checks"]["human_reviewer_signoff"])
        self.assertIn("human_reviewer_signoff",r["unmet_required_checks"])
        self.assertIn("INTERNAL",r["review_type"])

    def test_spec_fingerprint_is_stable(self):
        self.assertEqual(review_report()["source_spec_sha256"],
                         hashlib.sha256(canonical_bytes()).hexdigest())

    def test_mutated_spec_refused(self):
        altered=copy.deepcopy(AMENDMENT)
        altered["permissions"]["live_trading"]=True
        with self.assertRaises(ValueError):
            review_report(altered)

    def test_fabricated_approval_refused(self):
        altered=copy.deepcopy(AUTHORIZATION_CHECKS)
        altered["human_reviewer_signoff"]=True
        with self.assertRaises(ValueError):
            review_report(AMENDMENT,altered)

    def test_direct_authorization_refused(self):
        with self.assertRaises(PermissionError):
            require_offline_authorization()

    def test_no_change_to_source(self):
        snapshot=copy.deepcopy(AMENDMENT)
        review_report()
        self.assertEqual(snapshot,AMENDMENT)
        self.assertEqual(json.loads(json.dumps(review_report()))["program"],"BTC-023")


if __name__=="__main__":
    unittest.main()
