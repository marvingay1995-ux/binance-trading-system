"""BTC-060 static Docker synthetic-isolation contract, NOT launch authorization.

No Docker commands are executed. No images, containers, or runtime changes.
"""
import json
from .verifier_implementation_decision import decision_record as historical_decision

PROGRAM = "BTC-060-v1"
MAIN_SHA = "d2655d8f822840e662c97544151c9dbd3a7bdbb3"
MAIN_RUN = 45170296024
MAIN_TESTS = 366
REQUIRED_DOCKER_FLAGS = (
    "--network=none",
    "--read-only",
    "--cap-drop=ALL",
    "--security-opt=no-new-privileges:true",
    "--pids-limit=32",
    "--memory=256m",
    "--cpus=1",
    "--user=65534:65534",
)
REQUIRED_RUNTIME_EVIDENCE = (
    "explicit owner authorization for one disposable synthetic-only Docker experiment",
    "trusted locally available image identity and digest; no image pulls",
    "Docker daemon access scope, privilege/rootless assessment and runner identity",
    "verified IPv4/IPv6 egress denial without contacting a public endpoint",
    "read-only verified invented inputs and isolated writable output",
    "non-root uid/gid, zero added capabilities, no-new-privileges",
    "bounded CPU, memory, PID count and wall deadline with descendant cleanup",
    "actual negative-control logs for network, forbidden mounts and overwrite attempts",
    "runner and runtime versions, policy evidence, immutable CI commit and failure cleanup",
)
UNAPPROVED = (
    "actual Docker run, create, start, exec, build, pull, image download or VM provisioning",
    "privileged mode, host network, host PID namespace, broad filesystem mounts",
    "remote Docker endpoints, new secrets or paid infrastructure",
    "real or arbitrary Binance files, Binance account/API/credentials",
    "H01 strategies, backtesting, paper/testnet/live orders or automated trading",
)

def contract_record():
    old = historical_decision()
    if old["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(old["permissions"].values()):
        raise PermissionError("BTC028_HISTORIC_NO_GO_CHANGED")
    return {
        "program": PROGRAM,
        "baseline_main_sha": MAIN_SHA,
        "baseline_main_ci_run": MAIN_RUN,
        "baseline_main_tests": MAIN_TESTS,
        "observed_btc059_docker": "LOCAL_ENGINE_RESPONDED_VERSION_METADATA_ONLY",
        "observed_btc059_podman": "UNAVAILABLE_VERSION_QUERY_REJECTED",
        "decision": "EXECUTION_AUTHORIZATION_WITHHELD_SYNTHETIC_CONTRACT_DEFINED",
        "docker_execution_authorized": False,
        "sandbox_security_verified": False,
        "real_market_data_authorized": False,
        "trading_authorized": False,
        "docker_run_allowed": False,
        "proposed_future_flags_not_executable": list(REQUIRED_DOCKER_FLAGS),
        "required_before_separate_execution_approval": list(REQUIRED_RUNTIME_EVIDENCE),
        "prohibited": list(UNAPPROVED),
        "future_acceptance_rule": "FAIL_CLOSED_UNLESS_ALL_INDEPENDENT_OS_CONTROLS_VERIFIED",
        "next_step": "Record image/runtime policy and explicit scope approval before a separate synthetic-only Docker experiment; no container launch in BTC-060.",
    }

def authorize_docker_execution(*_args, **_kwargs):
    raise PermissionError("BTC060_DOCKER_EXECUTION_NOT_AUTHORIZED")

if __name__ == "__main__":
    print(json.dumps(contract_record(), sort_keys=True, indent=2))
