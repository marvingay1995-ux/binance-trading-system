import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from btc_engine.synthetic_fixture_generator import (
    BASE_CSV, LABEL, MAX_GENERATED_BYTES, fixture_bytes, generate,
    manifest_for, sha256,
)
from btc_engine.synthetic_fixture_spec import CSV_SHA256, JSONL_SHA256


class SyntheticFixtureGeneratorTests(unittest.TestCase):
    def test_golden_hash_is_frozen(self):
        f = fixture_bytes()
        self.assertEqual(sha256(f["golden.csv"]), CSV_SHA256)
        self.assertEqual(sha256(f["golden.jsonl"]), JSONL_SHA256)

    def test_zip_is_deterministic_and_one_member(self):
        first = fixture_bytes()["golden.zip"]
        self.assertEqual(first, fixture_bytes()["golden.zip"])
        import io
        with zipfile.ZipFile(io.BytesIO(first)) as z:
            self.assertEqual(z.namelist(), ["invented.csv"])
            self.assertEqual(z.read("invented.csv"), BASE_CSV)

    def test_zip_unsafe_name_is_data_not_extracted(self):
        import io
        data = fixture_bytes()["unsafe_member.zip"]
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            self.assertEqual(z.namelist(), ["../escape.csv"])
        # No extraction or verifier verdict in this test.

    def test_synthetic_cases_not_real(self):
        cases = fixture_bytes()
        self.assertEqual(len(cases), 9)
        self.assertNotEqual(cases["changed_bytes.csv"], BASE_CSV)
        self.assertIn(b"NaN", cases["nan_ohlc.csv"])
        self.assertIn(b"-1.5", cases["negative_volume.csv"])
        self.assertTrue(all(len(x) <= MAX_GENERATED_BYTES for x in cases.values()))

    def test_manifest_labels_every_item_and_records_hash(self):
        cases = fixture_bytes()
        m = manifest_for(cases)
        self.assertEqual(m["provenance"], LABEL)
        self.assertEqual(m["negative_fixture_status"], "GENERATED_NOT_VERIFIER_TESTED")
        for name, data in cases.items():
            self.assertEqual(m["cases"][name]["sha256"], sha256(data))
            self.assertEqual(m["cases"][name]["provenance"], LABEL)

    def test_write_into_new_directory_only(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent) / "synthetic"
            m = generate(str(root))
            self.assertTrue((root / "golden.csv").exists())
            self.assertEqual((root / "golden.csv").read_bytes(), BASE_CSV)
            manifest = json.loads((root / "manifest.json").read_text())
            self.assertEqual(manifest, m)
            with self.assertRaises(FileExistsError):
                generate(str(root))

    def test_existing_path_not_overwritten(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent) / "already"
            root.mkdir()
            (root / "sentinel.txt").write_text("untouched")
            with self.assertRaises(FileExistsError):
                generate(str(root))
            self.assertEqual((root / "sentinel.txt").read_text(), "untouched")

    def test_symlink_parent_rejected(self):
        with tempfile.TemporaryDirectory() as parent:
            base = Path(parent)
            actual = base / "actual"
            actual.mkdir()
            link = base / "link"
            try:
                link.symlink_to(actual, target_is_directory=True)
            except (NotImplementedError, OSError):
                self.skipTest("symlinks unavailable on runner")
            with self.assertRaises(ValueError):
                generate(str(link / "child"))

    def test_inventories_identical(self):
        self.assertEqual(fixture_bytes(), fixture_bytes())


if __name__ == "__main__":
    unittest.main()
