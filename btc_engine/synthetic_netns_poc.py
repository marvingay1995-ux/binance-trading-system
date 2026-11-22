"""BTC-055 unprivileged Linux network namespace observation; no network traffic."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

CHILD = """
import json, os
from pathlib import Path
routes = Path('/proc/net/route').read_text().splitlines()
nonloop = sum(1 for row in routes[1:] if row.split() and row.split()[0] != 'lo')
print(json.dumps({'ns': os.readlink('/proc/self/ns/net'), 'nonloop_routes':nonloop, 'real_data':False, 'trading':False}))
"""

def unavailable(reason):
    return {"status":"ISOLATION_UNAVAILABLE","reason":reason,
            "os_network_isolation_verified":False,"real_data_authorized":False,
            "trading_authorized":False,"security_certified":False}

def probe_unprivileged_netns(timeout=4):
    if type(timeout) not in (int,float) or not 0 < timeout <= 4:
        raise ValueError("INVALID_PROBE_TIMEOUT")
    if not sys.platform.startswith("linux") or not Path("/proc/self/ns/net").exists():
        return unavailable("UNSUPPORTED_PLATFORM")
    binary = shutil.which("unshare")
    if not binary:
        return unavailable("UNSHARE_NOT_INSTALLED")
    try:
        parent = os.readlink("/proc/self/ns/net")
    except OSError:
        return unavailable("PARENT_NS_UNREADABLE")
    cmd = [binary,"--user","--map-root-user","--net","--fork",
           sys.executable,"-I","-S","-c",CHILD]
    try:
        p = subprocess.run(cmd,cwd="/",env={"PYTHONDONTWRITEBYTECODE":"1"},
                           capture_output=True,text=True,timeout=timeout,check=False)
    except subprocess.TimeoutExpired:
        return unavailable("PROBE_TIMEOUT")
    except OSError:
        return unavailable("PROBE_LAUNCH_ERROR")
    if p.returncode != 0:
        return unavailable("NAMESPACE_CREATION_DENIED")
    try:
        child = json.loads(p.stdout)
    except (ValueError,TypeError):
        return unavailable("INVALID_EVIDENCE")
    if (not isinstance(child,dict) or not isinstance(child.get("ns"),str)
        or not child["ns"].startswith("net:[") or child["ns"] == parent
        or type(child.get("nonloop_routes")) is not int or child["nonloop_routes"] != 0
        or child.get("real_data") is not False or child.get("trading") is not False):
        return unavailable("ISOLATION_EVIDENCE_INSUFFICIENT")
    return {"status":"UNPRIVILEGED_NETNS_OBSERVED","reason":"DISTINCT_NS_NO_NONLOOPBACK_ROUTES",
            "os_network_isolation_verified":False,"real_data_authorized":False,
            "trading_authorized":False,"security_certified":False}
