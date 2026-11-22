"""BTC-035 scope-specific implementation authorization decision, not a generator."""
import argparse
import hashlib
import json
from pathlib import Path

from .synthetic_fixture_spec import contract_record

VERSION = "BTC-035-v1"
BASE_COMMIT = "62094a8ff855ab800ef9cf8a43b82e577425d479"
ALLOWED_ONLY_IF_SEPARATELY_APPROVED = (
    "Add a synthetic-only generator module btc_engine/synthetic_fixture_generator.py",
    "Add deterministic generated non-market CSV and ZIP fixtures under tests/fixtures/synthetic/",
    "Add tests/test_synthetic_fixture_generator.py with golden hashes and negative-control cases",
    "Use Python standard library, bounded resources, and isolated CI without credentials or network",
    "Report and label every generated item SYNTHETIC_NOT_BINANCE_DATA",
)
PROHIBITED = (
    "Any real BTC/USDT market data or Binance archive processing",
    "General local-file market-data verification",
    "Any Binance API, account key, signed call or network download",
    "H01 signals, backtesting, strategy returns or optimization",
    "Paper, testnet, live, automated orders or trading",
    "Changing historical NO_GO decisions or pretending AI review is independent security certification",
)
APPROVAL_EVIDENCE = {
    "product_owner_explicit_synthetic_only_approval": False,
    "exact_scope_and_file_list_accepted": False,
    "golden_reference_and_negative_controls_accepted": False,
    "bounded_offline_execution_plan_accepted": False,
}

def decision_record():
    original = contract_record()
    if original["decision"] != "SPECIFICATION_RECORDED_IMPLEMENTATION_AUTHORIZATION_WITHHELD":
        raise PermissionError("BTC-034 scope changed unexpectedly")
    if any(APPROVAL_EVIDENCE.values()):
        raise PermissionError("BTC-035 may not fabricate signoff")
    spec_sha = hashlib.sha256(
        json.dumps(original, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    ).hexdigest()
    return {
        "program": VERSION,
        "main_baseline_commit": BASE_COMMIT,
        "btc034_contract_sha256": spec_sha,
        "scope_after_separate_authorization_only": list(ALLOWED_ONLY_IF_SEPARATELY_APPROVED),
        "prohibited": list(PROHIBITED),
        "evidence": APPROVAL_EVIDENCE,
        "outstanding": list(APPROVAL_EVIDENCE),
        "decision": "SCOPED_REQUEST_PREPARED_IMPLEMENTATION_NOT_AUTHORIZED",
        "permissions": {
            "synthetic_fixture_generator_implementation": False,
            "synthetic_fixture_generation_or_execution": False,
            "real_market_verifier": False,
            "market_data_ingestion": False,
            "h01_backtesting": False,
            "binance_api_access": False,
            "paper_trading": False,
            "live_trading": False,
        },
        "notes": [
            "The milestone title requests an authorization review, not explicit signed implementation approval.",
            "This program does not construct or run a fixture generator.",
            "No independent security certification is asserted."
        ]
    }

def require_synthetic_generator_implementation():
    raise PermissionError("BTC-035: explicit scope acceptance and implementation approval missing")

def main():
    parser = argparse.ArgumentParser(description="BTC-035 authorization decision only")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    record = decision_record()
    Path(args.output).write_text(json.dumps(record, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"program": VERSION, "decision": record["decision"]}))

if __name__ == "__main__":
    main()
