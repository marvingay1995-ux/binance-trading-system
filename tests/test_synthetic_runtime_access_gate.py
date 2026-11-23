import json
import subprocess
import unittest
from unittest.mock import patch
from btc_engine.synthetic_runtime_access_gate import (
    COMMANDS, probe_local_runtime, inventory_runtime_access, require_sandbox,
)

def completion(out, code=0):
    return subprocess.CompletedProcess(["test"],code,stdout=out,stderr="")

class BTC059ReadOnlyAccessTests(unittest.TestCase):
    def test_live_runtime_metadata_only(self):
        result = inventory_runtime_access()
        print("BTC059_CI_RUNTIME_ACCESS="+json.dumps(result,sort_keys=True,separators=(",",":")),flush=True)
        self.assertFalse(result["os_network_isolation_verified"])
        self.assertFalse(result["real_data_authorized"])
        self.assertFalse(result["trading_authorized"])
        self.assertIsNone(result["selected_verified_sandbox"])

    def test_podman_version_is_not_sandbox_authorization(self):
        record = probe_local_runtime("podman",which=lambda n:"/usr/bin/podman",
                                     runner=lambda *a,**k:completion('{"Client":{"Version":"5.0"}}'))
        self.assertEqual(record["status"],"LOCAL_ENGINE_RESPONDED")
        self.assertFalse(record["rootless_verified"])
        self.assertFalse(record["container_launch_authorized"])

    def test_docker_server_version_not_isolation(self):
        record = probe_local_runtime("docker",which=lambda n:"/usr/bin/docker",
                                     runner=lambda *a,**k:completion('{"Version":"27.0"}'))
        self.assertEqual(record["status"],"LOCAL_ENGINE_RESPONDED")
        self.assertFalse(record["network_none_verified"])
        self.assertFalse(record["os_isolation_verified"])

    def test_missing_cli_before_run(self):
        with patch("subprocess.run",side_effect=AssertionError("must not run")):
            self.assertEqual(probe_local_runtime("podman",which=lambda _:None)["reason"],"CLI_NOT_FOUND")

    def test_local_only_version_commands(self):
        for name in COMMANDS:
            def safe_run(argv,**kwargs):
                self.assertEqual(argv[1:],list(COMMANDS[name]))
                self.assertFalse(kwargs.get("shell",False))
                self.assertFalse(any("pull" in s or "run"==s or "info"==s for s in argv))
                self.assertEqual(kwargs["cwd"],"/")
                self.assertEqual(kwargs["env"]["DOCKER_HOST"],"unix:///var/run/docker.sock")
                return completion('{"Client":{"Version":"5.0"}}' if name=="podman" else '{"Version":"27.0"}')
            probe_local_runtime(name,which=lambda n:"/usr/bin/"+n,runner=safe_run)

    def test_bad_timeout_and_name(self):
        for bad in (0,5,True,-1):
            with self.assertRaises(ValueError): probe_local_runtime("docker",timeout=bad)
        with self.assertRaises(ValueError): probe_local_runtime("nerdctl")

    def test_timeout_and_nonzero_fail_closed(self):
        self.assertEqual(probe_local_runtime("docker",which=lambda n:"/usr/bin/docker",
                         runner=lambda *a,**k:completion("",1))["reason"],"VERSION_QUERY_REJECTED")
        def fail(*a,**kw): raise subprocess.TimeoutExpired("docker",0.1)
        self.assertEqual(probe_local_runtime("docker",which=lambda n:"/usr/bin/docker",runner=fail)["reason"],"VERSION_QUERY_TIMEOUT")

    def test_invalid_or_null_server_rejected(self):
        for stdout in ("not json","null","{}",'{"Version":""}'):
            self.assertEqual(probe_local_runtime("docker",which=lambda n:"/usr/bin/docker",
                              runner=lambda *a,**k:completion(stdout))["status"],"UNAVAILABLE")

    def test_no_general_trading_or_file_authority(self):
        from btc_engine.verifier_implementation_decision import decision_record
        self.assertFalse(any(decision_record()["permissions"].values()))
        with self.assertRaises(PermissionError): require_sandbox()

if __name__=="__main__":
    unittest.main()
