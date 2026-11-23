# BTC-069 — Owner-approved R1 offline invented-JSON implementation

## Owner decision (November 23, 2026)

> For BTC-068, I explicitly approve R1 offline-only implementation and tests using invented BTCUSDT 1h/4h JSON fixtures. No Binance network requests, authentic data ingestion, API credentials, backtesting, paper/live orders, Docker execution, or spending. Record this narrow owner decision and proceed subject to the required security controls.

**Decision: APPROVE_OFFLINE_IMPLEMENTATION_ONLY**, attributable to the owner in the current ChatGPT conversation. This authorizes only the invention and processing of small, fixed JSON test fixtures and offline validation logic; it is **not** an authorization for authentic market data, an HTTP client contacting Binance, CSV/ZIP verifier scope, signals, trading, or spending.

## Repository dependency

BTC-068 PR #58 was **open** when this branch was created; its push/PR CI passed with **456 tests**. BTC-069 is based on BTC-068's head and should initially target that feature branch. Merge #58 into main, verify main CI, then retarget BTC-069 onto main and verify its CI before merging. There is no right to alter BTC-028/039 historical denials by inference.

## Exactly what was implemented

- `btc_engine/r1_offline_synthetic_json.py`: pure-Python static, embedded invented kline-array fixtures for BTCUSDT 1h and 4h shape. Prices are **invented** and are not authentic BTCUSDT market prices. The only externally available parsing gateway admits exact frozen fixture bytes with SHA-256 match; arbitrary input is rejected.
- No input file path, no network adapter, no URL loader, no credentials, no Docker, and no order functionality.
- Enforce strict JSON structure (12-element kline rows), UTC-millisecond aligned contiguous open/close times, completed candle structure, finite price/volume fields, OHLC consistency, row and byte ceilings; report only raw digest and synthetic coverage.
- Negative tests cover corrupted input, payload mismatch, malformed JSON/shape, timestamp units, duplicates/gaps, nonfinite values, altered OHLC, forbidden activities and scope consistency.
- This is an offline **security and format prototype**; it is not a complete independently reviewed HTTPS client, actual network security barrier or a provenance authenticator. Unverified caller data never becomes valid through the mock/test interface.

## Still gated

- Independent reviewer identity/sign-off and HTTPS/TLS/redirect/DNS policy evidence remain missing. Do not claim independent review from passing automated tests.
- No request to `data-api.binance.vision`; no Binance market file/ZIP; no H01, paper or Spot orders.
- The owner-approved offline fixture experiment does not change previously recorded real-data or Docker authority.
- Future decision: review fixture-bound logic and threat model; separately authorize a bounded offline HTTP-response handler (still no network) and then an actual read-only GET only after independent security acceptance and distinct explicit approval.

## Success criterion

Green Python CI and deterministic offline fixture validation without any operational capability expansion. Next milestone may be **BTC-070 — Offline Fixture Parser Negative-Control Review and R1 Implementation Security Acceptance**.
