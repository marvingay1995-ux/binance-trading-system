import hashlib
import json
import unittest

from btc_engine.synthetic_fixture_spec import (
    AUTHORIZATION, BOUNDS, CSV_SHA256, FAULT_CASES, GOLDEN_CSV,
    GOLDEN_JSONL, JSONL_SHA256, SCHEMA, contract_record,
)


class SyntheticFixtureSpecTests(unittest.TestCase):
    def test_golden_literal_csv_hash(self):
        self.assertEqual(hashlib.sha256(GOLDEN_CSV.encode("utf-8")).hexdigest(), CSV_SHA256)

    def test_golden_literal_canonical_hash(self):
        self.assertEqual(hashlib.sha256(GOLDEN_JSONL.encode("utf-8")).hexdigest(), JSONL_SHA256)

    def test_two_contiguous_4h_synthetic_bars(self):
        lines = GOLDEN_CSV.splitlines()
        self.assertEqual(len(lines), 3)
        first = int(lines[1].split(",")[0])
        second = int(lines[2].split(",")[0])
        self.assertEqual(second - first, 14_400_000)

    def test_canonical_schema_fields(self):
        self.assertEqual(SCHEMA["column_order"], ["open_time_ms","open","high","low","close","volume"])
        self.assertIn("no BOM", SCHEMA["encoding"])

    def test_single_fault_case_catalog(self):
        self.assertEqual(len(FAULT_CASES), 18)
        self.assertEqual(FAULT_CASES["S16"]["expected"], "CONTENT_VALID_SOURCE_UNVERIFIED")

    def test_bounds_are_still_proposed(self):
        self.assertEqual(BOUNDS["raw_bytes"], 25_000_000)
        self.assertEqual(BOUNDS["zip_entries"], 1)
        self.assertIn("proposed_bounds_not_enforced", contract_record())

    def test_all_implementation_permissions_false(self):
        self.assertTrue(AUTHORIZATION["fixture_format_contract_recorded"])
        self.assertFalse(any(v for k,v in AUTHORIZATION.items() if k != "fixture_format_contract_recorded"))

    def test_no_market_data_or_strategy(self):
        self.assertTrue(contract_record()["golden_reference"]["invented_data_only"])
        self.assertEqual(contract_record()["decision"], "SPECIFICATION_RECORDED_IMPLEMENTATION_AUTHORIZATION_WITHHELD")

    def test_json_round_trip(self):
        report = contract_record()
        self.assertEqual(json.loads(json.dumps(report, allow_nan=False)), report)


if __name__ == "__main__":
    unittest.main()
