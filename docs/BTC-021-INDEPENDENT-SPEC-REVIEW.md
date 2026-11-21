# BTC-021 — H01-v1 specification audit and readiness decision

**Decision: BLOCKED.** BTC-020 is an immutable, proposed design document; it is **not ready** for strategy implementation, backtesting, paper trading, or live trading.

## Method and scope
Inspected `btc_engine/trend_registration.py` and `docs/BTC-020-TREND-SPECIFICATION.md` on the merged `main` branch following PR #8. The accompanying `btc_engine/spec_audit.py` performs a deterministic contract audit and emits a source-spec fingerprint. It is an **automated internal review**, not independent external assurance, not market data analysis, and not proof that the proposed rules produce positive returns.

The audit deliberately does **not edit** BTC-020's frozen version, execute an indicator, calculate trade signals, connect to Binance, retrieve candles, or run a backtest.

## Findings: blockers

| ID | Finding | Required action |
| --- | --- | --- |
| DATA-002 | 1,200-bar 4h SMA requires ~200 consecutive days of warmup before December 1, 2026; provenance, exact source range and first eligible evaluation instant unspecified | Register continuous warmup-only source and hashes; explicitly forbid counting warmup as fresh out-of-sample returns |
| SIGNAL-001 | Prose describes next-open fills but lacks normative index alignment and ambiguous equality/entry timing checks | Specify exact bar-index formulas and deterministic completed-candle invariants |
| SIZE-001 | 20% equity sizing does not specify Decimal rounding, fees, min notional, dust, insufficient budget or shared-portfolio exposure | Freeze sizing and unavailable-order behavior |
| COMP-001 | “Risk-matched passive BTC” lacks allocation, rebalancing, fees and benchmark start/end conventions | Freeze mathematically reproducible comparator |
| RISK-002 | 2% daily-loss enforcement is not possible solely from 4h bar-open checks; market gaps can exceed limits | Separate reported historical losses from enforceable operational loss controls |
| EXEC-001 | Exchange rules, account-specific fees, partial fills, restarts and reconciliation unverified | Ground filters in authenticated source and specify realistic failure modes |
| EVAL-001 | 60 days of observations may provide too few trades or insufficient regimes; independent review and uncertainty plan absent | Register evaluation method and escalation requirements before observing data |
| AUTH-001 | BTC-020 prohibits new strategy implementation/backtesting | Seek a separately approved protocol and explicit simulation authorization after blockers are addressed |

An unauthorized flag, unexpectedly changed indicator, altered prospective boundary or excessive modeled target exposure would be flagged as additional structural blockers.

## Evidence to preserve
- Source PR #8, merged BTC-020; use canonical `specification_report()` SHA-256 to identify this exact version.
- BTC-017 archive run #44915102425 is a **retired SMA 5/20 benchmark**. It cannot be used to establish H01 profitability.
- BTC-015 prospective boundary remains 2026-12-01T00:00:00Z with a minimum 60 complete days; that is a data-admission rule, **not** an automatic approval or proof of edge.
- BTC-018 retirement of the prior SMA 5/20 1h and 4h strategies remains binding.

## Review decision and next program

BTC-021 explicitly **does not** select or change H01's 1,200-bar horizon, position size, or trading costs. Corrective proposals must become a **new version**, reviewed before any evaluation. BTC-022 should prepare a specification-completion amendment, including exact pseudocode and comparator definitions, then request review; it must not quietly authorize trading.

**No paper, live, or even new H01 backtest execution is authorized by this review.**
