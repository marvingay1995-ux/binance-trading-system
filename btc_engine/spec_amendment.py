"""BTC-022 proposed H01-v2 specification amendment, NO signal/backtest/trading.

Machine-readable contract and review checklist. All execution permissions off.
"""
import argparse
import hashlib
import json
from pathlib import Path

AMENDMENT = {
    "program": "BTC-022",
    "hypothesis": "H01_TREND_CONDITION",
    "version": "H01-v2-specification-amendment-proposed",
    "supersedes_for_review_only": "H01-v1-proposed",
    "status": "REVIEW_REQUIRED_NOT_APPROVED",
    "immutable_h01_parameters": {
        "symbol": "BTCUSDT", "venue": "Binance Spot", "timeframe": "4h",
        "lookback_completed_bars": 1200,
        "long_target_fraction_of_equity": "0.20",
        "max_portfolio_exposure_fraction": "0.30",
        "starting_simulated_usdt": "100",
        "fee_rate_per_side": "0.001",
        "slippage_per_side": "0.0005",
        "half_spread_per_side": "0.0001",
        "cost_multipliers": [1, 2, 3],
        "prospective_start_utc": "2026-12-01T00:00:00Z",
        "minimum_future_complete_days": 60,
    },
    "bar_index_contract": {
        "candle_index": "i is zero-based execution candle; its open timestamp is T_i",
        "closed_candle_input_only": "closes[0:i] excludes execution candle i",
        "latest_completed_close": "closes[i-1]",
        "sma_1200": "sum(closes[i-1200:i])/1200, requires i >= 1200",
        "evaluation_point": "at opening T_i, after candle i-1 is fully finalized",
        "entry": "flat AND closes[i-1] > sma_1200 => hypothetical buy at open[i]",
        "exit": "long AND closes[i-1] <= sma_1200 => hypothetical sell at open[i]",
        "not_enough_warmup": "remain flat; no signal",
        "same_bar_ordering": "never read high[i],low[i],close[i],volume[i] to decide at open[i]",
        "missing_or_revised_bar": "fail closed; no interpolating or filling gaps",
        "one_decision_per_bar": True,
    },
    "provenance": {
        "history_used_for_warmup_only": True,
        "warmup_requirement": "1200 consecutive complete 4h bars ending strictly before 2026-12-01T00:00:00Z",
        "initial_warmup_first_open_utc": "2026-05-15T00:00:00Z",
        "last_warmup_open_utc": "2026-11-30T20:00:00Z",
        "first_eligible_evaluation_open_utc": "2026-12-01T00:00:00Z",
        "required_evidence": ["origin_url", "archive_months", "retrieval_utc", "raw_sha256", "canonical_candle_sha256", "complete_contiguous_utc_candles"],
        "warmup_returns_are_holdout": False,
        "future_data_must_be_unseen_and_intact": True,
    },
    "hypothetical_sizing": {
        "arithmetic": "Decimal for quantities/fees; no binary float for order filters",
        "entry_budget": "min(0.20 * marked_equity, free_cash) INCLUSIVE of estimated entry fee",
        "entry_price": "next_open * (1 + multiplier*(slippage+half_spread))",
        "buy_quantity": "floor_to_step(entry_budget/(entry_price*(1+multiplier*fee_rate)))",
        "buy_rejection": "remain flat if step, minQty, minNotional, fee-inclusive cash, or max exposure fail",
        "sell_price": "next_open * (1 - multiplier*(slippage+half_spread))",
        "sell_quantity": "full owned BTC rounded down to valid exchange step; dust recorded, never silently discarded",
        "sell_rejection": "mark unresolved position, fail closed and prohibit new entries",
        "max_exposure": "aggregate marked BTC exposure across all tracked positions <= 0.30*equity; if other positions unknown, block",
        "unsupported": ["partial_fills", "account_actual_fee_tiers", "filter_refresh", "restart_reconciliation"],
    },
    "passive_comparator": {
        "kind": "RISK_MATCHED_PASSIVE_BTC_EXPOSURE",
        "start": "2026-12-01T00:00:00Z first verified opening price",
        "capital": "100 hypothetical USDT",
        "allocation": "20% of initial equity fee-inclusive, rounded using same hypothetical size/filter rules",
        "rebalancing": "NONE",
        "entry_costs": "same fee, spread and slippage assumptions as H01",
        "marking": "mark BTC to each completed bar close, cash unchanged",
        "terminal_comparison": "liquidate residual BTC notionally at last completed candle close with same sell costs, report also pre-liquidation marked equity",
        "no_trade_comparator": "100 USDT cash, no fee, no BTC, no yield",
        "risk_matching_limitation": "equal initial notional, NOT equal time-varying volatility or risk",
        "missing_entry": "comparator invalid, fail review; do not force a fill",
    },
    "risk_design": {
        "daily_limit_fraction": "0.02",
        "measurement": "mark portfolio equity relative to UTC day opening equity; report intrabar worst-case indicative lows separately",
        "gap_and_intrabar": "OHLC cannot certify an enforceable 2% loss ceiling; execution gaps can exceed threshold",
        "entry_admission": "deny new entries on unknown state, daily threshold reached, stale data, unverified filters, or disconnected venue",
        "halt_semantics": "fail closed, cancel unfilled hypothetical intents, reconcile any exposure before resumption",
        "risk_ceiling_is_guaranteed": False,
        "paper_or_live_risk_engine_ready": False,
        "emergency_exit": "not specified or authorized; market exits may exceed target loss and need separate review",
    },
    "evaluation_governance": {
        "predefined_failure": ["negative_baseline_net_after_costs", "negative_double_cost_net_after_costs", "data_integrity_failure", "unresolved_position", "risk_rule_violation"],
        "primary_endpoint": "terminal_liquidation_net_USDT_return_on_prospective_data",
        "secondary": ["max_drawdown", "trade_count", "gross_turnover", "fees", "worst_UTC_day_mark", "passive_comparator_return"],
        "minimum_observation": "60 contiguous future days is admission only, not statistical sufficiency",
        "sample_uncertainty": "report trade count, regime concentration and uncertainty; no statistical confidence claim when insufficient",
        "reuse_of_examined_2025_2026_archives_for_model_selection": False,
        "independent_human_signoff": "REQUIRED_NOT_PRESENT",
        "simulation_review_authorization": "REQUIRED_NOT_PRESENT",
    },
    "unresolved_blocks": ["real_exchange_filters_and_market_order_rules", "account_fee_tiers",
                          "partial_fills_dust_and_restart_reconciliation", "independent_review",
                          "paper_live_loss_limit_enforcement", "prospective_out_of_sample_data"],
    "permissions": {
        "signal_implementation": False,
        "new_h01_backtest": False,
        "paper_trading": False,
        "live_trading": False,
        "automated_orders": False,
    },
}


