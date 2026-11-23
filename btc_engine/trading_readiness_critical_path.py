"""BTC-064 consolidated trading readiness assessment; no market or order actions.

A critical-path *decision* is not permission to invoke market data APIs.
Historic SMA 5/20 retirement, BTC-028/039 NO_GO, Docker denial remain intact.
"""
import json

from .verifier_implementation_decision import decision_record as btc028
from .synthetic_docker_isolation_contract import contract_record as btc060
from .synthetic_image_trust_eligibility import assess_image_eligibility as btc063

VERSION = "BTC-064-v1"
REVIEWED_MAIN_SHA = "0ef335d5a6ed32f8b2999366bb031a465e9e5986"
REVIEWED_MAIN_CI_RUN = 45175767479
REVIEWED_MAIN_TESTS = 404

STAGES = (
    {
        "id": "R1",
        "name": "Separate approval: read-only public market-data research",
        "scope": "Propose narrowly scoped public BTCUSDT OHLCV acquisition and source authenticity; no account or API key",
        "gates": (
            "Attributable owner approval that supersedes only the specific read-only data embargo",
            "Source provenance, licensing, bounds, timeframes and request-rate constraints",
            "Offline reproducible source checks and independent security review appropriate to ingestion route",
            "No authenticated account, private endpoint, order API or strategy execution",
        ),
        "authorized_now": False,
    },
    {
        "id": "R2",
        "name": "New preregistered hypothesis and independent backtest",
        "scope": "Only after R1 and distinct research approval; include accurate exchange constraints and costs",
        "gates": (
            "New written hypothesis; retired SMA 5/20 1h and 4h remain benchmarks only",
            "Timestamped frozen specification and genuinely unseen prospective evaluation",
            "Realistic costs, exchange filters, minimum notionals, precision, partial fills and slippage",
            "Defensible positive out-of-sample edge with downside and sensitivity review, not guaranteed profit",
        ),
        "authorized_now": False,
    },
    {
        "id": "R3",
        "name": "Supervised simulation (paper trading)",
        "scope": "No real orders; after independent strategy and simulator evidence and separate approval",
        "gates": (
            "Idempotent simulated order state, event timing, balance and fee accounting",
            "Paper risk policies with max 2 percent daily loss and max 30 percent exposure",
            "Restart/recovery, alerting, reconciliation and emergency shutdown validation",
            "Review of sufficiently long forward paper results and failures",
        ),
        "authorized_now": False,
    },
    {
        "id": "R4",
        "name": "Controlled live Binance Spot",
        "scope": "Separate owner approval, minimum-capital executable orders; no leverage or withdrawal rights",
        "gates": (
            "Explicit order-execution permission and key-scope audit: Spot trade-only, no withdrawals",
            "Live exchange filter/fee/precision checks, partial-fill and balance reconciliation",
            "Server-side hard limits and kill switch, daily-loss and exposure validation",
            "First 20 live orders individually approved; documented operator rollback",
            "Verified live results do not imply persistent profitability",
        ),
        "authorized_now": False,
    },
)
NONCRITICAL_FOR_R1 = (
    "Docker image provenance audit for a future executable sandbox",
    "Automatic trade execution, account keys and WebSocket private feeds",
    "H01 optimization and paid infrastructure",
)
HISTORICAL_STRATEGY = {
    "strategy": "SMA_5_20",
    "decision": "RETIRED_BENCHMARK_ONLY",
    "timeframes": ["1h", "4h"],
    "basis": "BTC-018: last-window 1h -0.6653% baseline; 4h +0.6167% baseline but negative under doubled/tripled friction",
    "historical_windows_not_fresh_holdout": True,
    "paper_or_live_promotion_allowed": False,
}
LIMITS = {
    "indicative_capital_usd_less_than": 100,
    "proposed_daily_loss_limit_percent": 2,
    "proposed_max_spot_exposure_percent": 30,
    "initial_orders_requiring_manual_approval": 20,
    "leverage_authorized": False,
    "withdrawal_permission_authorized": False,
}

def critical_path_decision():
    previous = btc028()
    docker = btc060()
    image = btc063()
    if previous["decision"] != "NO_GO_LOCAL_VERIFIER_IMPLEMENTATION" or any(previous["permissions"].values()):
        raise PermissionError("BTC028_HISTORIC_NO_GO_CHANGED")
    if docker["docker_execution_authorized"] is not False or image["synthetic_execution_eligible"] is not False:
        raise PermissionError("DOCKER_EXECUTION_GATE_CHANGED")
    if any(stage["authorized_now"] for stage in STAGES):
        raise PermissionError("UNAUTHORIZED_MARKET_STAGE")
    return {
        "program": VERSION,
        "reviewed_main_sha": REVIEWED_MAIN_SHA,
        "reviewed_main_ci_run": REVIEWED_MAIN_CI_RUN,
        "reviewed_main_tests": REVIEWED_MAIN_TESTS,
        "decision": "NO_GO_ALL_MARKET_AND_TRADING_STAGES_PENDING_SEPARATE_SCOPE_APPROVAL",
        "next_recommended_milestone": "BTC-065 — Read-only public BTCUSDT data scope, authorization and provenance design",
        "priority": "Seek explicit limited approval for R1 before any authentic data acquisition; do not wait for every Docker candidate to be proven if the independently reviewed public-data research route needs no container",
        "stages": [dict(stage, gates=list(stage["gates"])) for stage in STAGES],
        "not_required_before_R1": list(NONCRITICAL_FOR_R1),
        "retired_strategy": dict(HISTORICAL_STRATEGY),
        "future_risk_limits_not_enforced": dict(LIMITS),
        "public_data_access_authorized": False,
        "local_real_data_ingestion_authorized": False,
        "h01_strategy_or_backtesting_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "binance_credentials_authorized": False,
        "orders_authorized": False,
        "docker_execution_authorized": False,
        "profitability_demonstrated": False,
    }

def require_market_or_trade_permission(*_args, **_kwargs):
    raise PermissionError("BTC064_MARKET_DATA_AND_TRADING_NO_GO")

if __name__ == "__main__":
    print(json.dumps(critical_path_decision(), sort_keys=True, indent=2, allow_nan=False))
