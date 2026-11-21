# BTC-023 — H01-v2 Specification Acceptance and Offline Research Authorization Review

**Formal decision: specification partially accepted as a proposed design, NOT accepted for research implementation or offline backtesting. No paper or live trading.**

## Review provenance and precise scope

BTC-022 (PR #10) was merged on 2026-11-21 at commit `b9b4b86b79569a7fa38508344da9494423063444`. The merged main-branch unit-test workflow succeeded. The reviewed source is `btc_engine/spec_amendment.py` (H01-v2) plus `docs/BTC-022-SPEC-COMPLETION.md`. The audit is implemented as a separate non-executing `btc_engine/spec_acceptance.py` module; its report records the canonical specification SHA-256.

This is an **internal document and code-contract review**, not a third-party independent technical audit. No real historical-market evaluation of H01 has been performed and no result establishes profitable expected returns.

## Acceptance matrix

| BTC-021 finding | BTC-023 decision | Explanation |
| --- | --- | --- |
| DATA-002 | Design recorded; evidence outstanding | 1,200 complete 4h bars, 2026-05-15 through 2026-11-30 UTC, provenance and hash rules are specified, but warmup inputs are not independently sourced and verified |
| SIGNAL-001 | Proposed rule is sufficiently explicit for further review | Last completed close `close[i-1]` and `SMA = sum(close[i-1200:i])/1200` at `open[i]`; tests asserting strings are not execution-level no-lookahead proofs |
| SIZE-001 | Design recorded; execution incomplete | Decimal fee-inclusive budget, step flooring and refusal rules are specified, but real exchange rules, dust and all fill outcomes are unresolved |
| COMP-001 | Comparator defined with qualification | No-rebalance passive BTC at 20% *initial notional* and a cash comparator; not dynamically equal-risk and requires separate comparator implementation tests |
| RISK-002 | Blocker remains | 2% UTC-day loss is an objective, **not** a guaranteed hard stop or verified operational limit |
| EXEC-001 | Blocker remains | Actual exchange filters, fees, partial fills, failure/recovery behavior and account reconciliation not verified |
| EVAL-001 | Blocker remains | Prospective 60-day minimum admits data but is not sufficient for statistical power or market regime diversity; independent human review missing |
| AUTH-001 | Blocker remains | No approved scope or explicit authorization to implement or run a new H01 offline strategy simulator |

## Offline research permission gate

**Authorization requested by program title, not granted by this audit.** A new explicit review decision is required before writing an executable strategy simulator or running H01 backtests.

Required evidence: (1) independent human sign-off on the exact SHA-256 H01-v2 contract; (2) source-manifest and continuity verification of the complete 1,200-bar warmup; (3) narrow simulator specification and negative-control tests; (4) realistic simulated-fee/filter/quantity treatment or documented limits; (5) signed decision separating strictly offline simulations from paper/live permissions.

Even if a future offline simulation is approved, it cannot activate Binance credentials, testnet, automatic Spot orders, or any actual funds. Production risk controls would require a distinct later authorization.

### Critical unresolved ambiguity

The H01 trend-entry budget is `min(20% equity, free cash)` while the proposed passive benchmark buys 20% *initial equity* once without rebalancing. This is **initial allocation matching**, not perpetual risk matching. The comparator label must not imply equivalent realized volatility or risk. A later evaluator must use the precise mathematical conventions from BTC-022 and must not optimize on already-examined holdouts.

## Next program

BTC-024 should prepare the separately reviewable **offline simulator architecture and evidence package**, with no implementation and no test execution of H01 market data until required approval. It should specify reproducible, immutable input manifests, deterministic bar-index checks, isolated cash accounting, explicit fill-rejection behavior and provenance of simulated filters. The path to H01 simulator authorization remains **blocked pending independent sign-off**.

**BTC-023 decision: NO GO for offline H01 strategy backtesting, paper and live trading.**
