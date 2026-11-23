"""BTC-059 bounded read-only local container runtime access probe.

No images, containers, networks, daemon modifications, or credentials.
Uses only local CLI version metadata, never remote endpoints, shell, or info
commands that may initialize storage. A responding engine is not a sandbox.
"""
import json
import os
import shutil
import subprocess
import sys

VERSION = "BTC-059-v1"
COMMANDS = {
    "podman": ("version", "--format", "json"),
    "docker": ("version", "--format", "{{json .Server}}"),
}
TIMEOUT_SECONDS = 3
MAX_STDOUT = 16000

def _record(name, status, reason):
    return {"runtime": name, "status": status, "reason": reason,
            "local_engine_metadata_observed": status == "LOCAL_ENGINE_RESPONDED",
            "rootless_verified": False,
            "network_none_verified": False,
            "filesystem_confinement_verified": False,
            "os_isolation_verified": False,
            "container_launch_authorized": False}

def _parse(name, content):
    if not content or len(content) > MAX_STDOUT:
        return _record(name, "UNAVAILABLE", "OUTPUT_MISSING_OR_TOO_LARGE")
    try:
        data = json.loads(content)
    except (ValueError, TypeError):
        return _record(name, "UNAVAILABLE", "INVALID_VERSION_JSON")
    if not isinstance(data, dict):
        return _record(name, "UNAVAILABLE", "INVALID_VERSION_JSON")
    if name == "docker":
        # .Server may serialize null when daemon is unreachable.
        if not isinstance(data.get("Version"), str) or not data["Version"]:
            return _record(name, "UNAVAILABLE", "SERVER_VERSION_NOT_PRESENT")
    else:
        # Podman version data is not proof that a rootless engine can launch.
        if not isinstance(data.get("Client"), dict) and not isinstance(data.get("Version"), str):
            return _record(name, "UNAVAILABLE", "PODMAN_VERSION_NOT_PRESENT")
    return _record(name, "LOCAL_ENGINE_RESPONDED", "VERSION_METADATA_ONLY")

def probe_local_runtime(name, *, which=None, runner=None, timeout=TIMEOUT_SECONDS):
    if name not in COMMANDS or not isinstance(name, str):
        raise ValueError("UNSUPPORTED_RUNTIME")
    if type(timeout) not in (int, float) or not 0 < timeout <= TIMEOUT_SECONDS:
        raise ValueError("INVALID_TIMEOUT")
    if which is None:
        which = shutil.which
    if runner is None:
        runner = subprocess.run
    binary = which(name)
    if not binary:
        return _record(name, "UNAVAILABLE", "CLI_NOT_FOUND")
    # Reject remote endpoint configuration, including inherited context env.
    # Restrict to local runtime executable, no shell and no image operations.
    env = {"PATH": os.defpath, "HOME": "/nonexistent",
           "DOCKER_HOST": "unix:///var/run/docker.sock",
           "CONTAINER_HOST": "unix:///dev/null",
           "XDG_RUNTIME_DIR": "/nonexistent"}
    try:
        result = runner(
            [binary, *COMMANDS[name]], cwd="/", env=env,
            text=True, capture_output=True, timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _record(name, "UNAVAILABLE", "VERSION_QUERY_TIMEOUT")
    except OSError:
        return _record(name, "UNAVAILABLE", "VERSION_QUERY_LAUNCH_ERROR")
    if result.returncode != 0:
        return _record(name, "UNAVAILABLE", "VERSION_QUERY_REJECTED")
    return _parse(name, result.stdout)

def inventory_runtime_access():
    records = {name: probe_local_runtime(name) for name in COMMANDS}
    return {
        "program": VERSION,
        "baseline": "BTC-058 PR #48 dependent review",
        "runtimes": records,
        "selected_verified_sandbox": None,
        "os_network_isolation_verified": False,
        "real_data_authorized": False,
        "trading_authorized": False,
        "decision": "NO_GO_SANDBOX_ENFORCEMENT_NOT_VERIFIED",
    }

def require_sandbox():
    raise PermissionError("BTC-059: local CLI version access is not sandbox enforcement")

if __name__ == "__main__":
    print("BTC059_ACTUAL_RUNTIME_ACCESS=" +
          json.dumps(inventory_runtime_access(), sort_keys=True, separators=(",",":")))
