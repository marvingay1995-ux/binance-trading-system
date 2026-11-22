import copy
import hashlib
import json
import unittest

from btc_engine.security_contract_acceptance import (
    FINDINGS, PERMISSIONS, PROPOSED_SYNTHETIC_SCOPE, REVIEW_SHA,
    acceptance_report, require_synthetic_fixture_authorization,
)
from btc_engine.verifier_security_v2 import remediation_report
from btc_engine.spec_amendment import canonical_bytes


class SecurityContractAcceptanceTests(unittest.TestCase):
    def test_version_and_commit(self):
        r=acceptance_report()
        self.assertEqual(r["program"],"BTC-033-v1")
        self.assertEqual(r["reviewed_main_commit"],REVIEW_SHA)

    def test_accept_design_only(self):
        r=acceptance_report()
        self.assertTrue(r["permissions"]["security_contract_design_accepted_for_further_review"])
        self.assertFalse(any(v for k,v in r["permissions"].items()
                             if k != "security_contract_design_accepted_for_further_review"))

    def test_unresolved_requirements(self):
        self.assertEqual(set(FINDINGS),{f"ACPT-{i:02d}" for i in range(1,6)})
        self.assertTrue(all(x["severity"]=="BLOCKER" for x in FINDINGS.values()))

    def test_scope_excludes_real_data_and_trading(self):
        text=" ".join(PROPOSED_SYNTHETIC_SCOPE["prohibited"]).lower()
        for term in ("market candles","h01 sma","binance api","real"):
            self.assertIn(term,text)

    def test_explicit_signoff_still_missing(self):
        r=acceptance_report()
        self.assertFalse(r["external_review_evidence_present"])
        self.assertFalse(r["synthetic_test_files_created"])
        self.assertFalse(r["synthetic_fixture_tests_executed"])
        self.assertFalse(r["actual_file_verifier_implemented"])

    def test_fail_closed_guard(self):
        with self.assertRaises(PermissionError):
            require_synthetic_fixture_authorization()

    def test_report_hash_grounded(self):
        r=acceptance_report()
        old=remediation_report()
        expected=hashlib.sha256(json.dumps(old,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")).hexdigest()
        self.assertEqual(r["reviewed_btc032_report_sha256"],expected)
        self.assertEqual(r["h01_v2_spec_sha256"],hashlib.sha256(canonical_bytes()).hexdigest())

    def test_no_contract_mutation(self):
        snapshot=copy.deepcopy(remediation_report())
        acceptance_report()
        self.assertEqual(snapshot,remediation_report())

    def test_json_stable(self):
        r=acceptance_report()
        self.assertEqual(json.loads(json.dumps(r,allow_nan=False)),r)


if __name__=="__main__":
    unittest.main()
