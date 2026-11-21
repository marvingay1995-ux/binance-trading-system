import copy
import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone

from btc_engine.simulator_architecture import (
    ARCHITECTURE, WARMUP_START, WARMUP_END_EXCLUSIVE,
    architecture_report, validate_manifest,
)
from btc_engine.spec_amendment import canonical_bytes

def sample(kind="WARMUP_ONLY"):
    s=WARMUP_START if kind=="WARMUP_ONLY" else WARMUP_END_EXCLUSIVE
    first=datetime.fromisoformat(s.replace("Z","+00:00"))
    count=1200 if kind=="WARMUP_ONLY" else 360
    end=(first+timedelta(hours=4*count)).isoformat().replace("+00:00","Z")
    return {"symbol":"BTCUSDT","interval":"4h","kind":kind,
            "source_uri":"https://data.binance.vision/example.zip",
            "retrieved_utc":"2027-03-01T00:00:00Z",
            "period_start_utc":s,"period_end_exclusive_utc":end,
            "candle_count":count,"raw_sha256":"a"*64,"canonical_sha256":"b"*64,
            "specification_sha256":hashlib.sha256(canonical_bytes()).hexdigest(),
            "review_status":"UNVERIFIED_REVIEW_ONLY"}


class SimulatorArchitectureTests(unittest.TestCase):
    def test_no_simulator_or_execution(self):
        r=architecture_report()
        self.assertEqual(r["authorization"],"NONE")
        self.assertFalse(any(ARCHITECTURE["isolation"].values()))

    def test_warmup_manifest_shape_only(self):
        r=validate_manifest(sample())
        self.assertEqual(r["status"],"MANIFEST_SHAPE_VALIDATED_CONTENT_NOT_VERIFIED")
        self.assertFalse(r["candles_checked"])

    def test_future_manifest_shape_only(self):
        r=validate_manifest(sample("PROSPECTIVE_ONLY"))
        self.assertFalse(r["backtesting_authorized"])

    def test_missing_hash_fails(self):
        item=sample()
        item["raw_sha256"]="notahash"
        with self.assertRaises(ValueError):validate_manifest(item)

    def test_wrong_specification_fails(self):
        item=sample()
        item["specification_sha256"]="0"*64
        with self.assertRaises(ValueError):validate_manifest(item)

    def test_missing_bar_in_manifest_fails(self):
        item=sample()
        item["candle_count"]=1199
        with self.assertRaises(ValueError):validate_manifest(item)

    def test_wrong_warmup_boundary_fails(self):
        item=sample()
        item["period_start_utc"]="2026-05-15T04:00:00Z"
        with self.assertRaises(ValueError):validate_manifest(item)

    def test_extra_fields_fail(self):
        item=sample()
        item["approved"]=True
        with self.assertRaises(ValueError):validate_manifest(item)

    def test_self_certification_fails(self):
        item=sample()
        item["review_status"]="VERIFIED"
        with self.assertRaises(ValueError):validate_manifest(item)

    def test_timestamp_alignment_fails(self):
        item=sample()
        item["period_start_utc"]="2026-05-15T01:00:00Z"
        with self.assertRaises(ValueError):validate_manifest(item)

    def test_future_overlap_fails(self):
        item=sample("PROSPECTIVE_ONLY")
        item["period_start_utc"]=WARMUP_START
        with self.assertRaises(ValueError):validate_manifest(item)

    def test_bool_is_not_candle_count(self):
        item=sample()
        item["candle_count"]=True
        with self.assertRaises(ValueError):validate_manifest(item)

    def test_json_serializable(self):
        self.assertEqual(json.loads(json.dumps(architecture_report()))["architecture"]["program"],"BTC-024")


if __name__ == "__main__":
    unittest.main()
