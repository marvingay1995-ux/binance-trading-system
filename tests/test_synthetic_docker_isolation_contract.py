"""BTC-060 static contract and refusal tests."""
import json
import unittest
from unittest.mock import patch
from btc_engine.synthetic_docker_isolation_contract import (
    REQUIRED_DOCKER_FLAGS, REQUIRED_RUNTIME_EVIDENCE,
    authorize_docker_execution, contract_record,
)

class BTC060DockerContractTests(unittest.TestCase):
    def test_gating_record_rejects_execution(self):
        r=contract_record()
        self.assertEqual(r["decision"],"EXECUTION_AUTHORIZATION_WITHHELD_SYNTHETIC_CONTRACT_DEFINED")
        for k in ("docker_execution_authorized","sandbox_security_verified",
                  "real_market_data_authorized","trading_authorized","docker_run_allowed"):
            self.assertFalse(r[k])

    def test_contract_is_read_only_no_spawns(self):
        with patch("subprocess.run",side_effect=AssertionError("must not run docker")):
            with patch("subprocess.Popen",side_effect=AssertionError("must not create process")):
                self.assertFalse(contract_record()["docker_execution_authorized"])

    def test_proposed_flags_lock_basic_restrictions(self):
        flags=set(REQUIRED_DOCKER_FLAGS)
        self.assertTrue({"--network=none","--read-only","--cap-drop=ALL",
                         "--security-opt=no-new-privileges:true",
                         "--pids-limit=32","--memory=256m",
                         "--cpus=1","--user=65534:65534"}.issubset(flags))
        self.assertFalse(any("privileged" in f and f.startswith("--privileged") for f in flags))

    def test_missing_execution_approval_cannot_be_overridden(self):
        for args in ({},{"owner_approved":True},{"security_verified":True,"docker_access":True}):
            with self.subTest(args=args):
                with self.assertRaisesRegex(PermissionError,"BTC060_DOCKER_EXECUTION_NOT_AUTHORIZED"):
                    authorize_docker_execution(**args)

    def test_evidence_covers_controls_and_privileges(self):
        data=" ".join(REQUIRED_RUNTIME_EVIDENCE).lower()
        for term in ("authorization","image","ipv4","ipv6","non-root","memory",
                     "pid","writable output","negative-control","cleanup"):
            self.assertIn(term,data)

    def test_baseline_exact_and_no_fake_runtime_security(self):
        record=contract_record()
        self.assertEqual(record["baseline_main_tests"],366)
        self.assertEqual(record["baseline_main_ci_run"],45170296024)
        self.assertIn("VERSION_METADATA_ONLY",record["observed_btc059_docker"])
        self.assertFalse(record["sandbox_security_verified"])

    def test_serializable_stable_contract(self):
        a=contract_record()
        self.assertEqual(json.loads(json.dumps(a,allow_nan=False)),a)
        self.assertEqual(a,contract_record())

    def test_historical_btc028_permissions_preserved(self):
        from btc_engine.verifier_implementation_decision import decision_record
        old=decision_record()
        self.assertEqual(old["decision"],"NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")
        self.assertFalse(any(old["permissions"].values()))

if __name__=="__main__":
    unittest.main()
