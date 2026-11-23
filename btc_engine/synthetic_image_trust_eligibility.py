"""BTC-063 local-image trust and synthetic-execution eligibility decision.

This module intentionally does not contact Docker. Inventory counts and an
image digest are neither provenance nor permission to run an image.
"""
import json
from .synthetic_docker_image_policy_evidence import review_local_metadata
from .synthetic_docker_isolation_contract import contract_record
from .verifier_implementation_decision import decision_record as historical_decision

VERSION = "BTC-063-v1"
REVIEWED_MAIN_SHA = "5af349e552385e1a90c79c59c3e71b83e6f63932"
MAIN_CI_RUN = 45174429505
MAIN_TESTS = 394
CI_OBSERVATION = {
    "local_image_count": 6,
    "images_with_digest_count": 6,
    "reported_os_type": "linux",
    "rootless_in_security_options": False,
    "metadata_only": True,
}
EVIDENCE_REQUIREMENTS = (
    "locally_present_image_id_and_architecture",
    "approved_digest_against_independent_trusted_source",
    "approved_image_maintainer_and_origin",
    "image_configuration_and_nonroot_compatibility",
    "read_only_synthetic_fixture_mount_contract",
    "daemon_authority_and_privilege_boundary",
    "isolated_ipv4_ipv6_negative_controls",
    "resource_and_filesystem_negative_controls",
    "explicit_owner_approval_for_one_synthetic_experiment",
)
REVIEW_STATES = frozenset(("MISSING", "UNVERIFIED", "REJECTED", "INDEPENDENTLY_REVIEWED"))
NO_GO_SCOPES = (
    "docker execution, image pull, container creation or privileged CI changes",
    "real Binance files or API/credentials",
    "H01 backtests, paper/testnet/live trading and automated orders",
)

def assess_image_eligibility(evidence=None):
    """Accept only review-status annotations; never promote them to authority."""
    if evidence is None:
        evidence = {}
    if not isinstance(evidence, dict) or set(evidence).difference(EVIDENCE_REQUIREMENTS):
        raise ValueError("INVALID_IMAGE_REVIEW_EVIDENCE")
    if any(value not in REVIEW_STATES for value in evidence.values()):
        raise ValueError("INVALID_IMAGE_REVIEW_STATE")
    old = historical_decision()
    contract = contract_record()
    if old["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(old["permissions"].values()):
        raise PermissionError("BTC028_HISTORICAL_GATE_CHANGED")
    if contract["docker_execution_authorized"] is not False:
        raise PermissionError("BTC060_EXECUTION_DENIAL_CHANGED")
    statuses = {key: evidence.get(key, "MISSING") for key in EVIDENCE_REQUIREMENTS}
    claimed = sum(status == "INDEPENDENTLY_REVIEWED" for status in statuses.values())
    # Caller-supplied labels are UNAUTHENTICATED; even all-reviewed labels
    # cannot authorize a Docker launch or establish trusted provenance.
    return {
        "program": VERSION,
        "reviewed_main_sha": REVIEWED_MAIN_SHA,
        "reviewed_main_ci_run": MAIN_CI_RUN,
        "reviewed_main_tests": MAIN_TESTS,
        "last_verified_ci_observation": dict(CI_OBSERVATION),
        "evidence_requirements": statuses,
        "unverified_or_missing": [key for key, status in statuses.items()
                                  if status != "INDEPENDENTLY_REVIEWED"],
        "caller_claims_independently_reviewed_count": claimed,
        "caller_evidence_authenticated": False,
        "selected_image": None,
        "image_trust_verified": False,
        "synthetic_execution_eligible": False,
        "docker_execution_authorized": False,
        "os_isolation_verified": False,
        "real_data_authorized": False,
        "h01_backtesting_authorized": False,
        "trading_authorized": False,
        "decision": "NO_GO_IMAGE_TRUST_UNVERIFIED_EXECUTION_INELIGIBLE",
        "prohibited": list(NO_GO_SCOPES),
        "recommended_next": "Consolidated trading-readiness review: identify minimum independent gates for read-only market data and supervised paper trading; do not equate image inventory with deployment readiness.",
    }

def require_execution(*_args, **_kwargs):
    raise PermissionError("BTC063_DOCKER_EXECUTION_NOT_AUTHORIZED")

if __name__ == "__main__":
    print(json.dumps(assess_image_eligibility(), sort_keys=True))
