"""BTC-054: non-activating isolation feasibility and integrated-evidence review.

Decisions are conservative snapshots; no sandbox or market-data pipeline is
created here. BTC-052/053 must be merged to main via PR #43 and retested.
"""
from .verifier_implementation_decision import decision_record as btc028
from .synthetic_evidence_acceptance import evidence_acceptance_record as btc052

VERSION = "BTC-054-v1"
REVIEWED_MAIN_SHA = "3558a4cc13b27cd576bb32272d9f9e1616b39fc9"
BTC051_MAIN_CI_RUN = 45040665467
BTC051_MAIN_TESTS = 305
BTC052_053_BRANCH_SHA = "d600a4ccffaedddfdf3fd01f266ce6554bbb6257"
BTC052_053_BRANCH_CI_RUN = 45040695110
BTC052_053_BRANCH_TESTS = 318

FEASIBILITY = {
    "existing_python_instrumentation": {
        "classification": "TEST_INSTRUMENTATION_ONLY",
        "verified_os_network_denial": False,
        "rejected_for_hostile_files": True,
    },
    "existing_linux_rlimits": {
        "classification": "LIMITED_CHILD_CPU_AND_VIRTUAL_MEMORY_CAPS",
        "verified_os_network_denial": False,
        "rejected_for_hostile_files": True,
    },
    "linux_user_network_mount_namespaces": {
        "classification": "CANDIDATE_NOT_IMPLEMENTED",
        "verified_os_network_denial": False,
        "requirements": "Dedicated disposable runner, prevalidated userns/netns support, disabled external networking, rootless and constrained filesystem, independently tested denial; unprivileged namespaces may be unavailable",
    },
    "rootless_container_no_network": {
        "classification": "CANDIDATE_NOT_IMPLEMENTED",
        "verified_os_network_denial": False,
        "requirements": "Verified runtime and policy with network none, read-only mounts, dropped capabilities, no new privileges, memory/CPU/PID ceilings and negative tests; image provenance and runtime access not authorized",
    },
    "windows_restricted_process": {
        "classification": "CANDIDATE_NOT_IMPLEMENTED",
        "verified_os_network_denial": False,
        "requirements": "Restricted token / job object and firewall controls with independent platform-specific negative tests; not equivalent to Linux dirfd/namespace model",
    },
}
OPEN_RISKS = (
    "Hostile ancestor / directory rename races and output ownership assumptions",
    "Kernel-enforced network-denial and process/privilege restrictions absent",
    "Production-scale streaming, memory and deadline ceilings unmeasured",
    "Real publisher provenance and independent human security review absent",
    "POSIX report staging lacks independently validated crash durability and Windows parity",
    "General CSV/ZIP parser and real-exchange data remain entirely unauthorized",
)
PERMISSIONS = {
    "known_invented_fixture_validation": True,
    "synthetic_only_test_research": True,
    "os_sandbox_deployment": False,
    "arbitrary_market_file_verifier": False,
    "real_market_data_ingestion": False,
    "publisher_authenticity_assertion": False,
    "h01_signal_or_backtest": False,
    "binance_api_or_credentials": False,
    "paper_testnet_live_orders": False,
}
RESTRICTED = tuple(k for k in PERMISSIONS if k not in (
    "known_invented_fixture_validation", "synthetic_only_test_research"
))

def decision_record():
    a = btc028()
    b = btc052()
    if a["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(a["permissions"].values()):
        raise PermissionError("BTC-028 historic boundary changed")
    if b["decision"] != "CONDITIONAL_ACCEPT_SYNTHETIC_ONLY_EVIDENCE_REAL_DATA_NO_GO":
        raise PermissionError("BTC-052 boundary changed")
    if any(PERMISSIONS[k] for k in RESTRICTED) or any(v["verified_os_network_denial"] for v in FEASIBILITY.values()):
        raise PermissionError("BTC-054 cannot authorize real-data or assert isolation")
    return {
        "program": VERSION,
        "classification": "INTERNAL_AI_ASSISTED_TECHNICAL_FEASIBILITY_NOT_INDEPENDENT_SECURITY_CERTIFICATION",
        "decision": "SYNTHETIC_ONLY_ACCEPTED_OS_ISOLATION_NOT_DEMONSTRATED_REAL_DATA_NO_GO",
        "integrated_evidence": {
            "reviewed_main_sha": REVIEWED_MAIN_SHA,
            "main_ci_run": BTC051_MAIN_CI_RUN,
            "main_tests_passed": BTC051_MAIN_TESTS,
            "btc052_053_feature_sha": BTC052_053_BRANCH_SHA,
            "feature_ci_run": BTC052_053_BRANCH_CI_RUN,
            "feature_tests_passed": BTC052_053_BRANCH_TESTS,
            "btc052_053_on_main_at_review": False,
            "integration_pr": 43,
            "merge_and_fresh_main_ci_required": True,
        },
        "feasibility": FEASIBILITY,
        "open_risks": list(OPEN_RISKS),
        "permissions": PERMISSIONS,
        "next_step": "Merge PR #43 and verify main CI, then integrate BTC-054 and review a separately scoped synthetic-only OS isolation spike without real market data.",
    }

def require_market_data_or_trading():
    raise PermissionError("BTC-054: real data, strategy and orders remain NO GO")
