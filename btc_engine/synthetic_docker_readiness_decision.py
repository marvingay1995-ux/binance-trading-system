"""BTC-061 static Docker contract verification and execution-readiness decision.

No Docker launch, daemon query, image lookup, process/network invocation,
credentials, trading, or external evidence authentication. Fail closed.
"""
import json

from .synthetic_docker_isolation_contract import (
    PROGRAM as CONTRACT_PROGRAM,
    REQUIRED_DOCKER_FLAGS,
    REQUIRED_RUNTIME_EVIDENCE,
    UNAPPROVED,
    contract_record,
)
from .verifier_implementation_decision import decision_record as btc028

VERSION = "BTC-061-v1"
MAIN_REVIEW_SHA = "d2655d8f822840e662c97544151c9dbd3a7bdbb3"
BASE_MAIN_TEST_COUNT = 366
BTC060_BRANCH_TEST_COUNT = 374
BTC060_BRANCH_CI_RUN = 45171490604
BTC060_PR = 50

MANDATORY_FLAGS = frozenset({
    "--network=none",
    "--read-only",
    "--cap-drop=ALL",
    "--security-opt=no-new-privileges:true",
    "--pids-limit=32",
    "--memory=256m",
    "--cpus=1",
    "--user=65534:65534",
})
PROHIBITED_FLAGS = frozenset({
    "--privileged", "--network=host", "--pid=host",
    "--cap-add=ALL", "--security-opt=no-new-privileges:false",
})
EVIDENCE_GATES = (
    "BTC060_MERGED_MAIN_AND_MAIN_CI",
    "EXPLICIT_SINGLE_SYNTHETIC_EXECUTION_APPROVAL",
    "TRUSTED_LOCAL_IMAGE_DIGEST",
    "DAEMON_AUTHORITY_AND_NONPRIVILEGED_CONTEXT",
    "NETWORK_IPV4_IPV6_DENIAL_EVIDENCE",
    "READ_ONLY_SYNTHETIC_INPUT_AND_SEPARATE_OUTPUT",
    "NONROOT_CAPABILITIES_AND_NO_NEW_PRIVILEGES",
    "RESOURCE_PROCESS_AND_TIMEOUT_ENFORCEMENT",
    "ACTUAL_NEGATIVE_CONTROL_RESULTS",
    "CLEANUP_AND_RUNTIME_AUDIT_EVIDENCE",
)
# Deliberately not caller-configurable: this is an assessment of *observed*
# verified evidence at the BTC-061 review snapshot, not an approval API.
OBSERVED_GATE_STATUS = {gate: False for gate in EVIDENCE_GATES}

def verify_static_contract():
    contract = contract_record()
    previous = btc028()
    if previous["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(previous["permissions"].values()):
        raise PermissionError("BTC028_HISTORICAL_GATE_CHANGED")
    flags = tuple(REQUIRED_DOCKER_FLAGS)
    if (len(flags) != len(set(flags)) or
            not MANDATORY_FLAGS.issubset(flags) or
            PROHIBITED_FLAGS.intersection(flags) or
            len(REQUIRED_RUNTIME_EVIDENCE) < 9 or
            not UNAPPROVED):
        raise PermissionError("BTC060_CONTRACT_INCOMPLETE_OR_UNSAFE")
    if (contract.get("program") != CONTRACT_PROGRAM or
            contract.get("decision") != "EXECUTION_AUTHORIZATION_WITHHELD_SYNTHETIC_CONTRACT_DEFINED" or
            contract.get("docker_execution_authorized") is not False or
            contract.get("docker_run_allowed") is not False or
            contract.get("sandbox_security_verified") is not False or
            contract.get("trading_authorized") is not False or
            contract.get("real_market_data_authorized") is not False):
        raise PermissionError("BTC060_CONTRACT_AUTHORITY_CHANGED")
    return {
        "static_contract_checks_passed": True,
        "mandatory_flags_present": True,
        "forbidden_flags_absent": True,
        "execution_denial_preserved": True,
        "contract_program": CONTRACT_PROGRAM,
    }

def readiness_decision():
    verification = verify_static_contract()
    missing = list(EVIDENCE_GATES)
    return {
        "program": VERSION,
        "snapshot_main_sha": MAIN_REVIEW_SHA,
        "snapshot_main_tests": BASE_MAIN_TEST_COUNT,
        "btc060_pr": BTC060_PR,
        "btc060_branch_ci_run": BTC060_BRANCH_CI_RUN,
        "btc060_branch_tests": BTC060_BRANCH_TEST_COUNT,
        "btc060_on_main_at_review": False,
        "verification": verification,
        "evidence_gate_status": dict(OBSERVED_GATE_STATUS),
        "missing_independently_verified_evidence": missing,
        "decision": "NO_GO_DOCKER_SYNTHETIC_EXECUTION_NOT_READY",
        "static_contract_accepted": True,
        "docker_execution_authorized": False,
        "docker_run_allowed": False,
        "sandbox_security_certified": False,
        "os_network_isolation_verified": False,
        "real_market_data_authorized": False,
        "h01_backtesting_authorized": False,
        "trading_authorized": False,
        "next_gate": "Merge BTC-060 to main and verify main CI, then merge BTC-061 after CI; any future Docker execution needs separate explicit approval, trusted local image and independently verified controls.",
    }

def require_execution_authorization(*_args, **_kwargs):
    raise PermissionError("BTC061_DOCKER_EXECUTION_NO_GO")

if __name__ == "__main__":
    print(json.dumps(readiness_decision(), indent=2, sort_keys=True, allow_nan=False))
