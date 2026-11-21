"""BTC-018 immutable research decision and fail-closed promotion check.

Historical benchmarks may still be calculated for comparison. Neither fixed
SMA 5/20 baseline is eligible for paper or live promotion.
"""
import argparse
import json
from pathlib import Path

DECISION_ID = "BTC-018"
SOURCE_RUN = 44915102425
SOURCE_COMMIT = "4e5688b84619cc6f047b8592b4145bd3188e44a4"
DECISIONS = {
    "sma_5_20_1h_baseline": {
        "status": "RETIRED_FROM_TRADING_CONSIDERATION",
        "benchmark_only": True,
        "holdout_return_pct": -0.6652519869565388,
        "double_cost_holdout_return_pct": -5.433550023134681,
        "triple_cost_holdout_return_pct": -9.986965643656088,
        "positive_historical_windows": 1,
        "observed_historical_windows": 6,
        "full_period_max_drawdown_pct": 29.511797039308398,
    },
    "sma_5_20_4h_baseline": {
        "status": "RETIRED_FROM_TRADING_CONSIDERATION",
        "benchmark_only": True,
        "holdout_return_pct": 0.6167093680309321,
        "double_cost_holdout_return_pct": -0.5826496339032428,
        "triple_cost_holdout_return_pct": -1.7128835238142792,
        "positive_historical_windows": 2,
        "observed_historical_windows": 6,
        "full_period_max_drawdown_pct": 8.93111746481109,
    },
}


def decision_report():
    return {
        "program": DECISION_ID,
        "status": "FINAL_RESEARCH_DECISION",
        "historical_source_run": SOURCE_RUN,
        "source_commit_sha": SOURCE_COMMIT,
        "strategies": DECISIONS,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "automated_execution_authorized": False,
        "qualification_policy": {
            "previously_viewed_data": "RESEARCH_ONLY_NO_NEW_HOLDOUT_CLAIMS",
            "prospective_4h_registration": "COMPARISON_BENCHMARK_ONLY",
            "new_hypotheses": "SEPARATELY_PREREGISTER_AND_VALIDATE",
            "authorization": "SEPARATE_EXPLICIT_REVIEW_REQUIRED",
        },
        "blockers": [
            "No robust profitability after higher simulated execution costs",
            "Daily loss cap is not enforceable using candle-open-only checks",
            "Exchange filters and fee tiers not independently verified",
            "Partial fills and restart reconciliation not modeled",
            "No genuinely new prospective confirmation",
        ],
    }


def require_promotion_authorization(strategy_id, target):
    """Never convert a benchmark status into a permission to trade."""
    if not isinstance(strategy_id, str) or strategy_id not in DECISIONS:
        raise ValueError("unknown strategy: fail closed")
    if target not in ("paper", "live"):
        raise ValueError("unknown promotion target: fail closed")
    raise PermissionError(
        f"{DECISION_ID}: {strategy_id} is RETIRED; {target} trading prohibited"
    )


def main():
    parser = argparse.ArgumentParser(description="BTC-018 research decision, no execution")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = decision_report()
    Path(args.output).write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"program": report["program"],
                      "decision": "RETIRED_BOTH_BASELINES",
                      "paper_trading_authorized": False,
                      "live_trading_authorized": False}, indent=2))


if __name__ == "__main__":
    main()
