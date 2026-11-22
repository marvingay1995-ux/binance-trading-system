# BTC-035 — Synthetic Fixture Generator Authorization

**Decision: scoped implementation request prepared; permission NOT granted.**

## Grounding
BTC-034 PR #23 merged into main on 2026-11-22, commit `62094a8ff855ab800ef9cf8a43b82e577425d479`. Its `btc_engine/synthetic_fixture_spec.py` defines two literal invented CSV/JSONL reference rows, fixed SHA-256 digests and 18 synthetic negative scenario descriptions. BTC-034 explicitly requires *separate product-owner approval* before actual generator implementation. Merely naming BTC-035 is a request to review the authorization, not a signed approval of the exact file list.

## Request requiring explicit product-owner authorization
Approve **only** a local, deterministic, non-market CSV/ZIP synthetic test fixture generator, on a dedicated branch of `marvingay1995-ux/binance-trading-system`, using:
- `btc_engine/synthetic_fixture_generator.py` — generator limited to invented, labeled records and bounded ZIP/CSV creation
- `tests/test_synthetic_fixture_generator.py` — reference-digest, repeatability and negative-case tests
- `tests/fixtures/synthetic/` — generated invented-only reference assets, if needed for review

Use Python standard library, configured output directory, no network, no external data, no credentials. Keep fixture sizes below BTC-034 proposed limits; do not attempt to construct an unsafe or huge ZIP bomb for a test. Tests must prove the synthetic provenance label remains explicit and must not claim the future real-data verifier passes any security control.

**Not authorized under this request:** general verifier implementation, real market-file processing, Binance API/account access, SMA/H01 computation, strategy backtests, paper/testnet/live orders, or changing previous NO-GO gates.

## Authorization state
There is no recorded explicit acceptance of this exact narrowed file/scope request. The permission ledger in `btc_engine/synthetic_generator_authorization.py` therefore keeps all implementation and execution flags false. No synthetic generator, security fixture files or runnable attack cases were created in BTC-035.

## Exact next decision requested
Product owner may authorize a separate **BTC-036 synthetic-only generator implementation** after reviewing and merging this request. Any such approval must name the permitted code/fixture scope and expressly keep real data and all trading excluded.

A code-review PR merge does not implicitly grant that approval, and an AI-generated report is not independent human security certification.
