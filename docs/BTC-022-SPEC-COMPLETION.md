# BTC-022 — Specification Completion and Risk-Control Design

**Status:** H01-v2 proposed amendment. **No backtesting, execution, paper, or live authority.** The original H01-v1 in BTC-020 remains unchanged and source of truth until a separate signed-off decision accepts any replacement.

## Audit scope and decision

BTC-021's eight blockers were reviewed and converted into explicit design requirements. This is a specification-only completion effort. Drafting technical definitions is **not** proof that production risk or exchange execution mechanisms exist.

| BTC-021 blocker | Proposed BTC-022 treatment | Readiness |
|---|---|---|
| DATA-002 | Specify 1,200 consecutive 4h warmup bars, UTC boundary, SHA256 provenance and warmup/result separation | Proposed, provenance not collected |
| SIGNAL-001 | Normative zero-based index rules: on candle i open use last completed close i-1 and SMA(closes[i-1200:i]) | Specified, not coded or independently verified |
| SIZE-001 | Fee-inclusive Decimal sizing, floor to exchange step, cash and portfolio cap, unresolved dust and refusal rules | Proposed, real filters unavailable |
| COMP-001 | Passive no-rebalance 20%-initial-notional BTC comparator with same hypothetical entry/sell costs, terminal liquidation and cash comparator | Proposed, no computations |
| RISK-002 | Distinguish observed UTC-day equity marks from enforceable loss stops; deny entries after breaches and on unknown state, never promise 2% hard cap | Safeguard design only |
| EXEC-001 | Require authenticated filter/fee evidence, partial-fill handling, price and quantity validity, restart reconciliation | Blocked |
| EVAL-001 | Freeze baseline and cost-stress failure gates, require independent review and uncertainty/regime checks after new prospective data | Proposed, not validated |
| AUTH-001 | Leave all simulation, signal implementation, paper and live permissions false | Blocked pending separate approval |

## Normative bar alignment (design only)

At the start of 4h candle `i`, previous candle `i-1` must have closed and been verified. The current candle `i` must not contribute to the SMA or signal. Set `SMA_i = sum(close[i-1200:i])/1200`. If insufficient complete bars, remain flat. When flat, `close[i-1] > SMA_i` implies hypothetical next-open long; when holding, `close[i-1] <= SMA_i` implies hypothetical exit at that opening. Equality never initiates entry. Missing or revised bars fail closed.

Initial prospective evaluation at **2026-12-01 00:00 UTC** requires warmup 4h candle opens beginning **2026-05-15 00:00 UTC** through **2026-11-30 20:00 UTC**, uninterrupted, with per-source and canonical hashes. Data before December 1 may only warm the indicator, not create new performance claims.

## Research sizing design, not exchange-approved

For hypothetical buy: budget = min(20% of marked equity, available free cash), including projected entry fee. Compute hypothetical positive execution price as next open adjusted by fee-independent slippage and half-spread, then floor quantity to the applicable step using decimal arithmetic. Reject if cash plus fees, minimum quantity, minimum notional, or aggregate 30%-exposure ceiling fails. For sells, do not pretend dust is fully liquidated; unresolved quantity blocks any new entries until reviewed. All such filters remain **unverified**.

## Comparator and evaluation design

A 100-USDT no-trade comparator remains cash. For the passive comparator, buy 20% of the starting hypothetical equity once at the first prospectively eligible opening and never rebalance. Apply the same modeled entry costs and end-of-period liquidation costs; report mark-to-market equity before liquidation as well. This matches *initial* notional only, not time-varying risk, and must be labeled accordingly.

Minimum 60 continuous future days is a data-admission threshold, not enough evidence by itself for claims of profitability or statistical confidence. The strategy must be rejected for further consideration if baseline or 2× friction net outcome is negative, required data fail integrity, or unresolved positions/risk violations occur. Comparator outperformance and drawdown are documented, but none automatically permit real-money orders.

## Risk ceilings and lifecycle

A 2% loss limit cannot be guaranteed by bar-open checks or OHLC simulation. Gaps and illiquidity can exceed intended levels; observed worst intrabar lows are indicative rather than guaranteed executable exits. Hard paper/live safety requires separately verified pretrade, intraday risk control, halt-state persistence, fill reconciliation, stale-data fail-closed behavior, emergency-exit policy and manual recovery governance. The BTC-022 specification supplies none of these as running software.

## Outstanding review / next program

The machine-readable amendment lives in `btc_engine/spec_amendment.py` and records a canonical SHA256. It has no signal generator, order connector, market fetcher, or backtest path. An independent reviewer should verify the date boundaries, mathematical comparators, exchange filter requirements, and assumptions. The 1,200 bars must be sourced before any evaluation. No revision of the frozen BTC-020 parameters was made. Any amendment after review must be separately versioned.

**BTC-022 decision: PROPOSED SPECIFICATION — NOT EXECUTION-READY.**