def canonical_bytes():
    return json.dumps(AMENDMENT, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def audit_amendment(spec=AMENDMENT):
    if spec != AMENDMENT:
        raise ValueError("unregistered H01-v2 specification mutation")
    if any(spec["permissions"].values()):
        raise PermissionError("BTC-022 cannot authorize execution")
    rules = spec["immutable_h01_parameters"]
    if rules["lookback_completed_bars"] != 1200 or rules["long_target_fraction_of_equity"] != "0.20":
        raise ValueError("original H01 controls altered")
    if spec["risk_design"]["risk_ceiling_is_guaranteed"]:
        raise PermissionError("false daily-loss guarantee")
    return {
        "program": "BTC-022",
        "specification_hash_sha256": hashlib.sha256(canonical_bytes()).hexdigest(),
        "audit_decision": "REVIEW_REQUIRED_NO_SIMULATION_OR_TRADING",
        "unresolved_blockers": list(spec["unresolved_blocks"]),
        "permissions": dict(spec["permissions"]),
    }


def main():
    parser = argparse.ArgumentParser(description="BTC-022 specification-only contract")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = {"specification": AMENDMENT, "review": audit_amendment()}
    Path(args.output).write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    print(json.dumps(report["review"], indent=2))


if __name__ == "__main__":
    main()
