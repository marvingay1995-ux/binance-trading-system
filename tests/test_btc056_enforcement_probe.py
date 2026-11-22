import errno
import json
import subprocess
import unittest
from unittest.mock import patch
from btc_engine.synthetic_enforcement_probe import verify_unprivileged_enforcement, CHILD

class BTC056EnforcementTests(unittest.TestCase):
    def test_actual_environment_probed_and_status_reported(self):
        outcome = verify_unprivileged_enforcement()
        print("BTC056_ACTUAL_PROBE="+json.dumps(outcome, sort_keys=True), flush=True)
        self.assertIn(outcome["status"], ("ENFORCEMENT_UNAVAILABLE","LIMITED_KERNEL_DENIAL_OBSERVED"))
        for key in ("filesystem_isolation_verified","comprehensive_network_isolation_verified",
                    "security_certified","real_data_authorized","trading_authorized"):
            self.assertFalse(outcome[key])
    def test_invalid_timeout(self):
        for v in (0,5,True,-1):
            with self.assertRaises(ValueError): verify_unprivileged_enforcement(timeout=v)
    def test_unavailable_platform_before_process(self):
        with patch("btc_engine.synthetic_enforcement_probe.sys.platform","win32"), \
             patch("btc_engine.synthetic_enforcement_probe.subprocess.run",side_effect=AssertionError("unexpected")):
            self.assertEqual(verify_unprivileged_enforcement()["reason"],"UNSUPPORTED_PLATFORM")
    def test_unshare_missing_no_launch(self):
        with patch("btc_engine.synthetic_enforcement_probe.shutil.which", return_value=None), \
             patch("btc_engine.synthetic_enforcement_probe.subprocess.run",side_effect=AssertionError("unexpected")):
            self.assertEqual(verify_unprivileged_enforcement()["reason"],"UNSHARE_UNAVAILABLE")
    def test_denied_creation(self):
        self.assertEqual(self.inject(subprocess.CompletedProcess([],1,"",""),"UNPRIVILEGED_NAMESPACE_DENIED")["status"],"ENFORCEMENT_UNAVAILABLE")
    def test_parent_timeout(self):
        with patch("btc_engine.synthetic_enforcement_probe.shutil.which", return_value="/usr/bin/unshare"), \
             patch("btc_engine.synthetic_enforcement_probe.subprocess.run", side_effect=subprocess.TimeoutExpired("unshare",0.1)):
            self.assertEqual(verify_unprivileged_enforcement()["reason"],"CHILD_TIMEOUT")
    def inject(self, completed, expected):
        with patch("btc_engine.synthetic_enforcement_probe.shutil.which",return_value="/usr/bin/unshare"), \
             patch("btc_engine.synthetic_enforcement_probe.os.readlink",return_value="net:[123]"), \
             patch("btc_engine.synthetic_enforcement_probe.subprocess.run",return_value=completed):
            result=verify_unprivileged_enforcement()
        self.assertEqual(result["reason"],expected)
        return result
    def test_wrong_namespace_and_missing_caps_fail_closed(self):
        for obj in (
            {"status":"PRECONDITION_FAILED"},
            {"status":"CHECKED","distinct":False,"only_loopback":True,"routes_absent":True,"cpu_cap":True,"memory_cap":True,"connect_errno":errno.ENETUNREACH},
            {"status":"CHECKED","distinct":True,"only_loopback":True,"routes_absent":True,"cpu_cap":False,"memory_cap":True,"connect_errno":errno.ENETUNREACH},
            {"status":"CHECKED","distinct":True,"only_loopback":True,"routes_absent":True,"cpu_cap":True,"memory_cap":True,"connect_errno":0},
        ):
            expected="SAFE_PREFLIGHT_FAILED" if obj["status"]=="PRECONDITION_FAILED" else "KERNEL_DENIAL_NOT_OBSERVED"
            self.inject(subprocess.CompletedProcess([],0,json.dumps(obj),""),expected)
    def test_good_mock_record_still_denies_general_security(self):
        obj={"status":"CHECKED","distinct":True,"only_loopback":True,"routes_absent":True,
             "cpu_cap":True,"memory_cap":True,"connect_errno":errno.ENETUNREACH}
        with patch("btc_engine.synthetic_enforcement_probe.shutil.which",return_value="/usr/bin/unshare"), \
             patch("btc_engine.synthetic_enforcement_probe.os.readlink",return_value="net:[1]"), \
             patch("btc_engine.synthetic_enforcement_probe.subprocess.run",return_value=subprocess.CompletedProcess([],0,json.dumps(obj),"")):
            result=verify_unprivileged_enforcement()
        self.assertEqual(result["status"],"LIMITED_KERNEL_DENIAL_OBSERVED")
        self.assertFalse(result["comprehensive_network_isolation_verified"])
        self.assertFalse(result["security_certified"])
    def test_child_has_safe_preflight_and_only_reserved_address(self):
        self.assertIn('interfaces == ["lo"]',CHILD)
        self.assertIn('"198.51.100.1"',CHILD)
        self.assertNotIn("binance",CHILD.lower())
        self.assertIn("if not safe:",CHILD)
    def test_existing_denial_persists(self):
        from btc_engine.verifier_implementation_decision import decision_record
        d=decision_record()
        self.assertEqual(d["decision"],"NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")
        self.assertFalse(any(d["permissions"].values()))
if __name__=="__main__": unittest.main()
