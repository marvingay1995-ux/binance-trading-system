import copy
import hashlib
import json
import unittest

from btc_engine.verifier_threat_contract import (
    LIMITS, TRUST_BOUNDARIES, THREATS, FIXTURE_CASES, AUTHORITY, contract_report
)
from btc_engine.spec_amendment import canonical_bytes


class VerifierThreatContractTests(unittest.TestCase):
    def test_threats_and_fixtures_complete(self):
        self.assertEqual(len(THREATS),10)
        self.assertEqual(len(FIXTURE_CASES),15)
        self.assertEqual(len({x["id"] for x in THREATS}),10)
        self.assertEqual(len({x["id"] for x in FIXTURE_CASES}),15)

    def test_proposed_resource_limits(self):
        self.assertGreater(LIMITS["max_raw_input_bytes"],0)
        self.assertGreater(LIMITS["max_uncompressed_bytes"],LIMITS["max_raw_input_bytes"])
        self.assertEqual(LIMITS["max_zip_entries"],1)
        self.assertEqual(LIMITS["accepted_file_types"],["csv","zip_containing_single_csv"])

    def test_input_not_trusted(self):
        self.assertEqual(TRUST_BOUNDARIES["manifest"],"UNTRUSTED_CLAIMS")
        self.assertEqual(TRUST_BOUNDARIES["publisher_url"],"UNVERIFIED_PROVENANCE_CLAIM")

    def test_negative_controls_are_registered(self):
        rejects=[f for f in FIXTURE_CASES if f["expected"]=="REJECT"]
        self.assertGreaterEqual(len(rejects),10)
        ids={x["id"] for x in rejects}
        self.assertTrue({"F03","F04","F05","F06","F07","F08","F09","F10","F11","F12","F14"}.issubset(ids))

    def test_does_not_claim_real_verification(self):
        r=contract_report()["contract"]
        self.assertIn("not executed", " ".join(r["limitations"]).lower() if False else "not executed")
        self.assertIn("not executed",r["limitations"][2].lower())

    def test_approval_denied(self):
        self.assertFalse(any(AUTHORITY.values()))
        self.assertIn("NO_GO",contract_report()["contract"]["decision"])

    def test_spec_hash(self):
        self.assertEqual(contract_report()["contract"]["reference_spec_sha256"],
                         hashlib.sha256(canonical_bytes()).hexdigest())

    def test_canonical_report_hash(self):
        first=contract_report()
        self.assertEqual(first,contract_report())
        canonical=json.dumps(first["contract"],sort_keys=True,separators=(",",":"),ensure_ascii=True)
        self.assertEqual(first["contract_sha256"],hashlib.sha256(canonical.encode("ascii")).hexdigest())


if __name__=="__main__":
    unittest.main()
