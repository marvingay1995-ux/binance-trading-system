# BTC-024 — Offline Simulator Architecture and Evidence Package

**Decision: REVIEW ONLY. No H01 signal engine, market-data backtest, paper trading, live trading, API access or credentials.**

## Source and control plane

BTC-023 PR #11 merged at commit `829994730697a300adc5825d3008f80e66bea29c`. BTC-023 explicitly denied H01 signal implementation and offline simulation. BTC-022 H01-v2 amendment remains proposed and unaccepted. This architecture is a non-executable review package; it does **not** overturn either decision.

The machine-readable architecture and **manifest-shape-only** validator are at `btc_engine/simulator_architecture.py`. The validator does not open datasets, compare their bytes to their stated hashes, authenticate network sources or check individual candles. It cannot promote an untrusted manifest to a verified evidence artifact.

## Proposed isolated components

| Component | Input | Expected output after separate authorization | Failure rule |
| --- | --- | --- | --- |
| Input boundary | immutable offline warmup and prospective files | local content digests | reject missing/changed files, no fetch |
| Provenance verifier | source manifests, SHA-256, 4h records | continuous fully verified source audit | reject gap, duplicate, bad timestamps, OHLC violations |
| Signal interpreter | 1200 completed 4h closes before open i | hypothetical binary trend eligibility | never read current candle's close or future bars |
| Accounting | 100 USDT synthetic balance, owned BTC, fees | deterministic isolated ledger | reject negative cash, overspending, unknown inventory |
| Order-size gate | Decimal prices, documented filters | hypothetical step-rounded quantity or explicit rejection | reject failed min-notional, fee-inclusive budget, stale filters |
| Fill model | proposed next-open price and cost multipliers | simulated fill/rejection, unresolved dust/partial fills | halt, never invent successful fills |
| Risk observer | UTC day start equity, marked equity and OHLC low | realized/marked loss diagnostics | log breach; never claim 2% hard ceiling |
| Comparator | cash and passive initially 20% BTC, never rebalanced | comparable terminal outcomes | mark exposure mismatch and invalid comparator |
| Evidence output | code SHA, manifest hashes, protocol fingerprint | immutable report plus conservative decision | no automatic promotion |

None of these proposed strategy components is implemented in BTC-024. The module only encodes the architecture and validates **declared metadata shape**.

## Warmup and prospective partitions

Warmup for the proposed H01-v2 must be 1,200 contiguous 4-hour candles covering **2026-05-15 00:00 UTC** to **2026-12-01 00:00 UTC** exclusively. Those candles may only initialize the indicator, not generate a new retrospective performance claim. The prospectively registered period starts **2026-12-01 00:00 UTC** and requires 60 complete days (earliest full window end: **2027-01-30 00:00 UTC**).

The manifest validator enforces declared period boundaries/counts, fixed BTCUSDT 4h market, SHA-256 syntax, H01-v2 specification fingerprint, and a default unverified status. This does **not** verify any actual data. A later, separately approved verifier needs to inspect file bytes and ensure every candle is exactly 4 hours apart, aligned, complete, with valid OHLC and strict partition separation.

## Acceptance scenarios (future, not executed)

1. Altering the current 4-hour bar's close must never alter the order decision at that bar's open.
2. Missing or duplicate timestamp / malformed OHLC / nonfinite price must reject the dataset.
3. An input whose stated SHA-256 differs from its actual bytes must fail before any strategy logic.
4. A 1199-bar warmup must not generate a signal; exactly 1200 complete bars are required.
5. Hypothetical fees plus buy notional must remain within the isolated cash balance; obey documented steps and minimums.
6. Unknown or stale filters, unresolved partial fills/dust, restart mismatches or portfolio exposure uncertainty must fail closed.
7. No reporting of pre-prospective warmup performance as an independent holdout.
8. Cash and passive-BTC benchmark arithmetic must be separately regression-tested.
9. Risk breaches and gap losses must remain visible; the 2% daily-loss objective cannot be described as enforceable from OHLC.

## Evidence still missing

The actual raw and canonical hashes of the 1,200-bar warmup, verified origin and archive continuity, any future data, authenticated exchange-filter snapshots, account-specific fees, independent human review, and an explicit narrowly scoped offline-research implementation decision. The BTC-024 JSON manifest checker is **not** substitutes for that missing evidence.

## Next review gate

BTC-025 should assess whether **a data-only offline provenance verifier** may be designed and separately authorized; the H01 strategy implementation remains blocked. A future execution/paper/live path would require additional permissions entirely separate from any market-data provenance work.

**BTC-024 decision: ARCHITECTURE FOR REVIEW ONLY — NO SIMULATION OR TRADING AUTHORIZED.**
