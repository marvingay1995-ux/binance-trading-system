"""BTC-062: limited read-only local Docker image and security-policy evidence.

Allowed operations: 'docker image ls' and read-only 'docker info' formatted
queries. No pull/run/create/start/inspect of image contents or daemon writes.
Metadata alone CANNOT authenticate a local image or approve execution.
"""
import json
import os
import shutil
import subprocess

from .synthetic_docker_isolation_contract import contract_record
from .synthetic_docker_readiness_decision import readiness_decision
from .verifier_implementation_decision import decision_record as historical_decision

PROGRAM = "BTC-062-v1"
REVIEWED_MAIN_SHA = "bfa607297da05d014b688c2bb0c411703867815c"
REVIEWED_MAIN_CI = 45173805165
REVIEWED_MAIN_TESTS = 384
TIMEOUT_SECONDS = 3
MAX_OUTPUT_CHARS = 65536

COMMANDS = {
    "images": ("image", "ls", "--no-trunc", "--digests", "--format", "{{json .}}"),
    "security_options": ("info", "--format", "{{json .SecurityOptions}}"),
    "os_type": ("info", "--format", "{{json .OSType}}"),
}

def _read_only_query(kind, *, which=None, runner=None):
    """Perform at most one fixed local-only CLI metadata query."""
    if kind not in COMMANDS:
        raise ValueError("COMMAND_NOT_ALLOWLISTED")
    if which is None:
        which = shutil.which
    if runner is None:
        runner = subprocess.run
    binary = which("docker")
    if not binary or not os.path.isabs(binary):
        return None, "DOCKER_CLI_UNAVAILABLE"
    # Pin to the local socket, discard remote contexts/config and credentials.
    env = {
        "PATH": os.defpath,
        "HOME": "/nonexistent",
        "DOCKER_CONFIG": "/nonexistent",
        "DOCKER_HOST": "unix:///var/run/docker.sock",
        "DOCKER_CONTEXT": "default",
    }
    try:
        p = runner(
            [binary, *COMMANDS[kind]], cwd="/", env=env,
            text=True, capture_output=True, timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, "READONLY_QUERY_TIMEOUT"
    except OSError:
        return None, "READONLY_QUERY_LAUNCH_ERROR"
    if p.returncode != 0:
        return None, "READONLY_QUERY_REJECTED"
    if not isinstance(p.stdout, str) or len(p.stdout) > MAX_OUTPUT_CHARS:
        return None, "READONLY_OUTPUT_EXCEEDED"
    return p.stdout, "METADATA_RETURNED"


def _image_metadata(raw):
    if raw is None:
        return {
            "inventory_observed": False, "local_image_count": None,
            "images_with_digest_count": None, "trusted_image_selected": False,
            "trusted_image_digest_verified": False,
        }
    rows = [line for line in raw.splitlines() if line.strip()]
    if len(rows) > 1000:
        return {
            "inventory_observed": False, "local_image_count": None,
            "images_with_digest_count": None, "trusted_image_selected": False,
            "trusted_image_digest_verified": False,
        }
    digest_count = 0
    for line in rows:
        try:
            record = json.loads(line)
        except (ValueError, TypeError):
            return _image_metadata(None)
        if not isinstance(record, dict):
            return _image_metadata(None)
        digest = record.get("Digest")
        if isinstance(digest, str) and digest.startswith("sha256:") and len(digest) == 71:
            try:
                int(digest[7:], 16)
            except ValueError:
                continue
            digest_count += 1
    return {
        "inventory_observed": True,
        "local_image_count": len(rows),
        "images_with_digest_count": digest_count,
        # Registry digest is NOT a signed provenance or local executable approval.
        "trusted_image_selected": False,
        "trusted_image_digest_verified": False,
    }


def _security_metadata(options_raw, os_raw):
    try:
        options = json.loads(options_raw) if options_raw is not None else None
        os_type = json.loads(os_raw) if os_raw is not None else None
    except (ValueError, TypeError):
        options, os_type = None, None
    if not isinstance(options, list) or any(not isinstance(s, str) for s in options):
        options = None
    if not isinstance(os_type, str):
        os_type = None
    # Hints only, never an assertion of effective confinement.
    rootless_hint = None if options is None else any(
        item == "name=rootless" or item.startswith("name=rootless,")
        for item in options
    )
    return {
        "policy_metadata_observed": options is not None and os_type is not None,
        "reported_os_type": os_type if os_type in ("linux", "windows") else "UNKNOWN",
        "rootless_in_security_options": rootless_hint,
        "rootless_enforcement_verified": False,
        "no_network_enforcement_verified": False,
        "readonly_mount_enforcement_verified": False,
        "host_privilege_boundary_verified": False,
    }


def review_local_metadata(*, query=None):
    """Inventory is explicitly not a Docker execution-readiness gate."""
    prior = historical_decision()
    current = contract_record()
    readiness = readiness_decision()
    if prior["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(prior["permissions"].values()):
        raise PermissionError("HISTORICAL_NO_GO_CHANGED")
    if current["docker_execution_authorized"] is not False or readiness["docker_run_allowed"] is not False:
        raise PermissionError("DOCKER_EXECUTION_GATE_CHANGED")
    if query is None:
        query = _read_only_query
    outputs = {}
    reasons = {}
    for name in COMMANDS:
        output, reason = query(name)
        outputs[name] = output
        reasons[name] = reason
    images = _image_metadata(outputs["images"])
    security = _security_metadata(outputs["security_options"], outputs["os_type"])
    return {
        "program": PROGRAM,
        "reviewed_main_sha": REVIEWED_MAIN_SHA,
        "reviewed_main_ci_run": REVIEWED_MAIN_CI,
        "reviewed_main_tests": REVIEWED_MAIN_TESTS,
        "read_only_query_reasons": reasons,
        "image_metadata": images,
        "runtime_security_metadata": security,
        "decision": "NO_GO_DOCKER_EXECUTION_IMAGE_TRUST_AND_ENFORCEMENT_UNVERIFIED",
        "trusted_local_image": None,
        "docker_execution_authorized": False,
        "sandbox_security_verified": False,
        "real_market_data_authorized": False,
        "h01_backtesting_authorized": False,
        "trading_authorized": False,
    }

def require_docker_experiment(*_args, **_kwargs):
    raise PermissionError("BTC062_EXECUTION_AUTHORIZATION_WITHHELD")

if __name__ == "__main__":
    print("BTC062_ACTUAL_IMAGE_POLICY_EVIDENCE=" +
          json.dumps(review_local_metadata(), sort_keys=True, separators=(",", ":")))
