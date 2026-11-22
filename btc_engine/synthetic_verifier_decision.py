"""BTC-043 synthetic-only offline verifier decision — no implementation.

This records a reviewed implementation boundary and missing explicit owner
authorization. Historical BTC-028/039 gates remain untouched.
"""
import hashlib
import json

from .verifier_implementation_decision import decision_record as historical_decision
from .synthetic_fixture_spec import contract_record as synthetic_spec
from .verifier_threat_contract import contract_report

VERSION = "BTC-043-v1"
BASELINE_SHA = "0c174f37b7ab6d883e3081c8569a410d16399cd5"
FILES_AFTER_SEPARATE_APPROVAL = (
    "btc_engine/offline_fixture_verifier.py",
    "tests/test_offline_fixture_verifier.py",
    "docs/BTC-043-OFFLINE-FIXTURE-VERIFIER-EVIDENCE.md",
)
SCOPE = {
    "data": "only invented local fixtures labeled SYNTHETIC_NOT_BINANCE_DATA",
    "file_types": ("strict synthetic-candle4h-v1 CSV", "single flat regular CSV member in ZIP"),
    "security": (
        "reject paths outside configured input root and symlinks/special files",
        "one opened snapshot for raw hashing and parsing; no archive extraction",
        "bounded raw/expanded/row/record processing and safe ZIP metadata",
        "deterministic reject codes, canonical SHA256, distinct unverified publisher status",
        "offline constrained CI; credentials and network/process calls prohibited",
    ),
    "tests": "existing BTC-034–038 synthetic fixtures, positive/negative and resource-boundary tests",
    "report": "deterministic local-only JSON, collision refusal and no overwrite",
}
EXCLUSIONS = (
    "real exchange CSV/ZIP files or data ingestion",
    "Binance API, network access or credentials",
    "H01 signals/backtesting/optimization and performance calculations",
    "paper trading, testnet trading, live trading or automated orders",
    "deployment, provider authentication or independent security certification claims",
)
MISSING_EVIDENCE = {
    "owner_explicit_approval_of_exact_btc043_scope": False,
    "accepted_runtime_resource_limits_and_fixture_verdicts": False,
    "confirmed_no_network_os_sandbox_design": False,
    "independent_human_security_signoff_for_general_market_verifier": False,
}
PERMISSIONS = {
    "synthetic_only_verifier_development": False,
    "real_market_data_verifier": False,
    "real_market_data_processing": False,
    "h01_signals_or_backtesting": False,
    "paper_or_testnet_trading": False,
    "live_or_automated_trading": False,
}

def decision_record():
    earlier = historical_decision()
    if earlier["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION":
        raise PermissionError("BTC-028 historical gate unexpectedly changed")
    if any(earlier["permissions"].values()) or any(MISSING_EVIDENCE.values()) or any(PERMISSIONS.values()):
        raise PermissionError("BTC-043 must remain unapproved")
    threat = contract_report()
    spec = synthetic_spec()
    spec_bytes = json.dumps(spec, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return {
        "program": VERSION,
        "reviewed_main_commit": BASELINE_SHA,
        "btc027_contract_sha256": threat["contract_sha256"],
        "btc034_spec_sha256": hashlib.sha256(spec_bytes).hexdigest(),
        "classification": "INTERNAL_AI_ASSISTED_SCOPE_REVIEW_NOT_SECURITY_CERTIFICATION",
        "decision": "SYNTHETIC_ONLY_SCOPE_PROPOSED_EXPLICIT_IMPLEMENTATION_APPROVAL_MISSING",
        "proposed_files": list(FILES_AFTER_SEPARATE_APPROVAL),
        "proposed_scope": SCOPE,
        "prohibited": list(EXCLUSIONS),
        "owner_and_security_evidence": MISSING_EVIDENCE,
        "permissions": PERMISSIONS,
        "limitations": [
            "Milestone title and PR merge do not constitute explicit authorization.",
            "No verifier was implemented or invoked; no hostile file was verified.",
            "Approval of invented-only development, if later given, cannot authorize general market-file parsing.",
        ],
    }

def require_implementation():
    raise PermissionError("BTC-043: synthetic-only verifier implementation approval not recorded")
