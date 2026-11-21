# BTC-019 — New strategy hypothesis registration (research only)

## Context and authority
BTC-018 has retired the 1h and 4h SMA 5/20 candidates from paper/live consideration. BTC-017's archive run #44915102425 verified a fixed-SMA 4h last-window baseline return of +0.6167% that flipped to -0.5826% with doubled simulated trading frictions; 1h baseline was negative. These are previously observed historical data, **not** fresh validation data.

No new candidate is selected, traded, optimized or backtested here. All possible strategies require independent specification and review before code or backtesting may begin. This document is a hypothesis *concept* registration, **not** a fully frozen executable trading strategy registration.

## H01 — Trend-condition concept
**Question:** Could exposure conditioned on a long-term upward trend reduce losses in sustained declines versus a no-trade or risk-matched comparator?

**Potential drawback:** The condition could miss reversals or introduce whipsaw costs.

**Not specified:** Which trend measure, bar alignment, threshold, order rules, exits, and handling of missing data. No parameters have been selected or tested.

## H02 — Volatility-control concept
**Question:** Could volatility-aware exposure reduce downside tails after fees, slippage and spread?

**Potential drawback:** Excessive turnover and missed upside.

**Not specified:** Volatility estimator, sampling window, threshold, sizing formula, order rules, exits, or missing-data handling. No parameters have been selected or tested.

## Preregistration protocol for a future project
Before implementing/backtesting either candidate, separately freeze the complete signal rules, rationale for each parameter unrelated to already viewed BTC-011–014 performance, execution assumptions and failure conditions, and hash the specification. Separate research/development data from genuinely unseen evaluation data. Preserve the December 1, 2026 starting prospective period as potential future observation, but do not treat it as an independently untouched performance test if examined or used during design.

An explicit second review must authorize *research simulation* before any new hypothesis backtesting. Passing such a gate does **not** authorize paper or live trading.

## Disallowed progression
- Do not repurpose retired SMA 5/20 as a new candidate or quietly change its thresholds.
- Do not imply that the 2025-11 through 2026-10 archives provide untouched future evidence.
- Do not create orders, exchange sessions, credentials, a portfolio executor or automatic trading schedule.
- No claims of profitability, win probability, or 2% daily-loss enforceability without independent supporting evidence.

**Current default:** `DO_NOT_TEST_OR_PROMOTE`. Both new entries are explicitly `CONCEPT_ONLY_NOT_PARAMETERIZED`. Next requested action should be deciding which idea deserves a **complete preregistered specification**, not pretending either is profitable.
