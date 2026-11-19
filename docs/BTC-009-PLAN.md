# BTC-009 — Strategy recovery and independent validation

**Stage:** proposed / not implemented. **Execution:** research and simulation only.

## Goals
Investigate the reported BTC-008 holdout failure, reconstruct a deterministic research foundation, and evaluate whether any strategy deserves further paper trading.

## Scope
1. Rebuild read-only public Binance BTCUSDT market-data ingestion for 1h and 4h candles with pagination, timestamp validation, deduplication and missing-candle checks.
2. Implement reproducible backtesting with fees, spread, slippage, minimum notional, lot-size and step-size constraints. No look-ahead, survivorship or future-data leakage.
3. Establish a frozen baseline strategy and configuration before running holdout tests; record all changes and avoid repeated optimization on holdout data.
4. Use chronological train/validation/untouched holdout splits and walk-forward evaluation; include trending, ranging and high-volatility regimes.
5. Report net P&L, maximum drawdown, win rate, profit factor, trade count, exposure, fees, turnover, and performance versus buy-and-hold and no-trade baselines.
6. Add negative and fault-injection tests: gaps, duplicate candles, invalid prices, stale market data, API outages, partial fills and restart/reconciliation behavior.
7. Only after independent review, advance to persistent paper-trading with daily monitoring and an audit trail. No live orders.

## Safety invariants for future implementation
- Spot only; no futures, margin, leverage or borrowing.
- Maximum total open exposure 30% of equity; default to no new order if equity or positions cannot be verified.
- Daily realized + unrealized loss limit 2% from defined day-start equity, with timezone/day boundary explicitly specified in code. Stop trading on limit breach.
- First 20 live trades require explicit user approval, but this rule is not itself authorization to enable live trading.
- Withdrawals disabled on any future API key; least privilege, IP restrictions where feasible.
- Fail closed on stale data, missing filters, inconsistent balances, reconciliation errors, API errors, or unexpected orders.
- No credentials, live order placement, deployments, or paid infrastructure in BTC-009.

## Exit criteria
- Independent reproducible test suite and documented inputs/configuration.
- Out-of-sample performance reported with uncertainty, fees and realistic constraints.
- No unresolved safety-critical defects or unverified exchange filters.
- Explicit go/no-go review for paper trading; **live trading remains blocked** regardless of backtest outcome.

## Unknowns to resolve
Original algorithm, trade ledger, test data, source code, dependency versions, exchange filter snapshot, previous PRs and CI results are unavailable. No historical tests have been rerun here.
