# BTC-065 — Read-Only BTCUSDT Data Scope, Authorization and Provenance Design

**Decision: R1 SCOPE PROPOSED, NOT APPROVED. Do not fetch authentic candles or start backtesting.** This milestone is a non-executing decision contract and ten regression tests.

## Verified integration and inherited restrictions
- BTC-064 PR #54 merged into `main` at `76ea2274965c8bce8facd3ac57d5facc35fc33f2`.
- Merged-main Actions run `45176833564` succeeded with **414 tests**.
- BTC-028 still says `NO_GO_LOCAL_VERIFIER_IMPLEMENTATION`, BTC-039 remains a historical verifier no-go, and BTC-064 R1–R4 all remain unauthorized.
- BTC-018 retires SMA 5/20 1h/4h from paper/live consideration. Historical inspected data cannot count as fresh holdout evidence.

## Proposed narrow source for separate approval: public keyless Spot REST

Official Binance Spot REST documentation identifies `https://data-api.binance.vision` as a market-data-only base origin and supports public GET kline queries. BTC-065 recommends it over opening hostile local ZIP files for an *initial future* R1 permission request, **not** because independent authentication or production security is already proven.

- **Request shape:** `GET https://data-api.binance.vision/api/v3/klines` with explicitly validated `symbol=BTCUSDT` and either `interval=1h` or `interval=4h`.
- **Proposal limits (not approved):** ≤500 rows/request, ≤1 request/minute, bounded time windows and response bytes, 5-second timeout, no API key or signed authentication, no private or order endpoints. Reconfirm currently published endpoint rates, restrictions and geographic availability before implementation.
- **Timestamp contract:** public REST JSON times default to milliseconds unless a different time-unit header is used; require default milliseconds and reject ambiguous units rather than guessing.
- **Redirect and TLS:** exact hostname allowlist, validated certificates, no redirects outside approved source, no credentials in headers or logs.
- **Data finality and correctness:** UTC timestamps, interval alignment, completed-only bars, OHLC/volume sanity, no gaps/duplicates, bounded JSON parsing, reproducible canonicalization.
- **Evidence:** raw response SHA256, response byte count, request parameter record, time, source URI, HTTP status, timestamp unit, candle count, gaps, audit checksum, explicit `publisher_provenance_status=UNVERIFIED` until independent corroboration.
- **No strategy/return calculations:** R1 outputs source, integrity and coverage metadata only, not H01 signals, candidate rankings, P&L, recommendations or simulated orders.

## Alternative: official public archive

Official [Binance public-data README](https://github.com/binance/binance-public-data) describes daily/monthly Spot archives, CHECKSUM sidecars, and Spot timestamps in **microseconds for data from January 1, 2025 onward**. Archive-checksum matching verifies integrity against that published checksum, not independent publisher authenticity; handling ZIP/CSV introduces the separate bounded decompression, path, parser, revision and provenance review under BTC-025/028/039. **Not selected for the first permission request.**

## Source material verified in BTC-065 research
- [Binance official Spot REST API documentation](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md)
- [Binance official market-data-only guide](https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md)
- [Binance public-data README](https://github.com/binance/binance-public-data)
- [Binance public datasets terms](https://github.com/binance/binance-public-data/blob/master/TERMS_AND_CONDITIONS.md)

These external pages were consulted as **public documentation only**. No market endpoint or download URL was called. Terms, authorization and endpoint implementation still need a fresh review before R1.

## Explicit approvals still missing
1. Dated attributable owner approval for **only** bounded public keyless BTCUSDT 1h/4h market-data acquisition, excluding exchange account access, orders, and strategy runs.
2. Independent security assessment of proposed HTTPS JSON ingestion, limits, storage, source trust and failure handling, with clear reviewer identity/evidence.
3. Licensed/regionally compliant source use, immutable schema/request contract and lossless provenance; no side effects beyond approved read-only data handling.
4. Separate future R2 authorization for any novel backtest. R3 paper trading and R4 live Spot each require their own approvals and evidence.

## Next decision
**BTC-066 — Explicit R1 Public Data Approval and HTTPS JSON Ingestion Safety Gate.** The gate should ask for a precise owner decision, ensure security preconditions are documented, and only then consider implementing a small, independent read-only fetcher. The presence of BTC-065 code or a merged PR must not imply that permission was granted.

**Not authorized:** outbound market requests, authentic market-data ingestion, H01/backtesting, Binance keys/account access, order execution (paper/testnet/live), Docker execution, spending or infrastructure deployment.
