"""BTC-056 kernel network-route denial experiment in an unprivileged child.

Only TEST-NET-2 198.51.100.1 is used. Before a connect attempt, child must
prove distinct netns, only loopback interface and no non-loopback routes.
If any precondition is unmet it DOES NOT open a socket. This is NOT a sandbox.
"""
import errno
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

VERSION = "BTC-056-v1"
TIMEOUT = 4

# The child has no imports of exchange, trading, or market-data modules.
CHILD = r'''
import errno, json, os, resource, socket, sys
from pathlib import Path
parent = sys.argv[1]
own = os.readlink("/proc/self/ns/net")
interfaces = sorted(p.name for p in Path("/sys/class/net").iterdir())
routing = Path("/proc/net/route").read_text(encoding="ascii").splitlines()[1:]
external_routes = [line for line in routing if line.split() and line.split()[0] != "lo"]
# Only test connectivity after strict safe preflight, to guarantee no external
# traffic even if namespace creation silently did not isolate networking.
safe = own != parent and own.startswith("net:[") and interfaces == ["lo"] and not external_routes
if not safe:
    print(json.dumps({"status":"PRECONDITION_FAILED","distinct":own != parent,
                      "only_loopback":interfaces == ["lo"],"routes_absent":not external_routes}))
    sys.exit(0)
# Resource limits are OS-enforced in this child; they do not deny filesystem.
resource.setrlimit(resource.RLIMIT_CORE, (0,0))
resource.setrlimit(resource.RLIMIT_CPU, (3,3))
resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.4)
    code = sock.connect_ex(("198.51.100.1", 9))
soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
memsoft, memhard = resource.getrlimit(resource.RLIMIT_AS)
print(json.dumps({"status":"CHECKED","distinct":True,"only_loopback":True,
                  "routes_absent":True,"connect_errno":code,
                  "cpu_cap":soft==3 and hard==3,
                  "memory_cap":memsoft==256*1024*1024 and memhard==256*1024*1024}))
'''

def _no(reason):
    return {
        "program": VERSION, "status": "ENFORCEMENT_UNAVAILABLE",
        "reason": reason, "kernel_egress_denial_observed": False,
        "cpu_memory_limits_observed": False,
        "filesystem_isolation_verified": False,
        "comprehensive_network_isolation_verified": False,
        "security_certified": False, "real_data_authorized": False,
        "trading_authorized": False,
    }

def verify_unprivileged_enforcement(*, timeout=TIMEOUT):
    """One controlled kernel route-denial experiment, no privileges/downloads."""
    if type(timeout) not in (int,float) or not 0 < timeout <= TIMEOUT:
        raise ValueError("INVALID_TIMEOUT")
    if not sys.platform.startswith("linux") or not Path("/proc/self/ns/net").exists():
        return _no("UNSUPPORTED_PLATFORM")
    binary = shutil.which("unshare")
    if not binary:
        return _no("UNSHARE_UNAVAILABLE")
    try:
        parent = os.readlink("/proc/self/ns/net")
    except OSError:
        return _no("PARENT_NAMESPACE_UNREADABLE")
    argv = [binary, "--user", "--map-root-user", "--net", "--fork",
            sys.executable, "-I", "-S", "-c", CHILD, parent]
    try:
        result = subprocess.run(
            argv, cwd="/", env={"PYTHONDONTWRITEBYTECODE":"1"},
            capture_output=True, text=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return _no("CHILD_TIMEOUT")
    except OSError:
        return _no("CHILD_LAUNCH_FAILED")
    if result.returncode:
        return _no("UNPRIVILEGED_NAMESPACE_DENIED")
    try:
        obj = json.loads(result.stdout)
    except (ValueError,TypeError):
        return _no("INVALID_CHILD_EVIDENCE")
    if not isinstance(obj,dict):
        return _no("INVALID_CHILD_EVIDENCE")
    if obj.get("status") == "PRECONDITION_FAILED":
        return _no("SAFE_PREFLIGHT_FAILED")
    if (obj.get("status") != "CHECKED" or
        any(obj.get(k) is not True for k in ("distinct","only_loopback","routes_absent","cpu_cap","memory_cap")) or
        type(obj.get("connect_errno")) is not int or
        obj["connect_errno"] not in (errno.ENETUNREACH, errno.EHOSTUNREACH)):
        return _no("KERNEL_DENIAL_NOT_OBSERVED")
    return {
        "program": VERSION, "status": "LIMITED_KERNEL_DENIAL_OBSERVED",
        "reason": "DISTINCT_NETNS_ONLY_LOOPBACK_TEST_NET_UNREACHABLE",
        "kernel_egress_denial_observed": True,
        "cpu_memory_limits_observed": True,
        "filesystem_isolation_verified": False,
        "comprehensive_network_isolation_verified": False,
        "security_certified": False, "real_data_authorized": False,
        "trading_authorized": False,
    }
