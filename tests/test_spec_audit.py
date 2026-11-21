import copy
import json
import unittest
from btc_engine.spec_audit import audit_h01
from btc_engine.trend_registration import PROTOCOL, specification_report


class SpecAuditTests(unittest.TestCase):
    def test_default_blocks_everything(self):
        report=audit_h01()
        self.assertEqual(report["decision"],"BLOCKED_RESEARCH_SIMULATION_PAPER_AND_LIVE")
        self.assertEqual(set(report["permissions"].values()), {False})
        self.assertGreaterEqual(report["blocker_count"],8)

    def test_frozen_protocol_sha(self):
        self.assertEqual(audit_h01()["source_protocol_sha256"],
                         specification_report()["canonical_sha256"])

    def test_audit_does_not_modify_contract(self):
        before=copy.deepcopy(PROTOCOL)
        audit_h01()
        self.assertEqual(before,PROTOCOL)

    def test_detects_lookback_mutation(self):
        changed=copy.deepcopy(PROTOCOL)
        changed["trend"]["lookback_complete_bars"]=100
        result=audit_h01(changed)
        self.assertIn("SPEC-001",[f["id"] for f in result["findings"]])
        self.assertIsNone(result["source_protocol_sha256"])

    def test_detects_exposure_violation(self):
        changed=copy.deepcopy(PROTOCOL)
        changed["position"]["target_exposure_fraction_of_current_equity"]=.40
        self.assertIn("RISK-001",[f["id"] for f in audit_h01(changed)["findings"]])

    def test_detects_unauthorized_flag(self):
        changed=copy.deepcopy(PROTOCOL)
        changed["controls"]["paper_trading_authorized"]=True
        self.assertIn("SAFE-001",[f["id"] for f in audit_h01(changed)["findings"]])

    def test_warmup_and_comparator_open(self):
        ids={f["id"] for f in audit_h01()["findings"]}
        self.assertTrue({"DATA-002","COMP-001","SIGNAL-001","RISK-002"}.issubset(ids))

    def test_output_is_finite_json(self):
        self.assertEqual(json.loads(json.dumps(audit_h01(),allow_nan=False))["program"],"BTC-021")


if __name__=="__main__":
    unittest.main()
