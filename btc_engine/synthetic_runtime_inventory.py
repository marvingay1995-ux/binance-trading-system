"""BTC-058 non-executing, synthetic-only runtime capability inventory.

No container launches, daemon queries, network probes, provisioning or privileges.
Executable presence is not availability or evidence of enforced isolation.
"""
import json
import os
from pathlib import Path
import platform
import shutil
from .verifier_implementation_decision import decision_record as historical_decision

PROGRAM = "BTC-058-v1"
BASELINE_MAIN = "12410dce113379a387891dcee0bc8c8bd2c23d4d"
BASELINE_RUN = 45046974338
BASELINE_TESTS = 349
TOOLS = ("podman", "docker", "nerdctl", "unshare", "bwrap", "firejail")
REQUIRED = (
    "dedicated disposable execution environment with authorization",
    "kernel-enforced IPv4 and IPv6 network-denial proof",
    "read-only frozen synthetic inputs; separate confined output",
    "non-root identity and minimal capabilities; no-new-privileges",
    "CPU/memory/PID/wall-time limits and descendant cleanup",
    "negative-control evidence of denied forbidden actions",
)
FORBIDDEN = (
    "real market data or arbitrary external CSV/ZIP",
    "Binance API/account credentials or network requests",
    "H01 signals/backtests, simulated/live orders and trading",
    "container launch, VM provisioning, image download, privileges or spending",
)

def collect_read_only_capabilities(*, which=None, system=None):
    """Filesystem/PATH metadata only; no subprocess or daemon contact."""
    if which is None:
        which = shutil.which
    if system is None:
        system = platform.system()
    if not isinstance(system, str) or not system:
        raise ValueError("INVALID_PLATFORM")
    presence = {tool: bool(which(tool)) for tool in TOOLS}
    return {
        "platform": system,
        "cli_present": presence,
        "namespace_poc_previous_runner": "UNPRIVILEGED_NAMESPACE_DENIED",
        "runtime_daemon_access_checked": False,
        "rootless_execution_verified": False,
        "container_network_none_verified": False,
        "vm_isolation_verified": False,
        "security_certified": False,
        "no_subprocess_or_network_probe_performed": True,
    }

def selection_record(capabilities):
    """Selection is a *future evaluation target*, never an executable sandbox."""
    if not isinstance(capabilities, dict) or not isinstance(capabilities.get("cli_present"), dict):
        raise ValueError("INVALID_CAPABILITY_RECORD")
    presence = capabilities["cli_present"]
    if set(presence) != set(TOOLS) or any(type(v) is not bool for v in presence.values()):
        raise ValueError("INVALID_CAPABILITY_RECORD")
    historic = historical_decision()
    if historic["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(historic["permissions"].values()):
        raise PermissionError("HISTORICAL_NO_GO_CHANGED")
    if capabilities.get("security_certified") is True:
        raise ValueError("UNSUPPORTED_SECURITY_CLAIM")
    # Presence is only a clue for possible follow-up, not proof of a usable runtime.
    target = "podman" if presence["podman"] else ("docker" if presence["docker"] else
             ("nerdctl" if presence["nerdctl"] else None))
    return {
        "program": PROGRAM,
        "baseline_main_sha": BASELINE_MAIN,
        "baseline_ci_run": BASELINE_RUN,
        "baseline_tests_passed": BASELINE_TESTS,
        "capabilities": capabilities,
        "decision": "NO_GO_ISOLATION_ENVIRONMENT_SELECTION_UNVERIFIED",
        "selected_verified_runtime": None,
        "candidate_to_evaluate_next": target,
        "candidate_selection_is_not_authorization": True,
        "runtime_enforcement_verified": False,
        "required_before_any_synthetic_runtime_spike": list(REQUIRED),
        "prohibited": list(FORBIDDEN),
        "real_market_data_authorized": False,
        "trading_authorized": False,
    }

def inventory_record():
    return selection_record(collect_read_only_capabilities())

def require_runtime_enforcement():
    raise PermissionError("BTC-058: no executable isolation environment selected or verified")

if __name__ == "__main__":
    print("BTC058_CAPABILITY_INVENTORY=" +
          json.dumps(inventory_record(), sort_keys=True, separators=(",",":"), allow_nan=False))
