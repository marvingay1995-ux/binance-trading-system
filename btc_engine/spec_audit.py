"""BTC-021: read-only design audit of H01-v1. No strategy signals or orders.

An automated inspection cannot replace independent human review.
"""
import argparse
import hashlib
import json
from pathlib import Path
from .trend_registration import PROTOCOL, canonical_bytes


def audit_h01(spec=PROTOCOL):
    """Separate verified structural facts from unresolved specification gaps."""
    findings = []
    def record(code, severity, evidence, resolution):
        findings.append({"id":code,"severity":severity,"evidence":evidence,
                         "required_resolution":resolution})
    m = spec.get("market", {})
    trend = spec.get("trend", {})
    position = spec.get("position", {})
    evaluation = spec.get("evaluation", {})
    controls = spec.get("controls", {})
    if m.get("interval") != "4h" or trend.get("lookback_complete_bars") != 1200:
        record("SPEC-001","BLOCKER","Unexpected interval or indicator length",
               "Register a new version; do not silently change H01-v1")
    if not all(controls.get(k) is False for k in
               ("research_backtest_authorized","paper_trading_authorized","live_trading_authorized")):
        record("SAFE-001","BLOCKER","A simulation or trading authorization is enabled",
               "Deny all execution in this review program")
    if position.get("target_exposure_fraction_of_current_equity", 1) > position.get("maximum_exposure_fraction", 0):
        record("RISK-001","BLOCKER","Target exposure exceeds maximum exposure",
               "Revise in separately versioned protocol")
    if evaluation.get("prospective_start_utc") != "2026-12-01T00:00:00Z":
        record("DATA-001","BLOCKER","Prospective cutoff differs from registered cutoff",
               "Use the preregistered prospective boundary")
    # The remaining issues cannot be cleared by checking prose.
    record("DATA-002","BLOCKER",
           "1,200 completed 4h warmup bars (200 days) required at 2026-12-01; source, hash, continuous alignment and first actionable bar not independently specified",
           "Define source ranges, warmup-only separation, provenance, alignment and first execution-eligible instant")
    record("SIGNAL-001","BLOCKER",
           "English rules do not provide normative bar-index pseudocode and exact signal/fill ordering",
           "Specify completed-bar indices, SMA endpoint, first eligible signal and no-lookahead invariants")
    record("SIZE-001","BLOCKER",
           "20% equity entry target has no rounding, fee-inclusive quote budget, residual/dust, minimum notional or sell quantity semantics",
           "Specify Decimal quantity math, remaining cash, unavailable sizes, and portfolio-wide risk invariants")
    record("COMP-001","BLOCKER",
           "Risk-matched passive BTC comparison lacks rebalance frequency, funding, initial allocation, fees and mark-to-market conventions",
           "Freeze comparator formulas and friction accounting before evaluation")
    record("RISK-002","BLOCKER",
           "2% UTC daily-loss ceiling cannot be guaranteed by 4h OHLC or candle-open checks",
           "Separate observed drawdown metric from hard live limits; design enforceable loss and shutdown controls")
    record("EXEC-001","BLOCKER",
           "Current exchange filters, spread, account fees, partial fills and restart reconciliation not verified",
           "Require provenance-bound filters and realistic execution specification before any execution approval")
    record("EVAL-001","BLOCKER",
           "60 days is a minimum admission window, not evidence of robust generalization; no independent reviewer or statistical uncertainty protocol",
           "Define prospective scoring, minimum effective trade count, multiple unseen regimes and independent reviewer identity")
    record("AUTH-001","BLOCKER",
           "BTC-020 explicitly withholds permission for offline strategy implementation and backtesting",
           "Obtain a separate reviewed authorization after a revised, complete protocol")
    return {
        "program":"BTC-021",
        "review_type":"AUTOMATED_DOCUMENT_AND_CONTRACT_REVIEW_NOT_EXTERNAL_INDEPENDENT_ASSURANCE",
        "source_program":spec.get("program"),
        "source_hypothesis":spec.get("hypothesis"),
        "source_version":spec.get("version"),
        "source_protocol_sha256":hashlib.sha256(canonical_bytes()).hexdigest() if spec == PROTOCOL else None,
        "findings":findings,
        "blocker_count":sum(x["severity"]=="BLOCKER" for x in findings),
        "decision":"BLOCKED_RESEARCH_SIMULATION_PAPER_AND_LIVE",
        "permissions":{"implement_signal":False,"backtest":False,"paper":False,"live":False},
        "note":"This report does not change the frozen BTC-020 specification or select new parameters."
    }


def main():
    p=argparse.ArgumentParser(description="BTC-021 non-executing specification audit")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    report=audit_h01()
    Path(args.output).write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"program":report["program"],"blockers":report["blocker_count"],
                      "decision":report["decision"]},indent=2))


if __name__=="__main__":
    main()
