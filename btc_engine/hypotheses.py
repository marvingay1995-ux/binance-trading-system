"""BTC-019 hypothesis registry: specifications only; no signals or orders."""
import argparse
import json
from pathlib import Path

REGISTRY_VERSION = "BTC-019-v1"
PROSPECTIVE_START_UTC = "2026-12-01T00:00:00Z"
RESEARCH_HYPOTHESES = {
    "H01_TREND_CONDITION": {
        "question": "Does a separately preregistered long-term trend condition improve long-only risk-adjusted outcomes compared with doing nothing?",
        "market": "BTCUSDT_SPOT", "timeframe": "4h",
        "expected_effect": "Reduce exposure in persistent declines, but may miss reversals.",
        "falsification": "Net-of-cost results do not outperform the preregistered no-trade and risk-matched comparison under an independent unseen period.",
        "status": "CONCEPT_ONLY_NOT_PARAMETERIZED",
        "entry_rule": None, "exit_rule": None, "parameters": None,
        "execution_code_authorized": False
    },
    "H02_VOLATILITY_CONTROL": {
        "question": "Does a separately preregistered volatility-aware exposure policy reduce tail risk without producing unacceptable cost drag?",
        "market": "BTCUSDT_SPOT", "timeframe": "4h",
        "expected_effect": "Reduce concentration of losses in volatile periods; could increase turnover.",
        "falsification": "No robust risk improvement after realistic costs, execution uncertainty and unseen-window comparisons.",
        "status": "CONCEPT_ONLY_NOT_PARAMETERIZED",
        "entry_rule": None, "exit_rule": None, "parameters": None,
        "execution_code_authorized": False
    }
}
REQUIRED_FOR_TESTING = (
    "immutable_rule_specification",
    "parameter_origin_without_viewed_holdout_tuning",
    "prospective_data_cutoff",
    "fee_spread_slippage_model",
    "executable_market_filter_provenance",
    "leakage_checks",
    "cost_stress_plan",
    "benchmark_and_risk_metrics",
    "predefined_fail_criteria",
    "independent_review_approval",
)


def registry_report():
    return {
        "program": REGISTRY_VERSION,
        "status": "IDEAS_REGISTERED_NOT_IMPLEMENTED",
        "strategy_candidates": RESEARCH_HYPOTHESES,
        "preregistered_prospective_start_utc": PROSPECTIVE_START_UTC,
        "earlier_data": "ALREADY_EXAMINED_NOT_ELIGIBLE_AS_FRESH_HOLDOUT",
        "retired_sma_baselines": ["sma_5_20_1h_baseline", "sma_5_20_4h_baseline"],
        "required_before_any_hypothesis_backtest": list(REQUIRED_FOR_TESTING),
        "default_decision": "DO_NOT_TEST_OR_PROMOTE",
        "paper_authorized": False, "live_authorized": False,
        "notes": [
            "Hypotheses do not yet have frozen indicator definitions, thresholds or exits.",
            "No profitability claim or candidate selection can be inferred.",
            "December 2026 future data is reserved; no additional retrospective parameter optimization.",
            "Separate review and explicit authorization required for any future simulation.",
            "No Binance account connection, orders or credentials."
        ]
    }


def require_research_execution(hypothesis_id, specification=None):
    """Never let a concept-only entry be used as an executable strategy."""
    if hypothesis_id not in RESEARCH_HYPOTHESES:
        raise ValueError("unknown research hypothesis; fail closed")
    raise PermissionError("BTC-019 concepts are not executable or authorized for backtesting/trading")


def main():
    p = argparse.ArgumentParser(description="BTC-019 registration, no trading")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    Path(args.output).write_text(json.dumps(registry_report(), indent=2) + "\n")
    print(json.dumps({"program": REGISTRY_VERSION, "decision": "DO_NOT_TEST_OR_PROMOTE"}, indent=2))


if __name__ == "__main__":
    main()
