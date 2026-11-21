"""BTC-023: H01-v2 review ledger and fail-closed authorization gate.

This audits a design contract. It does not grant permission to implement
signals, run a strategy simulation, connect to an account, or place orders.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .spec_amendment import AMENDMENT, canonical_bytes


DESIGN_FINDINGS = {
    "DATA-002": {"assessment": "DESIGNED_NOT_EVIDENCED",
                 "basis": "1,200-bar UTC warmup range, source/hash requirements specified; actual verified dataset absent"},
    "SIGNAL-001": {"assessment": "SPECIFIED_FOR_REVIEW",
                   "basis": "SMA uses closes[i-1200:i] at open[i], excludes current candle; no runtime leakage regression tests"},
    "SIZE-001": {"assessment": "DESIGNED_NOT_IMPLEMENTED",
                 "basis": "fee-inclusive Decimal budget and rejection rules; market filters, residual dust and executions unverified"},
    "COMP-001": {"assessment": "SPECIFIED_WITH_LIMITATION",
                 "basis": "20% initial-notional, never-rebalanced comparator is not dynamically risk-matched"},
    "RISK-002": {"assessment": "UNRESOLVED_HARD_LIMIT",
                 "basis": "2% UTC-day loss boundary cannot be enforced or guaranteed from 4h OHLC"},
    "EXEC-001": {"assessment": "UNRESOLVED_EXECUTION",
                 "basis": "authentic order filters/fees, partial fills and crash reconciliation missing"},
    "EVAL-001": {"assessment": "INCOMPLETE_INDEPENDENT_VALIDATION",
                 "basis": "60-day data admission is not statistical sufficiency; external review absent"},
    "AUTH-001": {"assessment": "AUTHORIZATION_NOT_GRANTED",
                 "basis": "specification has all execution permissions false and no documented independent human approval"},
}
AUTHORIZATION_CHECKS = {
    "human_reviewer_signoff": False,
    "provenance_bound_warmup_verified": False,
    "exact_h01_v2_specification_accepted": False,
    "simulator_scope_and_negative_controls_approved": False,
    "exchange_realism_model_verified": False,
    "results_are_not_live_or_paper_authority": True,
}


def review_report(spec=AMENDMENT, checks=AUTHORIZATION_CHECKS):
    if spec != AMENDMENT:
        raise ValueError("specification mismatch: fail closed")
    if checks != AUTHORIZATION_CHECKS:
        raise ValueError("unreviewed authorization evidence: fail closed")
    if any(spec["permissions"].values()):
        raise PermissionError("execution permission unexpectedly enabled")
    digest = hashlib.sha256(canonical_bytes()).hexdigest()
    eligibility = all(checks.values()) and not any(
        finding["assessment"].startswith(("UNRESOLVED", "INCOMPLETE", "AUTHORIZATION_NOT"))
        for finding in DESIGN_FINDINGS.values()
    )
    # Even meeting a checklist requires a new, separately approved program.
    return {
        "program": "BTC-023",
        "reviewed_specification": "BTC-022 H01-v2 proposed amendment",
        "source_spec_sha256": digest,
        "review_type": "INTERNAL_DOCUMENT_AND_CONTRACT_ASSESSMENT_NOT_EXTERNAL_INDEPENDENT_SIGNOFF",
        "findings": DESIGN_FINDINGS,
        "evidence_checks": checks,
        "design_status": "PARTIALLY_SPECIFIED_REQUIREMENTS_NOT_FULLY_ACCEPTED",
        "offline_research_implementation_authorized": False,
        "offline_research_backtest_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "may_auto_approve": False,
        "unmet_required_checks": [name for name, ok in checks.items() if not ok],
        "readiness_gate": "BLOCKED",
        "review_complete_for_decision": True,
        "rationale": "New independent review and an explicit separately versioned authorization are required",
        "hypothetical_evidence_sufficient_without_new_authorization": False,
        "current_checklist_preconditions_satisfied": eligibility,
    }


def require_offline_authorization():
    raise PermissionError("BTC-023: offline H01 implementation and backtesting NOT AUTHORIZED")


def main():
    p = argparse.ArgumentParser(description="BTC-023 offline authorization review ONLY")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    report = review_report()
    Path(args.output).write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(json.dumps({"program":report["program"], "readiness_gate":report["readiness_gate"],
        "offline_research_backtest_authorized": False,
        "outstanding_evidence_checks": report["unmet_required_checks"]}, indent=2))


if __name__ == "__main__":
    main()
