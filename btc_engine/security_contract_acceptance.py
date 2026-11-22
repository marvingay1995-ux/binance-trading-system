"""BTC-033 internal acceptance review of BTC-032, not executable fixture authorization.

This records open gaps and permitted *proposed* synthetic-only scope. It never
creates or reads hostile files, processes market data, or runs trading code.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .verifier_security_v2 import remediation_report, ERROR_CODES, TEST_CASES
from .spec_amendment import canonical_bytes

VERSION = "BTC-033-v1"
REVIEW_SHA = "4f99e21706d75d27f604f4500005bee610784835"
FINDINGS = {
    "ACPT-01": {
        "severity": "BLOCKER",
        "issue": "Canonical candle input column mapping, numeric grammar, BOM/UTF8 and JSONL bytes not fully finalized",
        "required_action": "Freeze a versioned CSV-to-canonical schema with literal synthetic golden bytes and SHA256 test vectors before implementation",
    },
    "ACPT-02": {
        "severity": "BLOCKER",
        "issue": "Several synthetic tests combine unrelated faults and cannot identify which protection rejected a file",
        "required_action": "Split ZIP entry and OHLCV cases into single-fault, expected-error fixtures; specify ordering if multiple faults exist",
    },
    "ACPT-03": {
        "severity": "BLOCKER",
        "issue": "Proposed numerical limits lack measured stress evidence or enforceable runtime budgets",
        "required_action": "Define reproducible bounded test harness and below/equal/above fixtures without treating contractual limits as verified",
    },
    "ACPT-04": {
        "severity": "BLOCKER",
        "issue": "Path/TOCTOU, ZIP member identity, output collision and no-network controls are not executable or tested",
        "required_action": "Specify OS-specific boundary, input/output sandbox and negative controls before authorizing a verifier",
    },
    "ACPT-05": {
        "severity": "BLOCKER",
        "issue": "Source provenance, independent security acceptance and explicit owner implementation approval are still missing",
        "required_action": "Never infer approval from an AI review, fixture test, PR merge, GitHub issue or locally matching hash",
    },
}
PROPOSED_SYNTHETIC_SCOPE = {
    "allowed_only_after_separate_approval": [
        "Create deterministic, generated, non-market BTCUSDT-like 4h CSV/ZIP fixture bytes in a repository test-fixture directory",
        "Implement an isolated fixture-generation program with no live network or account access",
        "Check self-consistency of synthetic fixtures, golden hashes and expected error-code registry against a fixture manifest",
        "Execute tests of fixture generation and contract metadata without interpreting strategy signals or calculating performance",
    ],
    "prohibited": [
        "Build a general CSV/ZIP verifier for actual exchange data",
        "Download, inspect, or authenticate real BTC market candles",
        "Perform H01 SMA calculation, optimization or backtesting",
        "Use Binance API, credentials, signed account endpoints, testnet or paper/live order execution",
        "Claim independent security certification or that the verifier is safe without runtime validation",
    ],
    "required_before_approval": [
        "Exact authorized repository branch, source commit, file paths and threat-contract fingerprint",
        "Product-owner signoff explicitly limited to synthetic fixture generation and offline tests",
        "Defined fixture input sizes and output directory, deterministic golden bytes and stable error codes",
        "Accepted CI isolation requirements and explicit rejection of network/credentials/strategy imports",
    ],
}
PERMISSIONS = {
    "security_contract_design_accepted_for_further_review": True,
    "synthetic_fixture_generator_implementation_authorized": False,
    "synthetic_fixture_execution_authorized": False,
    "general_market_data_verifier_authorized": False,
    "real_candle_processing_authorized": False,
    "h01_signal_or_backtest_authorized": False,
    "paper_trading_authorized": False,
    "live_trading_authorized": False,
    "automated_orders_authorized": False,
}


def acceptance_report():
    source = remediation_report()
    if source["decision"] != "CONTRACT_IMPROVED_NO_VERIFIER_IMPLEMENTATION_AUTHORIZED":
        raise PermissionError("BTC-032 contract gate changed")
    if set(source["remediations"]) != {f"AI-SEC-{i:02d}" for i in range(1,9)}:
        raise ValueError("BTC-032 findings incomplete")
    if "RECORD_COUNT_EXCEEDED" not in ERROR_CODES:
        raise ValueError("BTC-032 record boundary code missing")
    if not TEST_CASES:
        raise ValueError("no BTC-032 test contract")
    if any(PERMISSIONS[k] for k in PERMISSIONS if k != "security_contract_design_accepted_for_further_review"):
        raise PermissionError("BTC-033 must not grant test or trading authorization")
    fingerprint = hashlib.sha256(
        json.dumps(source,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")
    ).hexdigest()
    return {
        "program": VERSION,
        "reviewed_main_commit": REVIEW_SHA,
        "reviewed_btc032_report_sha256": fingerprint,
        "h01_v2_spec_sha256": hashlib.sha256(canonical_bytes()).hexdigest(),
        "review_classification": "INTERNAL_AI_ASSISTED_CONTRACT_REVIEW_NOT_INDEPENDENT_SECURITY_CERTIFICATION",
        "decision": "CONDITIONALLY_ACCEPT_DESIGN_ONLY_SYNTHETIC_TEST_AUTHORIZATION_WITHHELD",
        "review_findings": FINDINGS,
        "proposed_synthetic_only_scope": PROPOSED_SYNTHETIC_SCOPE,
        "permissions": PERMISSIONS,
        "external_review_evidence_present": False,
        "synthetic_test_files_created": False,
        "synthetic_fixture_tests_executed": False,
        "actual_file_verifier_implemented": False,
        "remaining_blockers": list(FINDINGS),
    }


def require_synthetic_fixture_authorization():
    raise PermissionError("BTC-033: no separately scoped synthetic fixture implementation authorization")


def main():
    parser=argparse.ArgumentParser(description="BTC-033 review only; no fixtures")
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    r=acceptance_report()
    Path(args.output).write_text(json.dumps(r,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"program":VERSION,"decision":r["decision"],"blockers":len(r["remaining_blockers"])},indent=2))


if __name__=="__main__":
    main()
