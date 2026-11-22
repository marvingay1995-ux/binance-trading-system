# BTC-046 — Synthetic Verifier Security Evidence Review and Real-Data Boundary Decision

**Decision: GO for existing allowlisted synthetic-fixture verification; NO GO for a general CSV/ZIP or real-market-data verifier.**

## Verified source and CI
- BTC-045 PR #32 merged on November 22, 2026; current reviewed main commit `b0df06e66cc7cb701df095f9a3d9abf5ebe076fa`.
- GitHub Actions run [45036068026](https://github.com/marvingay1995-ux/binance-trading-system/actions/runs/45036068026) completed successfully with **262 tests passing**.
- BTC-044 `verify_generated` accepts only `golden.csv` and `golden.zip` with hashes of exactly source-controlled invented bytes. No exchange file was verified.
- BTC-045 directly tested private `_csv_canonical`/`_zip_csv` helpers with malformed invented samples; the public entry point rejects tampered allowed filenames with `HASH_MISMATCH` before those parsers run. These are different kinds of evidence and must not be conflated.

## Risk findings requiring remediation before real-data consideration
| ID | Risk | Source evidence | Required action |
| --- | --- | --- | --- |
| B46-01 HIGH | Public verifier cannot test arbitrary external content | Frozen fixture hashes in `verify_generated` | Separate authorization for general-file verifier |
| B46-02 HIGH | Path safety not proven race-resistant | `_safe_read` uses initial path checks and `os.open` but no verified trusted root + dirfd strategy | Define supported-OS safe opening model and test races |
| B46-03 HIGH | Production resource ceilings unverified | 200,000-byte fixture cap, in-memory CSV rows, bounded test ZIP | Stress-test streaming, 25MB/50MB/100k rows/30s under hard resource limits |
| B46-04 MEDIUM | No OS sandbox evidence | Python mocks of socket/process calls | Dedicated no-network/no-process isolation |
| B46-05 MEDIUM | Report creation not fully hardened | Exclusive-create file path, no directory-fd confinement | Protected output-root and atomic report publication |
| B46-06 HIGH | Provider identity and approval missing | `publisher_provenance_verified=false`; BTC-028 NO-GO and missing signoff | Explicit owner scope decision and independently attributable security evidence for general verifier |

### Meaning of passing CI
The current tests establish regression properties for the narrowly allowlisted invented fixtures, some malformed-input handling in internal helper routines, and non-overwrite behavior. They do **not** establish independent security certification, exchange authenticity, performance profitability, OS isolation, resource-safe processing of arbitrary files, or an accepted 60-day prospective market dataset.

## Authorization boundary
Continue synthetic fixture development, documentation and regression testing. **Do not authorize or implement general CSV/ZIP market-file parsing, actual BTC/USDT file ingestion, Binance API/credentials, H01 signals/backtesting, paper/testnet/live orders, or any automated trading.** This review adds no credentials, downloads, provider, deployment or spending.

The original BTC-028 and BTC-039 decisions remain immutable historical NO-GO records. AI analysis does not satisfy their explicitly stated independent security-review requirement.

## Recommended next milestone
**BTC-047 — Offline Verifier Security Hardening Proposal (Synthetic-Only)**: take B46-01–B46-05 as targeted hardening tasks on invented bytes, with separately scoped implementation and measured evidence, without modifying the real-data boundary. Avoid writing redundant approval documentation where executable synthetic controls can be improved.
