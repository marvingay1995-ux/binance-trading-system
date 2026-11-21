# BTC-020 — H01 trend-condition specification freeze

**Status:** Proposed, versioned strategy specification for independent review only. No signals executed, no data examined, no performance claim, no backtesting authorization, no paper/live trades.

## Decision context
BTC-019 registered trend-condition (H01) and volatility-control (H02) research concepts. BTC-018 retired both SMA 5/20 baseline strategies from trading consideration. BTC-020 selects **H01 only for specification drafting**, *not* for investment or trading.

The canonical machine-readable specification is `btc_engine/trend_registration.py`. Its normalized JSON SHA-256 is printed by its report command and will be associated with the PR merge commit for audit. Any post-review change must receive a new version and re-approval.

## Frozen proposed rule H01-v1
- BTCUSDT Binance Spot, 4h bars, long-only, no leverage/futures/shorts.
- Trend basis: simple 200-calendar-day mean of closing prices = exactly **1,200 latest completed 4h candles**.
- At each new 4h candle open, observe only prior *completed* bar closing price and the last 1,200 completed 4h close prices. If flat and close exceeds its SMA, hypothetically enter long at the next open; if long and the completed close is at or below its SMA, hypothetically exit at next open. Equality means exit or remain flat; no same-candle data.
- When fewer than 1,200 completed bars are available, remain flat with no signal. Historical data already analyzed may serve as indicator *warmup* only, never a new untouched performance sample.
- Hypothetical entry targets 20% of marked equity, never exceeding the existing 30% maximum-exposure guard; starting modeled capital 100 USDT; no borrowing. Other portfolio positions and active intrabar risk enforcement are **not supported**.
- Modeling assumptions *only*: 0.10% fee/side, 0.05% slippage/side, 0.01% half-spread/side, with 1x/2x/3x cost sensitivity. These are not authenticated current account fees or exchange filters.
- No actionable live order instructions; realistic quantity, market conditions, partial fills, restart recovery, intrabar 2% stop guarantees and reliable loss limits are unresolved.

## Prospective evaluation plan — not yet authorized
- Preserve pre-registered prospective observation start **2026-12-01 00:00 UTC** and minimum **60 complete days**, with provenance and data continuity checks.
- Compare to cash/no-trade and a risk-matched passive BTC baseline; define exact comparator conventions *before any approved test*.
- Report returns after hypothetical fees/spread/slippage, drawdown, closed trade count, costs and worst observed UTC day.
- Reject for further consideration if baseline or 2x cost return is negative, if risk-matched passive comparison has better maximum drawdown, or if the data are incomplete.
- Passing any rule does not qualify the strategy for trading; 60 days is a minimum gate, not proof of a persistent advantage, and multiple subsequent independent periods may be needed.
- H02 remains a concept; there is no combined or optimized strategy.

## Next decision gate
Independent review must verify indicator alignment, warmup sourcing, specific comparator definitions, how a 2% daily loss cap would be safely modeled, and all execution assumptions. Only a separate explicit authorization may permit a strictly offline research backtest. BTC-020 itself provides neither engine implementation nor promotion.

**Binding decision:** REVIEW ONLY — DO NOT BACKTEST OR TRADE.
