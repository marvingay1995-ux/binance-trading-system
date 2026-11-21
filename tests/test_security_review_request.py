import hashlib
import json
import unittest

from btc_engine.security_review_request import (
    REQUIRED_REVIEW_RECORD_FIELDS, ALLOWED_REVIEW_OUTCOMES,
    request_package, validate_proposed_review_fields, require_implementation_authorization,
)
from btc_engine.verifier_threat_contract import contract_report
from btc_engine.spec_amendment import canonical_bytes


def proposed_record():
    record = {key: "placeholder-not-a-signature" for key in REQUIRED_REVIEW_RECORD_FIELDS}
    record["decision"] = "APPROVE_SCOPE_FOR_SEPARATE_OWNER_DECISION"
    return record


class SecurityReviewRequestTests(unittest.TestCase):
    def test_request_is_not_submitted(self):
        report = request_package()
        self.assertFalse(report["reviewer_request"]["request_sent"])
        self.assertFalse(report["reviewer_request"]["reviewer_assigned"])
        self.assertEqual(report["status"], "REVIEW_REQUEST_PREPARED_NOT_SUBMITTED")

    def test_no_execution_permissions(self):
        self.assertFalse(any(request_package()["authorizations"].values()))

    def test_cryptographic_references(self):
        r = request_package()
        self.assertEqual(r["reviewed_btc027_contract_sha256"], contract_report()["contract_sha256"])
        self.assertEqual(r["reviewed_h01_v2_spec_sha256"], hashlib.sha256(canonical_bytes()).hexdigest())

    def test_all_threat_and_fixture_ids(self):
        request = request_package()["reviewer_request"]
        self.assertEqual(request["fixed_threat_ids"], [f"T{i:02d}" for i in range(1, 11)])
        self.assertEqual(request["fixed_fixture_ids"], [f"F{i:02d}" for i in range(1, 16)])

    def test_valid_shape_still_untrusted(self):
        x = validate_proposed_review_fields(proposed_record())
        self.assertEqual(x["review_record_shape"], "VALID_BUT_UNAUTHENTICATED")
        self.assertFalse(x["signature_verified"])
        self.assertFalse(x["implementation_authorized"])

    def test_reject_missing_field(self):
        record = proposed_record()
        del record["reviewer_signature_or_attestation"]
        with self.assertRaises(ValueError):
            validate_proposed_review_fields(record)

    def test_reject_unknown_review_outcome(self):
        record = proposed_record()
        record["decision"] = "FULL_TRADING_APPROVAL"
        with self.assertRaises(ValueError):
            validate_proposed_review_fields(record)

    def test_refuse_implementation(self):
        with self.assertRaises(PermissionError):
            require_implementation_authorization()

    def test_json_serializable(self):
        r = request_package()
        self.assertEqual(json.loads(json.dumps(r, allow_nan=False)), r)


if __name__ == "__main__":
    unittest.main()
