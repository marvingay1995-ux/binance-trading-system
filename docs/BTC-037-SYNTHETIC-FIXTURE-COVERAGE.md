# BTC-037 — Synthetic Fixture Coverage Expansion and Security Verification

**Decision:** Expanded synthetic fixture construction and inventory-integrity checks completed **for review**; no real data verifier exists. This is not a verifier penetration test or sign-off.

## Baseline
BTC-036 PR #25 merged into `main` at `da139ff65d447d804359a7c1c82ebdb2e6fb0efe`. BTC-036 generated nine invented-only examples; this milestone adds additional small fault samples in `btc_engine/synthetic_fixture_coverage.py` with executable tests in `tests/test_synthetic_fixture_coverage.py`.

## Coverage
BTC-034 defines eighteen S01–S18 potential security scenarios. BTC-037 materializes twelve **small synthetic example byte sequences** for S01–S10, S15, and S16:
- Missing or duplicate sample rows, microsecond precision error, nonfinite OHLC, negative volume, oversized CSV field, changed content
- ZIP entry traversal, ZIP symlink metadata and corrupted CRC
- An illustrative shifted close-time sample and an explicitly unverified fictional source claim

The six remaining **context-only** scenarios S11–S14 and S17–S18 are named and assigned expected results but **not executed**: ZIP expansion limit, unsupported compression, filesystem symlink input, output collision, runtime no-network isolation and over-limit record count.

Every materialized case has a SHA-256 digest, size and `FIXTURE_BYTES_GENERATED_ONLY_NOT_VERIFIER_TESTED` status. Context-only cases remain `NOT_MATERIALIZED_NOT_TESTED`.

### Security checks actually performed
Unit tests inspect the bytes and ZIP metadata, assert reproducibility, check intentional field corruption, verify that Python's standard ZIP reader detects the CRC mismatch, and enforce generated file size caps. The CRC check is **only against the standard library reader**, not against a future verifier. No archive extraction or actual market-data ingest is performed.

The security verdict remains `VERIFIER_NOT_IMPLEMENTED_NO_SECURITY_PASS` irrespective of passing tests. No ZIP bomb or oversized dataset is generated. Later implementation of a dedicated verifier would require a separately reviewed and approved scope and independent negative testing under sandbox constraints.

### Known limitations
- S01 is a reduced sample, not an actual prospective/warmup proof; S15 is a modified timestamp needing a controlled clock to produce a reliable finality verdict.
- S16 is a forged *metadata claim*, with a fake Binance-style URI; hashes do not authenticate publisher identity.
- Some fixtures are intentionally malformed and are **not** generalized adversarial coverage.
- Directory output creation is not a hardened defense against a malicious local adversary racing file creation.
- Existing historical NO-GO flags remain unchanged. This PR adds no trading or account capability.

**Next:** assess remaining S11–S14 and S17–S18 under a separate bounded fixture test authorization. Do not implement the real data verifier or H01 strategies from this PR alone.
