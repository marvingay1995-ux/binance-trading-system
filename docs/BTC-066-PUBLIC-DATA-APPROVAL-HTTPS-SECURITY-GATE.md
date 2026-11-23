# BTC-066 — Public Market-Data Approval and HTTPS Ingestion Security Gate

**Decision: NO GO for live HTTP requests or authentic BTCUSDT ingestion.** BTC-066 establishes an owner/security approval checkpoint and offline URL-scope verification, but does not implement an HTTPS client or fetch data.

## Verified merged-main baseline
- BTC-065 PR #55 merged to `main` at `67adc7ddfd2f63a16f86491099eebec1805537de`.
- Merged-main GitHub Actions run `45177402725` passed **424 tests**.
- BTC-065 approved only source/provenance *design*. It did not grant public data acquisition.
- BTC-028/039 remain historical NO GO for their respective local verifier scope. BTC-018 retired SMA 5/20 variants; BTC-064 R1–R4 remain off.

## Proposed read-only data request (requires new express approval)

- Binance public **market-data-only** base: `https://data-api.binance.vision`.
- A future client could request `GET /api/v3/klines` for `BTCUSDT`, intervals exactly `1h` or `4h`. No API keys, signatures, private account routes or orders.
- Proposal limits: at most **500 candles/request** and **one request/minute** (not yet implemented or exercised); update/reconfirm official weights, terms and jurisdiction eligibility before operational use.
- For a hypothetical future client: HTTPS with valid TLS verification, strict exact-origin allowlist, no permissive redirects, no credential headers, bounded decompression and JSON bytes, 5-second deadline, UTC millisecond timestamps, completed-bar/finality and continuity checks, error logging and safe retries.
- Provenance record: request params, source and retrieval time, HTTP status, raw bytes count/digest, parser/schema version, candle UTC range, coverage and missing/duplicate status. Record publisher corroboration `UNVERIFIED` unless separately authenticated.
- Do not treat string parsing in BTC-066 as SSRF prevention for an eventual network implementation. DNS resolution, redirects, TLS, retries, and actual server responses are untested.

## Evidence and owner decision pending

| Gate | Review finding |
| --- | --- |
| Attributable, dated owner approval specifying **R1 only** | Not yet supplied; asking to implement BTC-066 is not itself the narrow approval |
| Independent security reviewer identifiable and signed-off | Not evidenced |
| Data access terms, regional access and rate weights | Pending implementation-time verification |
| HTTPS client threat model and bounds | Requirements drafted, not independently accepted |
| Synthetic response and timestamp negative controls | Not developed for the real client |
| Provenance, retention and secrets review | Incomplete |

The new Python module `btc_engine/readonly_https_approval_gate.py` validates **only an offline hypothetical URL** (exact HTTPS hostname, path, BTCUSDT symbol, 1h/4h intervals, bounded limit). Its decisions keep `http_calls`, `real_market_data_ingestion`, `authenticated_binance_api`, `h01_strategy_backtests`, `paper_trading`, `live_trading`, `order_execution`, and `docker_execution` all false. Even fake owner/reviewer claims cannot override these flags.

## Next decision point

**BTC-067 — Explicit Owner R1 Authorization and Independent HTTPS Security Review Record.** Collect a dated owner statement that authorizes, at most, a single narrowly bounded public keyless endpoint implementation, plus identifiable security findings and conditions. If incomplete, record NO GO. Do not authorize an implementation, fetch real data or activate trading by merging this PR. Do not pretend an AI-assisted checklist is an independent security assessment.

This does **not** allow Binance keys, order endpoints, external CSV/ZIP handling, H01 execution/backtesting, paper/testnet/live trades, Docker execution, spending or deployments.
