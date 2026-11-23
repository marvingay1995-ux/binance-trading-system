# BTC-071 — Offline HTTP Response Handler and Security Hardening

**Decision: GO for frozen invented response-envelope tests only. NO GO for real HTTP, arbitrary external JSON, authentic data or trading.**

## Verified baseline

- BTC-070 PR #60 merged into `main` at `38f29cac5054bfe4f9dddb7ed68cf7fcc465371b`.
- Merged-main CI `45181072519` passed **480 tests**.
- Owner's explicit November 23, 2026 decision remains `APPROVE_OFFLINE_IMPLEMENTATION_ONLY` for invented BTCUSDT 1h/4h JSON fixtures and tests. All other approvals remain denied.

## Implementation and controls

The new module `btc_engine/r1_offline_http_response.py` simulates an *in-memory* HTTP-style envelope. It is not an HTTP transport or client. The only successful body payloads are byte-for-byte registered BTC-069 synthetic fixtures verified by SHA-256; no arbitrary user response, CSV/ZIP, file or Binance response is accepted.

It enforces a strict synthetic envelope (status **200**, exactly `content-type: application/json` and correct `content-length`, no redirects/extra headers, no non-byte or oversized payload). It applies existing kline shape/continuity controls and checks the last candle against a **fixed invented UTC clock**; caller-supplied clocks are refused. Checks do not depend on actual current time or external data.

13 new negative-control tests cover statuses, nonstandard headers, response size and type, swapped or modified synthetic body, spoofed clock, malformed envelope, unsupported intervals and no process/network/file calls. No imports of HTTP client frameworks or sockets into the implementation.

## What this does *not* validate

- HTTPS TLS/certificates, DNS resolution, redirect behavior, actual response compression, rate limiting, retry logic and network failure handling remain untested because no network-capable code exists.
- SHA-256 proves equality with the frozen *invented* payload, not independent source provenance.
- UTC candle finality is checked only against a fixed test clock and on fixed invented data, not an actual exchange/server clock.
- The BTC-069 structural utility still relies on Python floats for invented numeric values; Decimal-safe authentic-exchange handling is not qualified.
- This is not an independent reviewer sign-off or security certification, and no actual public market data is fetched.

## Next critical decision

Review this bounded test handler and obtain independent security acceptance and **separate explicit authorization** before implementing any generic response-admission gateway or outbound keyless market-data fetch. Further tests alone do not imply permission for authentic data analysis, backtesting, paper or live orders.

No network, real data, credentials, H01, trading, Docker execution, deployment or spend.
