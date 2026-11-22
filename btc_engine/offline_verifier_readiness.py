"""BTC-039: evidence-based offline verifier readiness decision; no I/O verifier."""
import hashlib
import json

from .verifier_implementation_decision import decision_record as previous_decision
from .synthetic_fixture_spec import contract_record as fixture_spec
from .synthetic_fixture_generator import fixture_bytes, LABEL
from .synthetic_fixture_coverage import coverage_report
from .synthetic_fixture_isolation import remaining_case_report

VERSION = "BTC-039-v1"
REVIEWED_MAIN_SHA = "da139ff65d447d804359a7c1c82ebdb2e6fb0efe"
REVIEWED_BTC038_BRANCH_SHA = "2d32328b96a43fda9d336dd70b7533c2b142acc9"

BLOCKERS = {
    "DEP-01": "BTC-037 PR #26 remains open against main; BTC-038 PR #27 merged only into BTC-037 feature branch; 225 passing branch tests are not a main-branch integration result.",
    "SAFE-01": "No local offline verifier exists; synthetic helper behavior does not demonstrate untrusted-input, file path, ZIP, CSV, SHA or provenance enforcement.",
    "SAFE-02": "Production-scale caps (25MB raw, 50MB expanded, 100000 rows, 30 seconds) have not been stress-tested with enforceable memory/time bounds.",
    "SAFE-03": "Atomic no-follow file open, same-byte hash/parse, symlink races, report creation and OS network isolation have not been proven.",
    "SAFE-04": "Publisher authenticity is not established by a local SHA256, a plausible URL or invented fixture metadata.",
    "GOV-01": "BTC-028 approval evidence remains missing; no separately attributable owner approval for the real-data verifier or independently authenticated security assessment has been supplied.",
}

CONDITIONS = {
    "C01": "Merge BTC-037 into main and verify all 225 current branch tests on the actual main revision; re-evaluate any merge conflicts or regressions.",
    "C02": "Specify the exact read-only verifier file list, allowed input root and immutable source SHA fingerprints, accepted parsing schema and output directory.",
    "C03": "Define controlled, measurable adversarial tests for raw/expanded bytes, compression ratio, record count, parser bounds, deadlines and memory ceilings.",
    "C04": "Define secure OS-specific input open/snapshot strategy, report no-overwrite semantics and independently verified runtime network restrictions.",
    "C05": "Require explicit owner authorization for the narrow verifier code implementation and separately record security-review limitations; never infer trading approval.",
}

DENIALS = {
    "offline_local_verifier_implementation": False,
    "real_market_data_ingestion": False,
    "publisher_authenticity_verified": False,
    "h01_signal_implementation": False,
    "h01_backtesting": False,
    "paper_trading": False,
    "live_trading": False,
    "binance_account_access": False,
}

def readiness_record():
    earlier = previous_decision()
    if earlier["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION":
        raise PermissionError("previous NO-GO decision changed")
    if any(earlier["permissions"].values()) or any(DENIALS.values()):
        raise PermissionError("unapproved capability found")
    parent = coverage_report()
    child = remaining_case_report()
    if len(parent["materialized_fixture_cases"]) != 12 or len(parent["context_only_unexecuted"]) != 6:
        raise ValueError("expected 12+6 synthetic coverage contract")
    if len(child["cases"]) != 6:
        raise ValueError("incomplete bounded probes")
    if child["security_verdict"] != "SYNTHETIC_HARNESS_CHECKS_ONLY_VERIFIER_NOT_IMPLEMENTED":
        raise ValueError("synthetic tests misrepresented")
    if len(fixture_bytes()) != 9:
        raise ValueError("baseline fixture inventory changed")
    spec = fixture_spec()
    canonical = json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return {
        "program": VERSION,
        "decision": "NO_GO_OFFLINE_VERIFIER_IMPLEMENTATION",
        "reviewed_main_sha": REVIEWED_MAIN_SHA,
        "reviewed_btc038_branch_sha": REVIEWED_BTC038_BRANCH_SHA,
        "btc034_spec_sha256": hashlib.sha256(canonical).hexdigest(),
        "evidence": {
            "btc037_pr26_main_merged": False,
            "btc038_pr27_merged_to_btc037_branch": True,
            "btc038_branch_ci_tests_passed": 225,
            "existing_generator_fixture_count": 9,
            "btc037_materialized_synthetic_scenarios": 12,
            "btc038_bounded_probe_scenarios": 6,
            "tested_against_real_verifier": False,
            "independent_security_certification": False,
            "data_source_authenticity_verified": False,
            "recorded_provenance": LABEL,
        },
        "blocking_findings": BLOCKERS,
        "reconsideration_conditions": CONDITIONS,
        "permissions": DENIALS,
        "interpretation": "Design and synthetic probe evidence only; no secure verifier implementation, real-data processing or trading permission.",
    }

def require_offline_verifier_implementation():
    raise PermissionError("BTC-039: offline local verifier implementation NO GO")
