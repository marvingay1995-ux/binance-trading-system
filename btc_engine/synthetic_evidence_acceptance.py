"""BTC-052: bounded synthetic evidence acceptance, without runtime activation.

This is an internal review record, not a general-file or trading permission.
BTC-051 must be merged to main before this review becomes integrated evidence.
"""
import json
from .verifier_implementation_decision import decision_record as historical_decision
from .synthetic_verifier_boundary_review import review_record as btc046_review

VERSION = "BTC-052-v1"
REVIEWED_MAIN_SHA = "bfee4cbd4e7b732297ce67a723710ea9d7859490"
BTC051_PR = 40
BTC051_CI_RUN = 45039910593
BTC051_BRANCH_TESTS = 305
BASELINE_MAIN_TESTS = 294
RISKS = {
    "R48-01": {
        "severity": "HIGH", "finding": "File path TOCTOU and hostile local root",
        "observed_reduction": "POSIX no-follow and controlled open-time symlink substitution tests",
        "remaining": "Uncontrolled concurrency and root-ancestor races unverified",
        "status": "OPEN_PARTIALLY_TESTED",
    },
    "R48-02": {
        "severity": "HIGH", "finding": "No OS-enforced network/process sandbox",
        "observed_reduction": "Child with Linux CPU/address-space limits and Python instrumentation",
        "remaining": "OS-level network denial and privilege isolation not implemented",
        "status": "OPEN",
    },
    "R48-03": {
        "severity": "HIGH", "finding": "General processing memory, time and ZIP limits",
        "observed_reduction": "Fixed 200KB golden fixtures, Linux CPU/AS limits and 5-second parent timeout",
        "remaining": "25MB/50MB/100000 records/30-second production limits not measured",
        "status": "OPEN",
    },
    "R48-04": {
        "severity": "HIGH", "finding": "Authentic market-data publisher provenance",
        "observed_reduction": "Known invented fixture SHA-256 integrity tests only",
        "remaining": "No authentic Binance provenance or real-data authorization",
        "status": "OPEN",
    },
    "R48-05": {
        "severity": "MEDIUM", "finding": "Report creation concurrency and partial writes",
        "observed_reduction": "Exclusive create and sentinel collision checks",
        "remaining": "Root confinement, atomic publish and partial-write recovery unverified",
        "status": "OPEN",
    },
    "R48-06": {
        "severity": "MEDIUM", "finding": "Unclassified I/O and subprocess failures",
        "observed_reduction": "BTC-051 fault injection for open/read/fstat EIO, timeout, launch failures and malformed child output",
        "remaining": "Disk faults, ENOSPC, output partial writes, arbitrary OS errors and resource exhaustion not fully covered",
        "status": "OPEN_PARTIALLY_TESTED",
    },
    "R48-07": {
        "severity": "MEDIUM", "finding": "Windows security parity",
        "observed_reduction": "No verified Windows platform tests",
        "remaining": "Windows dirfd/no-follow equivalent and resource enforcement unverified",
        "status": "OPEN",
    },
    "R48-08": {
        "severity": "MEDIUM", "finding": "Misstated public/parser coverage",
        "observed_reduction": "Tests distinguish public golden-hash allowlist from private CSV/ZIP parser probes",
        "remaining": "General external-file parser security untested and unauthorized",
        "status": "OPEN_WITH_SCOPE_CLARIFIED",
    },
}
PERMISSIONS = {
    "existing_synthetic_golden_fixture_verification": True,
    "synthetic_regression_testing": True,
    "arbitrary_csv_zip_verification": False,
    "real_binance_market_data": False,
    "publisher_authenticity_verified": False,
    "h01_signals_or_backtesting": False,
    "binance_api_or_credentials": False,
    "paper_or_testnet_orders": False,
    "live_or_automated_orders": False,
}
RESTRICTED_KEYS = tuple(k for k in PERMISSIONS if k not in (
    "existing_synthetic_golden_fixture_verification", "synthetic_regression_testing"
))

def evidence_acceptance_record():
    historical = historical_decision()
    review = btc046_review()
    if historical["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION":
        raise PermissionError("BTC-028 gate changed")
    if any(historical["permissions"].values()) or any(PERMISSIONS[k] for k in RESTRICTED_KEYS):
        raise PermissionError("unauthorized expanded verifier or trading permission")
    if review["decision"] != "SYNTHETIC_ONLY_EVIDENCE_ACCEPTED_REAL_DATA_BOUNDARY_NO_GO":
        raise PermissionError("BTC-046 boundary changed")
    return {
        "program": VERSION,
        "classification": "INTERNAL_AI_ASSISTED_REVIEW_NOT_INDEPENDENT_SECURITY_CERTIFICATION",
        "reviewed_main_sha": REVIEWED_MAIN_SHA,
        "btc051_pr": BTC051_PR,
        "btc051_branch_ci_run": BTC051_CI_RUN,
        "btc051_branch_tests_passed": BTC051_BRANCH_TESTS,
        "prior_merged_main_tests": BASELINE_MAIN_TESTS,
        "integration": {
            "btc050_on_main": True,
            "btc051_on_main_at_review": False,
            "btc052_on_main_at_review": False,
            "requires_merge_and_fresh_main_ci": True,
        },
        "decision": "CONDITIONAL_ACCEPT_SYNTHETIC_ONLY_EVIDENCE_REAL_DATA_NO_GO",
        "accepted": [
            "Existing frozen invented BTC-036 golden CSV/ZIP regression evidence",
            "BTC-050 controlled subprocess bounds and deterministic file-race cases",
            "BTC-051 mocked read/stat/open failures and child timeout/error paths on its passing branch",
        ],
        "not_accepted": [
            "OS-enforced network/privilege sandbox",
            "Hostile-file or real Binance market archive verification",
            "General ZIP/CSV processing resource certification",
            "Publisher authenticity or independent security signoff",
            "Paper, testnet, live or automated trading readiness",
        ],
        "risk_register": RISKS,
        "permissions": PERMISSIONS,
        "next_controlled_work": "Merge BTC-051 then BTC-052 to main; record exact main CI and remediate remaining synthetic-only P0 risks before any new scope decision.",
    }

def require_real_data_or_trading():
    raise PermissionError("BTC-052: real market-data verification and trading NO GO")

if __name__ == "__main__":
    print(json.dumps(evidence_acceptance_record(), sort_keys=True, indent=2, allow_nan=False))
