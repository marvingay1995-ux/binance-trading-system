# BTC-025 — Data Provenance Verification Readiness

**Decision: READINESS REVIEW COMPLETE; DATA-ONLY VERIFIER NOT YET AUTHORIZED.**
No H01 implementation, offline strategy backtesting, Binance API interaction, paper trading or real-money trading.

## Baseline and reviewed material

BTC-024 PR #12 merged at `2c3fd188e1208b742d04402b26ac75117ada385f` on 2026-11-21. Its `btc_engine/simulator_architecture.py` only checks **manifest metadata shape**. It neither opens the referenced datasets nor verifies hashes against bytes nor authenticates the declared source. BTC-023 denied offline H01 research authorization; that decision remains in force.

The new `btc_engine/provenance_readiness.py` is **requirements bookkeeping and a non-executing report generator**, not the candle-file verification module. It defines 12 outstanding evidence items and binds them to the unchanged canonical H01-v2 specification SHA-256.

## Three distinct evidence stages

| Stage | Proof possible once independently implemented | Status now |
| --- | --- | --- |
| 1. Metadata/manifest shape | Required fields, timestamps, aligned declared periods, hash syntax, registered spec SHA | BTC-024 has a shape validator; no content authentication |
| 2. Local byte and candle integrity | Recompute raw ZIP digest from raw bytes; independently parse CSV/JSON; canonicalize records; verify canonical digest, every OHLC and each contiguous aligned UTC 4h timestamp | Not implemented, no dataset inspected |
| 3. Source provenance/authenticity | Corroborate publisher records/checksums and download provenance, document retrieval time, original source URI and chain of custody, flag equivocation or upstream revisions | Not established and cannot be inferred from a source URL |

A valid-looking SHA-256 string does not prove any bytes were downloaded or verified; a matching locally computed digest proves file identity relative to an expected hash, **not** that the source is authentic.

## Data partition and finality

Warmup requirement: 1200 consecutive *completed* BTCUSDT 4h bars beginning **2026-05-15 00:00 UTC** and ending with the **2026-11-30 20:00 UTC** opening bar. The exclusive warmup end is December 1 00:00 UTC. This warmup is not a fresh out-of-sample result.

Prospective observation begins **2026-12-01 00:00 UTC**. Sixty complete days end no earlier than **2027-01-30 00:00 UTC**. Until that point the proposed prospective minimum is not met. Reject an unclosed final candle, an overlap with the warmup, gaps, duplicates, malformed OHLC, invalid timestamp units and any hash mismatch.

## Minimum data-only verifier design

1. Read explicitly supplied **local** files only, cap bytes/rows/ZIP expansion, reject archive traversal/bombs and unexpected entries. No network download and no credentials.
2. Recompute raw SHA-256 and byte count; preserve the original byte stream and immutable chain-of-custody record.
3. Normalize timestamp units explicitly: Binance Vision recent archives may use microsecond UTC timestamps, while earlier files can use milliseconds. Never guess silently; enforce an explicitly documented timestamp-unit contract for each source file.
4. Validate open time alignment and exact +14,400,000 ms increments. Require finite positive OHLC, coherent high/low ordering, nonnegative volume, no duplicates and no missing first/final candle.
5. Specify deterministic canonical JSON ordering, numeric representation, serialization and encoding; compute canonical SHA-256 and bind it to raw source digests and source period identifiers.
6. Distinguish independently corroborated publisher provenance from self-declared `source_uri`; record `UNVERIFIED` rather than claim authenticated status if corroboration is unavailable.
7. Emit **data-integrity-only** reports with explicit unresolved evidence; never calculate H01 signals, P&L, trading recommendations, or strategy metrics.

## Test and decision requirements

Negative controls for modified bytes, fraudulent digest, malformed ZIP, incorrect timestamps, a 1199-row warmup, invalid OHLC, duplicate/gapped/misaligned bars, an unclosed prospective candle, source revisions, mixed timestamp units, oversized inputs, and manifest tampering.

Approval to *implement* the data-only verifier, if granted in a separate program, must be narrowly scoped to explicit local input and static evidence reports, with review of code and threat model. It does **not** grant permission to collect future data automatically, invoke Binance, implement H01, run a backtest, paper trade, or place any order.

## Current limitations and next action

No genuine raw dataset or source authentication was performed in BTC-025. All 12 evidence checks remain open, including independent review and verifier implementation authority. Production exchange filters, fees, partial fills, state recovery and hard intraday limits continue to block actual order execution separately.

**Proposed next gate: BTC-026 — Local Provenance Verifier Implementation Authorization Review.** This would decide whether to permit a **data-only, local-file** verifier with hard I/O and no-network boundaries. It must not authorize a trading engine.
