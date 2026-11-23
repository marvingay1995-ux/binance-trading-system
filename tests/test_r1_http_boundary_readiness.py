"""BTC-072 evidence-linked synthetic HTTP boundary readiness tests."""
import json
import unittest
from unittest.mock import patch

from btc_engine.r1_http_boundary_readiness import (
    FINDINGS, GATES, readiness_record, require_external_data_or_order
)
from btc_engine.r1_offline_http_response import (
    invented_response, review_invented_response,
)
from btc_engine.r1_offline_synthetic_json import SYNTHETIC_FIXTURES

class BTC072SyntheticBoundaryReviewTests(unittest.TestCase):
    def test_actual_decision_not_a_fetch_approval(self):
        r=readiness_record()
        self.assertEqual(r["decision"],"NO_GO_EXTERNAL_DATA_R1_SECURITY_AND_APPROVAL_GATES_MISSING")
        self.assertTrue(r["internal_synthetic_testing_remains_permitted"])
        self.assertEqual(r["reviewed_main_tests"],493)

    def test_synthetic_1h_and_4h_only(self):
        r=readiness_record()
        self.assertEqual(set(r["invented_fixture_checks"]),{"1h","4h"})
        self.assertTrue(all(x["synthetic_only"] for x in r["invented_fixture_checks"].values()))
        self.assertTrue(all(not x["real_data_verified"] for x in r["invented_fixture_checks"].values()))

    def test_evidence_gates_are_not_inferred(self):
        gates=readiness_record()["gate_evidence"]
        self.assertEqual(gates["OWNER_R1_OFFLINE_ONLY_SCOPE"],"SATISFIED_FOR_INVENTED_FIXTURES_ONLY")
        self.assertEqual(gates["IDENTIFIED_INDEPENDENT_SECURITY_SIGNOFF"],"MISSING")
        self.assertEqual(gates["SEPARATE_OWNER_APPROVAL_FOR_REAL_PUBLIC_DATA"],"NOT_GRANTED")
        self.assertEqual(gates["FIXTURE_REGISTRY_IMMUTABILITY_AND_INTEGRITY"],"NOT_VERIFIED")

    def test_findings_have_ids_and_distinct_resolution(self):
        self.assertEqual(len(FINDINGS),5)
        self.assertEqual(len({x["id"] for x in FINDINGS}),len(FINDINGS))
        self.assertTrue(all(x["evidence"] and x["resolution"] for x in FINDINGS))
        self.assertTrue(any(x["severity"]=="BLOCKING" for x in FINDINGS))

    def test_mutable_fixture_registry_is_a_real_boundary_gap(self):
        # Internal mutation is possible if code in this process already has
        # write access. This does not mean a remote actor can mutate it.
        original=SYNTHETIC_FIXTURES["1h"]
        altered=json.loads(original)
        altered[0][1]="101"
        altered[0][2]="103"
        altered[0][3]="100"
        altered[0][4]="102"
        substitute=json.dumps(altered,separators=(",",":")).encode("ascii")
        with patch.dict(SYNTHETIC_FIXTURES,{"1h":substitute}):
            result=review_invented_response("1h",invented_response("1h"))
            self.assertEqual(result["body_sha256"],
                             __import__("hashlib").sha256(substitute).hexdigest())
            self.assertFalse(result["real_data_verified"])
        self.assertEqual(SYNTHETIC_FIXTURES["1h"],original)

    def test_old_approved_fixture_only_cannot_be_external_admission(self):
        env=invented_response("4h")
        env["body"]=env["body"]+b" "
        env["headers"]["content-length"]=str(len(env["body"]))
        with self.assertRaises(PermissionError):
            review_invented_response("4h",env)

    def test_no_operational_permissions(self):
        r=readiness_record()
        for field in ("independent_security_review_verified",
                      "real_https_transport_implemented",
                      "external_response_admission_authorized",
                      "public_market_data_fetch_authorized",
                      "authentic_data_ingestion_authorized",
                      "backtesting_authorized","paper_trading_authorized",
                      "live_spot_trading_authorized","exchange_credentials_authorized",
                      "orders_authorized","docker_execution_authorized"):
            self.assertFalse(r[field])

    def test_mocked_prior_auth_change_is_denied(self):
        from btc_engine.r1_offline_http_response import security_decision
        previous=security_decision()
        previous["real_market_data_ingestion_authorized"]=True
        with patch("btc_engine.r1_http_boundary_readiness.btc071_decision",return_value=previous):
            with self.assertRaisesRegex(PermissionError,"BTC071_GATE_CHANGED"):
                readiness_record()

    def test_no_network_process_or_filesystem(self):
        with patch("socket.socket",side_effect=AssertionError("unexpected network")), \
             patch("subprocess.run",side_effect=AssertionError("unexpected process")), \
             patch("builtins.open",side_effect=AssertionError("unexpected disk")):
            self.assertFalse(readiness_record()["public_market_data_fetch_authorized"])

    def test_approval_arguments_always_denied(self):
        with self.assertRaisesRegex(PermissionError,"BTC072_EXTERNAL_DATA_AND_TRADING_NO_GO"):
            require_external_data_or_order(owner_approved=True,security_passed=True)

    def test_repeatable_json_serialization(self):
        x=readiness_record()
        self.assertEqual(x,json.loads(json.dumps(x,allow_nan=False)))
        self.assertEqual(x,readiness_record())

if __name__=="__main__": unittest.main()
