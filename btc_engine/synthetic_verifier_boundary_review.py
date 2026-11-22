"""BTC-046 security evidence and real-data boundary review. No verifier execution."""
import hashlib
import json

from .verifier_implementation_decision import decision_record as historical_decision
from .synthetic_verifier_decision import decision_record as synthetic_scope_decision
from .synthetic_fixture_spec import contract_record

VERSION = "BTC-046-v1"
BASELINE_SHA = "b0df06e66cc7cb701df095f9a3d9abf5ebe076fa"
CI_RUN_ID = 45036068026
REPO_TEST_COUNT = 262
REVIEW_FINDINGS = {
    "B46-01": {
        "severity": "HIGH",
        "status": "OPEN_FOR_GENERAL_VERIFIER",
        "evidence": "btc_engine/offline_fixture_verifier.py: verify_generated compares incoming bytes with the frozen source-controlled golden fixture hashes before calling parsers",
        "implication": "Specialized errors on malformed files are directly exercised only via private helpers; the public path is not a general adversarial parser",
        "required": "Separately authorize and validate a general-file parser before processing any real exchange CSV/ZIP.",
    },
    "B46-02": {
        "severity": "HIGH",
        "status": "OPEN_FOR_GENERAL_VERIFIER",
        "evidence": "btc_engine/offline_fixture_verifier.py: _safe_read uses candidate.is_symlink and os.open, but does not establish every input-root ancestor against an attacker-controlled race or immutable content snapshot",
        "implication": "The current helper is not a proven TOCTOU-resistant filesystem trust boundary.",
        "required": "Review input-root ownership, dirfd-based path confinement, no-follow behavior on supported OSes, and same-snapshot read guarantees.",
    },
    "B46-03": {
        "severity": "HIGH",
        "status": "OPEN_FOR_GENERAL_VERIFIER",
        "evidence": "btc_engine/offline_fixture_verifier.py: MAX_LOCAL_FILE_BYTES is 200000; _csv_canonical materializes CSV rows and _zip_csv reads bounded invented member content",
        "implication": "Production 25 MB/50 MB/100000-record/30-second resource ceilings were not exercised or proven safe.",
        "required": "Design bounded streaming and independent CPU/memory/time limits with below/at/above stress evidence.",
    },
    "B46-04": {
        "severity": "MEDIUM",
        "status": "OPEN_FOR_GENERAL_VERIFIER",
        "evidence": "tests/test_offline_fixture_verifier_negative_controls.py monkeypatches socket, connection and subprocess functions during synthetic verification",
        "implication": "Mocking API calls is not a hardened no-network or no-subprocess execution environment.",
        "required": "Define and test OS-level network and process isolation in a dedicated verifier process before general file ingestion.",
    },
    "B46-05": {
        "severity": "MEDIUM",
        "status": "OPEN_FOR_GENERAL_VERIFIER",
        "evidence": "btc_engine/offline_fixture_verifier.py: write_report_new uses exclusive create after checking output path/parent; it does not bind the path to a protected output-root file descriptor",
        "implication": "Output no-overwrite works in unit tests but root confinement, race-hardening, disk errors and atomic completeness are not established.",
        "required": "Use a dedicated trusted output root and robust exclusive/atomic report publication with negative tests.",
    },
    "B46-06": {
        "severity": "HIGH",
        "status": "OPEN_FOR_REAL_DATA",
        "evidence": "btc_engine/offline_fixture_verifier.py always reports publisher_provenance_verified=false and real_market_data_verified=false; BTC-028 records missing independent security signoff",
        "implication": "Neither upstream exchange provenance nor separate owner authorization for real market-file verification has been evidenced.",
        "required": "Retain separate data-source corroboration and explicit scoped owner/security decisions; never infer them from AI review or CI.",
    },
}
PERMISSIONS = {
    "synthetic_only_fixture_verification": True,
    "real_market_data_ingestion": False,
    "general_csv_zip_verifier_implementation": False,
    "publisher_source_authenticity_verified": False,
    "h01_strategy_backtesting": False,
    "binance_account_api_access": False,
    "paper_testnet_trading": False,
    "live_automated_trading": False,
}

def review_record():
    historical = historical_decision()
    synthetic = synthetic_scope_decision()
    if historical["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION":
        raise PermissionError("Historical real-data verifier denial changed")
    if any(historical["permissions"].values()) or any(synthetic["permissions"].values()):
        raise PermissionError("Historical permissions changed")
    if any(value for key, value in PERMISSIONS.items() if key != "synthetic_only_fixture_verification"):
        raise PermissionError("BTC-046 does not authorize an expanded verifier or trading")
    spec = contract_record()
    digest = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",",":"), ensure_ascii=True).encode("ascii")).hexdigest()
    return {
        "program": VERSION,
        "reviewed_main_commit": BASELINE_SHA,
        "ci_run_id": CI_RUN_ID,
        "main_tests_passed": REPO_TEST_COUNT,
        "btc034_spec_sha256": digest,
        "classification": "AI_ASSISTED_EVIDENCE_REVIEW_NOT_INDEPENDENT_SECURITY_CERTIFICATION",
        "decision": "SYNTHETIC_ONLY_EVIDENCE_ACCEPTED_REAL_DATA_BOUNDARY_NO_GO",
        "tested": {
            "two_allowlisted_generated_golden_fixtures": True,
            "public_entrypoint_tamper_refusals": True,
            "direct_csv_zip_parser_negative_tests": True,
            "production_limits_or_os_sandbox": False,
            "arbitrary_or_real_exchange_candle_files": False,
        },
        "findings": REVIEW_FINDINGS,
        "permissions": PERMISSIONS,
        "conclusion": "BTC-044/045 evidence supports exact invented-fixture recognition only. No real-data processing, trading, or general verifier authority.",
    }

def require_real_data_verification():
    raise PermissionError("BTC-046: real market-data verification NO GO")
