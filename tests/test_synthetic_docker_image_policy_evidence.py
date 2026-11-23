"""BTC-062 fixed read-only Docker metadata and fail-closed readiness tests."""
import json
import subprocess
import unittest
from unittest.mock import patch

from btc_engine.synthetic_docker_image_policy_evidence import (
    COMMANDS, _image_metadata, _read_only_query, _security_metadata,
    require_docker_experiment, review_local_metadata,
)

class BTC062DockerImagePolicyTests(unittest.TestCase):
    def test_ci_read_only_evidence_and_non_authorization(self):
        record = review_local_metadata()
        print("BTC062_CI_EVIDENCE="+json.dumps(record,sort_keys=True,separators=(",",":")),flush=True)
        self.assertIsNone(record["trusted_local_image"])
        self.assertEqual(record["decision"],"NO_GO_DOCKER_EXECUTION_IMAGE_TRUST_AND_ENFORCEMENT_UNVERIFIED")
        for key in ("docker_execution_authorized","sandbox_security_verified",
                    "real_market_data_authorized","h01_backtesting_authorized","trading_authorized"):
            self.assertFalse(record[key])

    def test_image_digest_metadata_not_trusted_provenance(self):
        row=json.dumps({"Repository":"invented", "Tag":"latest","Digest":"sha256:"+"a"*64})
        result=_image_metadata(row)
        self.assertTrue(result["inventory_observed"])
        self.assertEqual(result["images_with_digest_count"],1)
        self.assertFalse(result["trusted_image_selected"])
        self.assertFalse(result["trusted_image_digest_verified"])

    def test_empty_image_list_is_not_trust(self):
        result=_image_metadata("")
        self.assertEqual(result["local_image_count"],0)
        self.assertFalse(result["trusted_image_selected"])

    def test_malformed_or_oversized_image_list_fails_closed(self):
        self.assertFalse(_image_metadata("not-json")["inventory_observed"])
        self.assertFalse(_image_metadata("\n".join("{}" for _ in range(1001)))["inventory_observed"])

    def test_security_options_are_hints_not_proof(self):
        metadata=_security_metadata('["name=rootless","name=seccomp,profile=builtin"]','"linux"')
        self.assertTrue(metadata["policy_metadata_observed"])
        self.assertTrue(metadata["rootless_in_security_options"])
        for key in ("rootless_enforcement_verified","no_network_enforcement_verified",
                    "readonly_mount_enforcement_verified","host_privilege_boundary_verified"):
            self.assertFalse(metadata[key])

    def test_malformed_policy_evidence_rejected(self):
        meta=_security_metadata("not-json",'"linux"')
        self.assertFalse(meta["policy_metadata_observed"])
        self.assertIsNone(meta["rootless_in_security_options"])

    def test_exact_commands_no_launch_pull_or_credential_reads(self):
        def fake(argv, **kw):
            self.assertEqual(argv[1:],list(COMMANDS[self.kind]))
            self.assertEqual(kw["cwd"],"/")
            self.assertFalse(kw.get("shell",False))
            self.assertEqual(kw["env"]["DOCKER_HOST"],"unix:///var/run/docker.sock")
            self.assertEqual(kw["env"]["DOCKER_CONFIG"],"/nonexistent")
            self.assertFalse(any(s in argv for s in ("run","create","start","pull","build","inspect")))
            return subprocess.CompletedProcess(argv,0,stdout="[]",stderr="")
        for name in COMMANDS:
            with self.subTest(name=name):
                self.kind=name
                data,reason=_read_only_query(name,which=lambda _: "/usr/bin/docker",runner=fake)
                self.assertEqual(reason,"METADATA_RETURNED")
                self.assertEqual(data,"[]")

    def test_bad_operation_missing_binary_and_timeout_fail_closed(self):
        with self.assertRaises(ValueError): _read_only_query("run")
        self.assertEqual(_read_only_query("images",which=lambda _:None)[1],"DOCKER_CLI_UNAVAILABLE")
        def timeout(*a,**kw): raise subprocess.TimeoutExpired("docker",1)
        self.assertEqual(_read_only_query("images",which=lambda _: "/usr/bin/docker",runner=timeout)[1],"READONLY_QUERY_TIMEOUT")

    def test_mock_fake_approval_cannot_override_evidence_gate(self):
        digest=json.dumps({"Digest":"sha256:"+"b"*64})
        outputs={"images":(digest,"METADATA_RETURNED"),
                 "security_options":('["name=rootless"]',"METADATA_RETURNED"),
                 "os_type":('"linux"',"METADATA_RETURNED")}
        record=review_local_metadata(query=lambda key:outputs[key])
        self.assertTrue(record["image_metadata"]["inventory_observed"])
        self.assertFalse(record["docker_execution_authorized"])
        self.assertIsNone(record["trusted_local_image"])
        with self.assertRaises(PermissionError): require_docker_experiment(approved=True)

    def test_repeatable_and_json_serializable_mock_record(self):
        outputs={"images":("","METADATA_RETURNED"),
                 "security_options":("[]","METADATA_RETURNED"),
                 "os_type":('"linux"',"METADATA_RETURNED")}
        a=review_local_metadata(query=lambda key:outputs[key])
        self.assertEqual(json.loads(json.dumps(a,allow_nan=False)),a)
        self.assertEqual(a,review_local_metadata(query=lambda key:outputs[key]))

if __name__=="__main__":
    unittest.main()
