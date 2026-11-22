"""BTC-057 bounded isolation environment strategy and fail-closed selection.

This is a policy/evidence planner, NOT a sandbox implementation. No host
probes, privileged operations, real market files, exchange APIs, or orders.
"""
from .verifier_implementation_decision import decision_record as historical_decision

PROGRAM = "BTC-057-v1"
REVIEWED_MAIN = "f65da28e6cbe5c988971588d7c8a2d7b4a0d733b"
CI_RUN = 45046604431
MAIN_TESTS = 342
OBSERVED = {
    "environment": "CURRENT_GITHUB_ACTIONS_RUNNER",
    "btc056_reason": "UNPRIVILEGED_NAMESPACE_DENIED",
    "kernel_egress_denial_observed": False,
    "os_network_isolation_verified": False,
    "filesystem_isolation_verified": False,
    "security_certified": False,
}
CANDIDATES = {
    "current_github_host_unshare": {
        "feasibility": "REJECT_FOR_NEXT_PROOF",
        "reason": "BTC-056 live probe denied unprivileged namespace creation",
        "requires_paid_or_privileged_changes": False,
    },
    "dedicated_rootless_container": {
        "feasibility": "CANDIDATE_UNVERIFIED",
        "reason": "Requires preinstalled, authorized rootless runtime, network-none, readonly mounts, dropped capabilities, no-new-privileges, non-root uid and PID/CPU/memory limits",
        "requires_paid_or_privileged_changes": False,
    },
    "disposable_linux_vm": {
        "feasibility": "CANDIDATE_UNVERIFIED",
        "reason": "Would need existing authorized disposable VM, host-enforced egress denial and filesystem boundary; provisioning or spend not approved",
        "requires_paid_or_privileged_changes": None,
    },
    "existing_ci_linux_with_restricted_container": {
        "feasibility": "CANDIDATE_UNVERIFIED",
        "reason": "CI might support container jobs but capability, runner trust and policy enforcement not checked; no Docker invocation authorized here",
        "requires_paid_or_privileged_changes": None,
    },
}
REQUIRED_CONTROLS = (
    "Network egress denied by OS/runtime policy, including IPv4 and IPv6; prove with closed-world tests without outbound requests",
    "Only frozen synthetic files mounted read-only under trusted root; deny access to unrelated paths and credentials",
    "Run as non-root with dropped capabilities, no-new-privileges and restrictive process/PID policy",
    "Enforce CPU, address-space/memory, wall-time and process limits; verify exit and descendant cleanup",
    "Write reports to dedicated confined output with collision refusal and failure cleanup",
    "Collect immutable runner/runtime versions, policy configuration and actual positive/negative CI verdicts",
)
FORBIDDEN = (
    "Binance API, real-market data or exchange credentials",
    "H01 strategies, indicators, backtesting and signal generation",
    "Paper/testnet/live orders, automated trading or account actions",
    "Privileged CI flags, paid provisioning, new secrets or production deployment",
)
PERMISSIONS = {
    "synthetic_policy_and_test_design": True,
    "offline_synthetic_runtime_capability_research": True,
    "real_data_ingestion": False,
    "os_sandbox_declared_secure": False,
    "container_or_vm_provisioning": False,
    "privileged_runner_changes": False,
    "h01_research_or_backtest": False,
    "binance_account_access": False,
    "trading_orders": False,
}


def choose_environment(evidence=None):
    """Never infer suitability from a name or mocked network-denial result."""
    if evidence is None:
        evidence = {}
    if not isinstance(evidence, dict):
        raise ValueError("INVALID_EVIDENCE")
    historical = historical_decision()
    if historical["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(historical["permissions"].values()):
        raise PermissionError("HISTORICAL_GATE_CHANGED")
    if any(v for k,v in PERMISSIONS.items() if k not in
           ("synthetic_policy_and_test_design", "offline_synthetic_runtime_capability_research")):
        raise PermissionError("UNAUTHORIZED_SCOPE")
    # This program records requirements, not a proof of actual host controls.
    return {
        "program": PROGRAM,
        "reviewed_main": REVIEWED_MAIN,
        "merged_main_ci_run": CI_RUN,
        "merged_main_tests": MAIN_TESTS,
        "observed_runner": OBSERVED,
        "decision": "NO_GO_OS_ISOLATION_ENFORCEMENT_CURRENT_RUNNER",
        "environment_selected": None,
        "candidates": CANDIDATES,
        "required_controls": list(REQUIRED_CONTROLS),
        "forbidden": list(FORBIDDEN),
        "additional_evidence_supplied_but_not_authenticated": bool(evidence),
        "verified_full_isolation": False,
        "real_data_authorized": False,
        "trading_authorized": False,
        "permissions": PERMISSIONS,
        "next_action": "Inventory already authorized disposable runtimes before separately approving a synthetic-only enforcement experiment",
    }


def require_verified_isolation_or_real_data():
    raise PermissionError("BTC-057: OS isolation not verified; real data and trading NO GO")
