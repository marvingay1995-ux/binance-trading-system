import json
import unittest
from unittest.mock import patch

from btc_engine.synthetic_image_trust_eligibility import (
    CI_OBSERVATION, EVIDENCE_REQUIREMENTS, assess_image_eligibility, require_execution,
)

class BTC063ImageTrustTests(unittest.TestCase):
    def test_observed_six_local_images_not_trusted(self):
        result = assess_image_eligibility()
        self.assertEqual(result["last_verified_ci_observation"]["local_image_count"],6)
        self.assertEqual(result["last_verified_ci_observation"]["images_with_digest_count"],6)
        self.assertIsNone(result["selected_image"])
        self.assertFalse(result["image_trust_verified"])

    def test_metadata_and_non_root_observation_not_security(self):
        result = assess_image_eligibility()
        self.assertFalse(result["last_verified_ci_observation"]["rootless_in_security_options"])
        self.assertFalse(result["os_isolation_verified"])
        self.assertFalse(result["synthetic_execution_eligible"])

    def test_all_reviewed_claims_cannot_grant_execution(self):
        claims={key:"INDEPENDENTLY_REVIEWED" for key in EVIDENCE_REQUIREMENTS}
        result=assess_image_eligibility(claims)
        self.assertEqual(result["caller_claims_independently_reviewed_count"],len(EVIDENCE_REQUIREMENTS))
        self.assertFalse(result["caller_evidence_authenticated"])
        self.assertFalse(result["docker_execution_authorized"])
        self.assertFalse(result["image_trust_verified"])

    def test_missing_requirements_reported(self):
        result=assess_image_eligibility()
        self.assertEqual(set(result["unverified_or_missing"]),set(EVIDENCE_REQUIREMENTS))
        self.assertTrue(all(v=="MISSING" for v in result["evidence_requirements"].values()))

    def test_invalid_and_extra_claims_rejected(self):
        for record in ({"unexpected":"INDEPENDENTLY_REVIEWED"},
                       {"approved_digest_against_independent_trusted_source":True},
                       "yes",{"locally_present_image_id_and_architecture":"TRUSTED"}):
            with self.subTest(record=record):
                with self.assertRaises(ValueError): assess_image_eligibility(record)

    def test_historical_gate_fail_closed(self):
        from btc_engine.verifier_implementation_decision import decision_record
        previous=decision_record()
        self.assertEqual(previous["decision"],"NO_GO_LOCAL_VERIFIER_IMPLEMENTATION")
        self.assertFalse(any(previous["permissions"].values()))

    def test_execution_refused_regardless_of_claim(self):
        with self.assertRaisesRegex(PermissionError,"BTC063_DOCKER_EXECUTION_NOT_AUTHORIZED"):
            require_execution(owner_approved=True,image_verified=True)

    def test_no_docker_calls_or_network(self):
        with patch("subprocess.run",side_effect=AssertionError("no subprocess")), \
             patch("subprocess.Popen",side_effect=AssertionError("no spawn")), \
             patch("socket.socket",side_effect=AssertionError("no socket")):
            result=assess_image_eligibility()
        self.assertFalse(result["docker_execution_authorized"])

    def test_json_stability(self):
        result=assess_image_eligibility()
        self.assertEqual(json.loads(json.dumps(result,allow_nan=False)),result)
        self.assertEqual(result,assess_image_eligibility())

    def test_separate_real_market_and_paper_restrictions(self):
        result=assess_image_eligibility()
        self.assertFalse(result["real_data_authorized"])
        self.assertFalse(result["h01_backtesting_authorized"])
        self.assertFalse(result["trading_authorized"])

if __name__=="__main__": unittest.main()
