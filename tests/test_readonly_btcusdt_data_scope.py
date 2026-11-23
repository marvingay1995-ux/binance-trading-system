import json
import unittest
from unittest.mock import patch
from btc_engine.readonly_btcusdt_data_scope import CANDIDATE, ALTERNATE, scope_proposal, require_public_fetch

class BTC065ReadOnlyScopeTests(unittest.TestCase):
    def test_public_keyless_only(self):
        c=scope_proposal()["preferred_source_candidate"]
        self.assertEqual(c["origin"],"https://data-api.binance.vision")
        self.assertEqual(c["path"],"/api/v3/klines")
        self.assertEqual(c["method"],"GET")
        self.assertEqual(c["symbol"],"BTCUSDT")
        self.assertEqual(c["intervals"],["1h","4h"])
        self.assertFalse(c["request_key_or_signed_auth"])

    def test_strict_proposed_limits(self):
        c=scope_proposal()["preferred_source_candidate"]
        self.assertEqual(c["max_rows_per_request_proposed"],500)
        self.assertEqual(c["max_requests_proposed_per_minute"],1)
        self.assertEqual(c["default_timestamp_unit"],"MILLISECONDS")

    def test_archive_distinction(self):
        a=scope_proposal()["alternate_source"]
        self.assertFalse(a["considered_for_initial_gate"])
        self.assertTrue(a["zip_csv_risk_review_required"])
        self.assertEqual(a["published_spot_from_2025_timestamp_unit"],"MICROSECONDS")
        self.assertTrue(a["checksum_file_is_not_independent_publisher_authentication"])

    def test_approval_and_review_missing(self):
        r=scope_proposal()
        self.assertEqual(r["decision"],"PROPOSAL_COMPLETE_R1_APPROVAL_NOT_GRANTED")
        self.assertFalse(r["owner_approval_recorded"])
        self.assertFalse(r["independent_security_review_complete"])
        self.assertFalse(r["publisher_authenticity_verified"])

    def test_operational_permissions_denied(self):
        r=scope_proposal()
        for key in ("network_fetch_authorized","real_data_ingestion_authorized",
                    "backtesting_authorized","paper_trading_authorized",
                    "live_trading_authorized","account_api_access_authorized",
                    "docker_execution_authorized"):
            self.assertFalse(r[key])

    def test_approval_claims_cannot_override(self):
        for opts in ({},{"owner_approved":True},{"public_data_approved":True,"security_review":True}):
            with self.subTest(opts=opts):
                with self.assertRaisesRegex(PermissionError,"BTC065_PUBLIC_DATA_FETCH_NOT_AUTHORIZED"):
                    require_public_fetch(**opts)

    def test_no_network_or_process(self):
        with patch("socket.socket",side_effect=AssertionError("no network")), \
             patch("subprocess.run",side_effect=AssertionError("no command")):
            self.assertFalse(scope_proposal()["network_fetch_authorized"])

    def test_historical_denial_integrity(self):
        from btc_engine.verifier_implementation_decision import decision_record
        old=decision_record()
        self.assertEqual(old["decision"],"NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")
        self.assertFalse(any(old["permissions"].values()))

    def test_forged_key_auth_change_refused(self):
        with patch.dict(CANDIDATE,{"request_key_or_signed_auth":True}):
            with self.assertRaisesRegex(PermissionError,"KEYLESS_CONTRACT_CHANGED"):
                scope_proposal()

    def test_stable_report(self):
        r=scope_proposal()
        self.assertEqual(r, json.loads(json.dumps(r,allow_nan=False)))
        self.assertEqual(r,scope_proposal())
        self.assertEqual(r["reviewed_main_tests"],414)
if __name__=="__main__": unittest.main()
