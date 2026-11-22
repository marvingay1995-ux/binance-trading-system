# BTC-036 — Synthetic Fixture Generator Implementation

**Implementation:** deterministic **invented-only** CSV, JSONL and small ZIP fixtures generated with standard-library Python. This scope is the narrow implementation the product owner requested as "BTC-036 — Synthetic Fixture Generator Implementation" following BTC-035.

**Baseline:** BTC-035 PR #24 merged as `a36e9cb8e2b53e4d01b9f5e55e480714ddaaa400`. The earlier BTC-035 file is a historical no-authorization record and remains unchanged. This milestone records the owner's new request as approval for this **synthetic-only implementation**, not a retroactive change to BTC-035 or any real-data approval.

## Exact files
- `btc_engine/synthetic_fixture_generator.py`: produces a bounded deterministic inventory, optionally writing into a caller-selected **new absolute directory** only.
- `tests/test_synthetic_fixture_generator.py`: local golden digest, ZIP bytes, write, refusal and provenance-label tests.
- `tests/fixtures/synthetic/README.md`: fixture inventory and repeatable manual generation instructions.
- This document, describing capabilities and exclusions.

## Generated inventory
`golden.csv`, `golden.jsonl`, `golden.zip`, `duplicate_timestamp.csv`, `nan_ohlc.csv`, `negative_volume.csv`, `changed_bytes.csv`, `unsafe_member.zip`, and `unclosed_candle.csv`. Every output has `SYNTHETIC_NOT_BINANCE_DATA` in the generated manifest, alongside byte lengths and SHA-256 values. ZIP metadata and entry ordering are deterministic. No ZIP extraction is performed. The unsafe name is test data, never used as a filesystem path.

This is a **starter fixture subset**: not all BTC-034 S01–S18 scenarios are implemented, and none has been run against the future market-data verifier. These tests prove deterministic fixture creation only, not security protection against hostile files.

## Restrictions
No network, Binance credentials, real market candles, H01 strategy, backtesting, paper/live orders, or market-file verifier. Each generated item is bounded to 200,000 bytes, far below the proposed BTC-034 budgets. Output refuses existing directories and symlink parents. Generation does not claim sandboxing against a malicious local actor racing directory creation; it should run in an isolated, controlled CI temporary directory.

**Next:** expand synthetic-only coverage and create a separate decision before any general local file verifier or real market-data processing.
