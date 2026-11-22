import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from btc_engine.synthetic_fixture_coverage import (
    CONTEXT_ONLY, SOURCE_COMMIT, coverage_report, expanded_fixture_bytes,
)
from btc_engine.synthetic_fixture_generator import BASE_CSV, LABEL, sha256
from btc_engine.synthetic_fixture_spec import CSV_SHA256, FAULT_CASES


class SyntheticFixtureCoverageTests(unittest.TestCase):
    def test_all_scenarios_accounted_without_claiming_verification(self):
        r = coverage_report()
        self.assertEqual(r["total_scenarios_registered"], 18)
        self.assertEqual(set(r["materialized_fixture_cases"]) | set(r["context_only_unexecuted"]), set(FAULT_CASES))
        self.assertFalse(set(r["materialized_fixture_cases"]) & set(r["context_only_unexecuted"]))
        self.assertEqual(r["security_verdict"], "VERIFIER_NOT_IMPLEMENTED_NO_SECURITY_PASS")

    def test_materialized_fixture_bytes_are_stable(self):
        self.assertEqual(expanded_fixture_bytes(), expanded_fixture_bytes())
        for key, data in expanded_fixture_bytes().items():
            item = coverage_report()["materialized_fixture_cases"][key]
            self.assertEqual(item["sha256"], sha256(data))
            self.assertEqual(item["evidence_status"], "FIXTURE_BYTES_GENERATED_ONLY_NOT_VERIFIER_TESTED")
            self.assertLess(len(data), 200_000)

    def test_mutations_are_real_not_empty(self):
        cases = expanded_fixture_bytes()
        self.assertEqual(cases["S01"].count(b"\n"), 2)
        self.assertEqual(cases["S02"].count(b"\n"), 4)
        self.assertIn(b"1778817600000001", cases["S03"])
        self.assertIn(b"NaN", cases["S04"])
        self.assertIn(b"-1.5", cases["S05"])
        self.assertGreater(len(cases["S06"].splitlines()[1]), 4096)
        self.assertNotEqual(cases["S07"], BASE_CSV)

    def test_unsafe_member_is_metadata_only(self):
        z = expanded_fixture_bytes()["S08"]
        with zipfile.ZipFile(io.BytesIO(z)) as archive:
            self.assertEqual(archive.namelist(), ["../escape.csv"])
        # Never extract to filesystem.

    def test_zip_symlink_member_is_marked_as_symlink(self):
        z = expanded_fixture_bytes()["S09"]
        with zipfile.ZipFile(io.BytesIO(z)) as archive:
            member = archive.infolist()[0]
            self.assertEqual((member.external_attr >> 16) & 0o170000, 0o120000)

    def test_crc_sample_is_rejected_by_standard_zip_reader(self):
        z = expanded_fixture_bytes()["S10"]
        with zipfile.ZipFile(io.BytesIO(z)) as archive:
            with self.assertRaises(zipfile.BadZipFile):
                archive.read("synthetic.csv")
        # A library reader's exception is not a test of the future verifier.

    def test_fake_source_claim_is_explicitly_unverified(self):
        claim = json.loads(expanded_fixture_bytes()["S16"])
        self.assertEqual(claim["provenance"], LABEL)
        self.assertFalse(claim["publisher_verified"])
        self.assertTrue(claim["test_only"])
        self.assertEqual(claim["raw_sha256"], CSV_SHA256)

    def test_context_only_cases_remain_unexecuted(self):
        self.assertEqual(set(CONTEXT_ONLY), {"S11","S12","S13","S14","S17","S18"})
        self.assertTrue(all(v["evidence_status"]=="NOT_MATERIALIZED_NOT_TESTED"
                            for v in coverage_report()["context_only_unexecuted"].values()))

    def test_no_trading_or_market_data_authorization(self):
        report = coverage_report()
        self.assertFalse(report["h01_backtesting_authorized"])
        self.assertFalse(report["real_market_data_processing_authorized"])
        self.assertFalse(report["trading_authorized"])
        self.assertEqual(report["baseline"], SOURCE_COMMIT)

    def test_manifest_is_json_compatible(self):
        report = coverage_report()
        self.assertEqual(report, json.loads(json.dumps(report, sort_keys=True)))

if __name__ == "__main__":
    unittest.main()
