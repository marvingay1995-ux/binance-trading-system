import copy
import hashlib
import json
import unittest

from btc_engine.verifier_security_v2 import (
    EXPECTED_STATUS, REMEDIATIONS, ERROR_CODES, TEST_CASES, SOURCE_REVIEW_SHA,
    PARENT_CONTRACT_SHA, H01_SPEC_SHA, remediation_report,
)
from btc_engine.spec_amendment import canonical_bytes
from btc_engine.verifier_threat_contract import contract_report


class SecurityRemediationContractTests(unittest.TestCase):
    def test_all_eight_findings_mapped(self):
        self.assertEqual(set(REMEDIATIONS),{f"AI-SEC-{i:02d}" for i in range(1,9)})
        self.assertEqual(sum(1 for v in REMEDIATIONS.values() if v["severity"]=="HIGH"),3)

    def test_contract_hashes_unchanged(self):
        self.assertEqual(PARENT_CONTRACT_SHA,contract_report()["contract_sha256"])
        self.assertEqual(H01_SPEC_SHA,hashlib.sha256(canonical_bytes()).hexdigest())

    def test_no_execution_or_approval(self):
        self.assertFalse(any(EXPECTED_STATUS.values()))
        self.assertIn("NO_VERIFIER_IMPLEMENTATION",remediation_report()["decision"])

    def test_source_revision_recorded(self):
        self.assertEqual(SOURCE_REVIEW_SHA,"75129d093ee2127a1af4d8243a8a216a450f9c38")

    def test_budget_controls_are_draft_only(self):
        material=" ".join(REMEDIATIONS["AI-SEC-01"]["controls"]).lower()
        for term in ("25000000","50000000","100000","deadline"):
            self.assertIn(term,material)
        self.assertIn("not implemented",REMEDIATIONS["AI-SEC-01"]["remaining"])

    def test_provenance_distinct_from_content(self):
        text=" ".join(REMEDIATIONS["AI-SEC-03"]["controls"])
        self.assertIn("content_integrity_verified",text)
        self.assertIn("publisher_provenance_verified",text)
        self.assertFalse(EXPECTED_STATUS["content_integrity_verified"])
        self.assertFalse(EXPECTED_STATUS["publisher_provenance_verified"])

    def test_fixture_error_codes_are_defined(self):
        self.assertEqual(len(ERROR_CODES),len(set(ERROR_CODES)))
        self.assertTrue(all(v[1] in ERROR_CODES for v in TEST_CASES.values()))
        self.assertGreaterEqual(len(TEST_CASES),20)

    def test_no_existing_frozen_contract_mutation(self):
        old=copy.deepcopy(contract_report()["contract"])
        remediation_report()
        self.assertEqual(old,contract_report()["contract"])

    def test_output_json_deterministic(self):
        r=remediation_report()
        self.assertEqual(r,remediation_report())
        self.assertEqual(json.loads(json.dumps(r,allow_nan=False)),r)


if __name__=="__main__":
    unittest.main()
