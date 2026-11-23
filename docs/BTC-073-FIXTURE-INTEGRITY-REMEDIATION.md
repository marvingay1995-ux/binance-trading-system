# BTC-073 — Synthetic Fixture Integrity Remediation and Parser Boundary Hardening

**Decision:** restricted invented-fixture testing remains the only permitted input. No external JSON/HTTP, authentic data, strategy backtest or trading authorization.

## Dependency
BTC-072 PR #62 is still open on `main` at implementation time. BTC-073 branches from its feature branch and PR must target BTC-072 until that dependency merges. BTC-071 merged into `main` as `cfb8cdf6f45f73c4bf3e6a2f9d7488d15dffecba`; merged-main CI `45184893342` passed **493 tests**. The BTC-072 branch CI passed **504 tests**, but this is not main-branch integration evidence.

## Source-grounded remediation
- `btc_engine/r1_pinned_fixture_integrity.py` independently pins literal SHA-256 digests for the two invented 246-byte kline fixture bodies. Its `MappingProxyType` prevents normal dictionary assignment to approved digest values.
- The BTC-069 `review_frozen_fixture` and BTC-071 `invented_response` / `review_invented_response` entrypoints now compare the body against those pinned digests; a mutated `SYNTHETIC_FIXTURES` entry no longer becomes the trusted baseline.
- BTC-072's regression that demonstrated the in-process mutation weakness now expects a fail-closed `PermissionError`; separate BTC-073 controls cover both intervals, integrity pins, attempted substitutions and unsupported inputs.
- **Trust limitation:** in-process arbitrary Python execution can still monkeypatch module symbols and functions. This fix protects against accidental or incidental registry mutation under the current tested boundary, not a process-level adversary with code execution.
- `_validate_json_klines` is still an internal structural utility that can parse arbitrary caller bytes; it has **not** been authorized or qualified to ingest outside market data. No general external parser was added.

## Remaining genuine blockers
- Independent, identifiable security review of actual future implementation remains absent.
- Real TLS/DNS/redirect, rate/time/response size, compressed bodies, clock finality and decimal precision for outside data are not implemented or reviewed.
- No approval for genuine Binance data, exchange credentials, strategy signals or backtests, paper/testnet/live orders, Docker execution, deployment or spending.

## Next
First merge BTC-072 to main, verify integrated CI, then retarget BTC-073 to main and validate its CI before merging. To advance beyond frozen invented fixtures, obtain a **separate scoped authorization** and independent security review for external JSON admission and any genuine public-data fetch. Repeating internal reviews will not substitute for that evidence.
