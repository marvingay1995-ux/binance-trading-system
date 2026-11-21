"""BTC-020 versioned strategy design contract; deliberately not executable.

This module specifies the proposed hypothesis and validates its fields.
It has no candle-to-signal function, backtester, account session, or orders.
"""
import argparse
import hashlib
import json
from pathlib import Path

PROTOCOL = {
    "program": "BTC-020",
    "hypothesis": "H01_TREND_CONDITION",
    "version": "H01-v1-proposed",
    "stage": "SPECIFICATION_FROZEN_FOR_REVIEW_NOT_AUTHORIZED",
    "market": {"symbol": "BTCUSDT", "venue": "Binance Spot", "interval": "4h",
               "direction": "LONG_ONLY_NO_LEVERAGE"},
    "trend": {
        "indicator": "SMA",
        "lookback_complete_bars": 1200,
        "rationale": "200 calendar days x six 4h bars/day; conventional long-horizon trend concept, not fitted to BTC-011–014 returns",
        "price": "CLOSE",
        "signal_observation": "LATEST_COMPLETED_4H_BAR_ONLY",
        "entry": "If flat and previous completed close > SMA of the latest 1200 completed 4h closes, mark simulated buy for next bar open",
        "exit": "If long and previous completed close <= that SMA, mark simulated sell for next bar open",
        "equality": "FLAT_OR_EXIT",
        "position_when_no_warmup": "FLAT_NO_SIGNAL",
        "reentry": "After an exit, a later completed bar above its SMA can qualify; no optimization",
    },
    "position": {
        "target_exposure_fraction_of_current_equity": 0.20,
        "maximum_exposure_fraction": 0.30,
        "starting_simulated_usdt": 100.0,
        "risk_assumption": "Spot long, cash only, no borrowing, no shorts",
    },
    "research_execution_assumptions": {
        "fee_rate_per_side": 0.001,
        "slippage_rate_per_side": 0.0005,
        "half_spread_rate_per_side": 0.0001,
        "stress_multipliers": [1, 2, 3],
        "fill": "HYPOTHETICAL_NEXT_BAR_OPEN_WITH_COSTS",
        "exchange_filter_verification": "NOT_VERIFIED",
        "partial_fills": "NOT_MODELED",
        "overnight_gaps_and_intrabar_stops": "NOT_MODELED",
        "daily_loss_cap": "NOT_ENFORCEABLE_IN_THIS_RESEARCH_ENGINE",
    },
    "evaluation": {
        "previously_examined_history": "WARMUP_ONLY_NO_MODEL_SELECTION_OR_FRESH_HOLDOUT_CLAIMS",
        "prospective_start_utc": "2026-12-01T00:00:00Z",
        "minimum_prospective_days": 60,
        "primary_metric": "NET_USDT_RETURN_AFTER_SIMULATED_COSTS",
        "comparators": ["NO_TRADE_CASH", "RISK_MATCHED_PASSIVE_BTC_EXPOSURE"],
        "secondary_metrics": ["MAX_DRAWDOWN", "CLOSED_TRADE_COUNT", "TOTAL_FEES", "WORST_UTC_DAY_MARK"],
        "qualification_rule": "NO_AUTOMATIC_QUALIFICATION_EVEN_IF_ALL_CHECKS_PASS",
        "rejection_conditions": [
            "NEGATIVE_NET_RETURN_AFTER_BASELINE_COSTS",
            "NEGATIVE_NET_RETURN_AFTER_DOUBLE_COSTS",
            "WORSE_MAX_DRAWDOWN_THAN_RISK_MATCHED_PASSIVE_COMPARATOR",
            "DATA_INTEGRITY_FAILURE",
            "UNVERIFIED_ORDER_FILTERS_FOR_ANY_EXECUTION_PROPOSAL",
        ],
    },
    "controls": {
        "retired_baseline_reuse": False,
        "parameter_tuning_on_viewed_archives": False,
        "new_signal_implementation_allowed": False,
        "research_backtest_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "approval_required": "SEPARATE_SIGNED_OFF_RESEARCH_PROTOCOL",
    },
}


def canonical_bytes():
    return json.dumps(PROTOCOL, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def specification_report():
    validate_registration(PROTOCOL)
    return {
        "protocol": PROTOCOL,
        "canonical_sha256": hashlib.sha256(canonical_bytes()).hexdigest(),
        "decision": "REVIEW_ONLY_DO_NOT_SIMULATE_OR_TRADE",
    }


def validate_registration(spec):
    if spec != PROTOCOL:
        raise ValueError("modified or unknown research specification; fail closed")
    if spec["controls"]["research_backtest_authorized"] or spec["controls"]["paper_trading_authorized"] or spec["controls"]["live_trading_authorized"]:
        raise PermissionError("trading or backtesting cannot be authorized by BTC-020")
    if spec["trend"]["lookback_complete_bars"] != 1200:
        raise ValueError("unexpected lookback")
    if spec["evaluation"]["prospective_start_utc"] != "2026-12-01T00:00:00Z":
        raise ValueError("unexpected prospective boundary")
    return True


def main():
    p = argparse.ArgumentParser(description="BTC-020 offline strategy specification, no execution")
    p.add_argument("--output", required=True)
    args = p.parse_args()
    result = specification_report()
    Path(args.output).write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"program": "BTC-020", "sha256": result["canonical_sha256"],
                      "decision": result["decision"]}, indent=2))


if __name__ == "__main__":
    main()
