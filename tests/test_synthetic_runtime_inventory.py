import json
import unittest
from unittest.mock import patch
from btc_engine.synthetic_runtime_inventory import (
    TOOLS, collect_read_only_capabilities, inventory_record, selection_record,
    require_runtime_enforcement,
)

class BTC058RuntimeInventoryTests(unittest.TestCase):
    def test_actual_inventory_is_read_only_and_no_go(self):
        record = inventory_record()
        print("BTC058_CI_INVENTORY="+json.dumps(record, sort_keys=True, separators=(",",":")), flush=True)
        self.assertTrue(record["capabilities"]["no_subprocess_or_network_probe_performed"])
        self.assertIsNone(record["selected_verified_runtime"])
        self.assertEqual(record["decision"], "NO_GO_ISOLATION_ENVIRONMENT_SELECTION_UNVERIFIED")
        self.assertFalse(record["real_market_data_authorized"])
        self.assertFalse(record["trading_authorized"])

    def test_no_tool_is_not_mistaken_for_isolation(self):
        cap = collect_read_only_capabilities(which=lambda _:None, system="Linux")
        rec = selection_record(cap)
        self.assertIsNone(rec["candidate_to_evaluate_next"])
        self.assertIsNone(rec["selected_verified_runtime"])

    def test_cli_presence_only_generates_evaluation_target(self):
        for name in ("podman", "docker", "nerdctl"):
            with self.subTest(name=name):
                cap=collect_read_only_capabilities(which=lambda tool: "/usr/bin/"+tool if tool==name else None, system="Linux")
                rec=selection_record(cap)
                self.assertEqual(rec["candidate_to_evaluate_next"],name)
                self.assertIsNone(rec["selected_verified_runtime"])
                self.assertFalse(rec["runtime_enforcement_verified"])

    def test_no_daemon_or_network_queries(self):
        with patch("subprocess.run",side_effect=AssertionError("never call runtime")), \
             patch("socket.socket",side_effect=AssertionError("never create socket")):
            collect_read_only_capabilities(which=lambda _:None,system="Linux")

    def test_fake_certification_claim_is_rejected(self):
        cap=collect_read_only_capabilities(which=lambda _:None,system="Linux")
        cap["security_certified"]=True
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_SECURITY_CLAIM"):
            selection_record(cap)

    def test_invalid_capabilities_rejected(self):
        with self.assertRaises(ValueError): selection_record({})
        cap=collect_read_only_capabilities(which=lambda _:None,system="Linux")
        cap["cli_present"]["docker"]="yes"
        with self.assertRaises(ValueError): selection_record(cap)

    def test_no_provisioning_and_historical_denial(self):
        with self.assertRaises(PermissionError):
            require_runtime_enforcement()
        from btc_engine.verifier_implementation_decision import decision_record
        self.assertEqual(decision_record()["decision"],"NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")
        self.assertFalse(any(decision_record()["permissions"].values()))

    def test_json_stable(self):
        cap=collect_read_only_capabilities(which=lambda _:None,system="Linux")
        record=selection_record(cap)
        self.assertEqual(json.loads(json.dumps(record, allow_nan=False)),record)
        self.assertEqual(set(cap["cli_present"]),set(TOOLS))

if __name__=="__main__":
    unittest.main()
