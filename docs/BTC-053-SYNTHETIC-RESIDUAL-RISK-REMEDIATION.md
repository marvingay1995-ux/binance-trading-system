# BTC-053 — Synthetic-Only Residual Risk Remediation

**Dependency:** BTC-051 PR #40 and BTC-052 PR #41 were open at review. BTC-053 branches from BTC-052 and must be integrated only after the preceding changes reach main; review/retarget BTC-053 to main and rerun main CI.

## Executable remediation

`btc_engine/offline_fixture_verifier.py` implements POSIX-only staged publication for a **synthetic verification report**. It creates a hidden, exclusive `0600` file relative to a parent directory descriptor, writes data in bounded chunks, fsyncs the staged descriptor and creates the final filename using an atomic hard link. A pre-existing target is never overwritten. The temporary name is removed after success and on ordinary staged-write/link failures. The Windows fallback remains path-based exclusive creation and is **not equivalent assurance**.

`tests/test_btc053_report_hardening.py` checks positive publication, collisions, existing symlinks, symlinked parent, simulated partial write/ENOSPC, link failure and deterministic final-link collision. These are **synthetic mock/fault tests**, not a filesystem stress audit or durable-storage certification.

## Not resolved

- **R48-01 root/ancestor TOCTOU:** parent ancestor ownership and concurrent rename safety have not been independently proven.
- **R48-02 network sandbox:** no kernel-enforced network denial, namespaced filesystem, seccomp or privilege drop added. BTC-050 Python instrumentation is not a sandbox; this PR deliberately makes **no claim** of OS isolation.
- **R48-03 processing scale:** only two frozen invented CSV/ZIP fixtures (200KB max) are accepted; 25MB/50MB/100k rows/30-second limits remain unvalidated.
- **R48-04 authenticity:** no source publisher proof; SHA-256 matches invented source-controlled bytes only.
- **R48-05 output durability:** stronger POSIX collision/partial-write behavior is demonstrated, but no tested parent-directory fsync, crash recovery, hostile writable directory adversary, platform parity or multi-process stress.
- **R48-06 errors:** modeled read/write/link errors covered; unmodeled OS errors and process termination remain.
- **R48-07 Windows:** unverified path fallback; no claim of platform parity.
- **R48-08 private parsing:** public verifier accepts frozen golden hashes only.

**Decision:** GO for further synthetic-only testing and narrowly scoped report publication, NO GO for arbitrary or real Binance files, H01 signals/backtesting, account/API credentials, paper/testnet/live trading, deployment and spending. Historical BTC-028/039 permission denials remain unchanged.

**Next:** BTC-054 — Verify integration into main, test report path/cleanup and evaluate whether an OS network sandbox is feasible in a dedicated synthetic-only CI environment. Do not imply the latter is implemented in BTC-053.
