# BTC-070 — Offline Fixture Parser Negative-Control Review and R1 Security Evidence Assessment

**Decision: GO for frozen invented-fixture testing only. NO GO for external JSON, real data, HTTP requests, backtests or orders.** This is an internal review/test record; **not** independent security acceptance.

## Verified GitHub integration

- PR #59 was **already merged into PR #58's feature branch** when reviewed. It could not be retargeted as an open PR.
- PR #58, still OPEN at the start of this review, was merged to `main` as `ccf23abbc5a33d117c073c88e0e15c935b523458`, integrating the BTC-068 and BTC-069 code together.
- Merged-main Actions run `45180387857` passed **468 tests**.
- BTC-069 records owner's dated, explicitly narrow `APPROVE_OFFLINE_IMPLEMENTATION_ONLY` for invented BTCUSDT-shaped JSON fixtures. This does not override BTC-028/039, and BTC-018 still retires SMA 5/20 paper/live candidates.

## Reviewed BTC-069 implementation

`btc_engine/r1_offline_synthetic_json.py` generates three invented 12-element kline arrays for 1h and 4h, from fixed in-module literals. Public fixture gateway `review_frozen_fixture` validates SHA-256 equality with the frozen bytes before attempting structural parsing. It does not load files, make an HTTP call or process genuine exchange data.

Internal `_validate_json_klines` applies small caps (8,192 bytes; up to four rows), finite numeric and OHLC checks, millisecond interval alignment, matching close time and contiguous open times. It is an **internal utility** and can parse arbitrary bytes when directly invoked by tests; it is **not security-qualified to receive external or authentic JSON**.

## Expanded negative controls

The new regression suite tests modified/truncated/frozen-byte variants, unsupported or cross-interval fixtures, empty and five-row payloads, Boolean integer fields, missing/unsorted timestamps, negative volume, excessive taker volumes, invalid ignored-field values, nonfinite and zero prices, no subprocess/network invocation and hard denials for real data or trading.

**Explicit residual gaps:**
- No independently identifiable, dated, signed security review.
- No actual bounded HTTPS/TLS/DNS/redirect/rate-limited client.
- No external JSON admission; no generic malicious-response parsing certification, including excessive nesting and duplicate object keys.
- No wall-clock candle closure/finality enforcement or precise-decimal exchange numeric contract beyond float-based small fixture checks.
- No source provenance authentication, no arbitrary external market data handling, no historical strategy promotion, and no trading/risk execution enforcement.

The tests demonstrate properties of the frozen invented-fixture gateway, *not* a secure generic candle parser or production operating environment.

## Readiness decision and actionable next step

Continue limited offline fixture review within the recorded owner permission; do not call Binance or add account functions. An **independent, identifiable reviewer** must inspect the boundary code and evidence, including bypass paths, payload sizing, numeric precision, UTC finality, secure response handling, and documented residual risks before external ingestion can be proposed.

Avoid repeating NO-GO documentation without bringing new evidence. A future milestone, if approved, should address the actual residual controls for a bounded, invented-response-only handler before a separately authorized genuine public-data fetch. No inference that paper/live trading is near merely because unit-test counts increase.

No credentials, network calls, authentic data, trading, Docker launches, deployment or spending under BTC-070.
