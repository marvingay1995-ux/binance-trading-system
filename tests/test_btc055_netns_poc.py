import json
import subprocess
import unittest
from unittest.mock import patch
from btc_engine.synthetic_netns_poc import probe_unprivileged_netns, CHILD

class BTC055Tests(unittest.TestCase):
    def test_actual_probe_reports_only_observation_or_unavailability(self):
        result = probe_unprivileged_netns()
        self.assertIn(result["status"], ("UNPRIVILEGED_NETNS_OBSERVED","ISOLATION_UNAVAILABLE"))
        for key in ("os_network_isolation_verified","real_data_authorized","trading_authorized","security_certified"):
            self.assertFalse(result[key])
    def test_invalid_timeout_refused(self):
        for value in (0,5,True,-1):
            with self.assertRaises(ValueError):
                probe_unprivileged_netns(value)
    def test_unsupported_platform_refused_before_spawn(self):
        with patch("btc_engine.synthetic_netns_poc.sys.platform","win32"), patch("btc_engine.synthetic_netns_poc.subprocess.run",side_effect=AssertionError):
            self.assertEqual(probe_unprivileged_netns()["reason"],"UNSUPPORTED_PLATFORM")
    def test_missing_binary_refused_before_spawn(self):
        with patch("btc_engine.synthetic_netns_poc.shutil.which",return_value=None), patch("btc_engine.synthetic_netns_poc.subprocess.run",side_effect=AssertionError):
            self.assertEqual(probe_unprivileged_netns()["reason"],"UNSHARE_NOT_INSTALLED")
    def test_namespace_denied_refused(self):
        p=subprocess.CompletedProcess([],1,"","denied")
        with patch("btc_engine.synthetic_netns_poc.shutil.which",return_value="/usr/bin/unshare"), patch("btc_engine.synthetic_netns_poc.subprocess.run",return_value=p):
            self.assertEqual(probe_unprivileged_netns()["reason"],"NAMESPACE_CREATION_DENIED")
    def test_timeout_refused(self):
        with patch("btc_engine.synthetic_netns_poc.shutil.which",return_value="/usr/bin/unshare"), patch("btc_engine.synthetic_netns_poc.subprocess.run",side_effect=subprocess.TimeoutExpired("unshare",1)):
            self.assertEqual(probe_unprivileged_netns()["reason"],"PROBE_TIMEOUT")
    def test_bad_json_refused(self):
        p=subprocess.CompletedProcess([],0,"not json","")
        with patch("btc_engine.synthetic_netns_poc.shutil.which",return_value="/usr/bin/unshare"), patch("btc_engine.synthetic_netns_poc.subprocess.run",return_value=p):
            self.assertEqual(probe_unprivileged_netns()["reason"],"INVALID_EVIDENCE")
    def test_same_ns_and_external_routes_refused(self):
        for routes,ns in ((0,"net:[1]"),(2,"net:[2]")):
            p=subprocess.CompletedProcess([],0,json.dumps({"ns":ns,"nonloop_routes":routes,"real_data":False,"trading":False}),"")
            with patch("btc_engine.synthetic_netns_poc.shutil.which",return_value="/usr/bin/unshare"), patch("btc_engine.synthetic_netns_poc.os.readlink",return_value="net:[1]"), patch("btc_engine.synthetic_netns_poc.subprocess.run",return_value=p):
                self.assertEqual(probe_unprivileged_netns()["reason"],"ISOLATION_EVIDENCE_INSUFFICIENT")
    def test_no_network_traffic_in_child_and_historical_denial(self):
        self.assertNotIn("socket",CHILD)
        from btc_engine.verifier_implementation_decision import decision_record
        self.assertEqual(decision_record()["decision"],"NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")
if __name__=="__main__":
    unittest.main()
