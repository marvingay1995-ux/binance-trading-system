"""BTC-050 bounded subprocess probe for *known invented fixtures only*.

The external timeout/CPU and address-space caps are real process limits on
Linux; the socket guard is *only Python instrumentation*, not OS network
isolation. This is not a sandbox for hostile files.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

PROBE_VERSION = "BTC-050-v1"
TIMEOUT_SECONDS = 5
MEMORY_LIMIT_BYTES = 256 * 1024 * 1024
CPU_LIMIT_SECONDS = 4
ALLOWED_FILES = frozenset({"golden.csv", "golden.zip"})

_CHILD = r'''
import json
from pathlib import Path
import socket
import subprocess
import sys
def deny(*args, **kwargs):
    raise PermissionError("PYTHON_NETWORK_OR_CHILD_PROCESS_DENIED")
socket.socket = deny
socket.create_connection = deny
subprocess.Popen = deny
sys.path.insert(0, sys.argv[1])
from btc_engine.offline_fixture_verifier import verify_generated
result = verify_generated(sys.argv[2], sys.argv[3])
print(json.dumps({
    "status": result["status"],
    "publisher_provenance_verified": result["publisher_provenance_verified"],
    "real_market_data_verified": result["real_market_data_verified"],
    "trading_authorized": result["trading_authorized"],
    "python_network_instrumentation_only": True,
    "os_network_isolation_verified": False,
}, sort_keys=True))
'''

def _posix_resource_limits():
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_LIMIT_SECONDS, CPU_LIMIT_SECONDS))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def probe_generated(root, filename, *, timeout=TIMEOUT_SECONDS):
    """Spawn one bounded, instrumented subprocess, never accepting file URLs."""
    if filename not in ALLOWED_FILES or not isinstance(filename, str):
        raise ValueError("SYNTHETIC_FILE_NOT_ALLOWED")
    path = Path(root)
    if not path.is_absolute() or not path.is_dir() or path.is_symlink():
        raise ValueError("INPUT_OUTSIDE_ROOT")
    if timeout <= 0 or timeout > TIMEOUT_SECONDS:
        raise ValueError("INVALID_TIMEOUT")
    repo_root = Path(__file__).resolve().parent.parent
    # These environment variables are intentionally not inherited. This is
    # a hygiene measure, NOT a security boundary against a malicious child.
    env = {"PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
    args = [sys.executable, "-I", "-S", "-c", _CHILD, str(repo_root), str(path), filename]
    completed = subprocess.run(
        args,
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        preexec_fn=_posix_resource_limits if sys.platform.startswith("linux") else None,
    )
    if completed.returncode != 0:
        raise RuntimeError("SYNTHETIC_CHILD_FAILED")
    try:
        result = json.loads(completed.stdout)
    except (ValueError, TypeError):
        raise RuntimeError("SYNTHETIC_CHILD_OUTPUT_INVALID")
    if (
        result.get("status") != "SYNTHETIC_INTEGRITY_ONLY"
        or result.get("os_network_isolation_verified") is not False
        or result.get("trading_authorized") is not False
        or result.get("real_market_data_verified") is not False
    ):
        raise RuntimeError("SYNTHETIC_CHILD_OUTPUT_INVALID")
    return {
        "program": PROBE_VERSION,
        "fixture": filename,
        "result": result,
        "limits": {
            "timeout_seconds": timeout,
            "linux_cpu_seconds": CPU_LIMIT_SECONDS if sys.platform.startswith("linux") else None,
            "linux_address_space_bytes": MEMORY_LIMIT_BYTES if sys.platform.startswith("linux") else None,
        },
        "os_network_isolation_verified": False,
        "real_data_authorized": False,
    }
