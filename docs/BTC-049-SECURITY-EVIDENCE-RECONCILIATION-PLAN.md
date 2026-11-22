# BTC-049 — Integrated Security Evidence Reconciliation and Residual Risk Remediation Plan

**Decision: synthetic-only research GO; general/real-market verifier and all trading NO GO.**  
**Repository snapshot (2026-11-22):** `main` at `f4fb636a585a2a4c91813f452464edceb9a02e39`. This is a timestamped observation, not a live-computed status.

## Verified GitHub integration and evidence

| Milestone | GitHub state at review | Evidence |
|---|---|---|
| BTC-046 / PR #33 | Merged into main | Merge `2763e5d0389fabd13d9b3ba694ac1b470832cbee` |
| BTC-047 / PR #34 | Merged into BTC-046 feature branch | Branch merge `3d933898d47de1448c2bf7833fb52d3f40e9a2a1` |
| BTC-047 integration / PR #35 | Merged into main | Merge `f4fb636a585a2a4c91813f452464edceb9a02e39`; GitHub Actions run `45038764454` passed **279 tests** on main |
| BTC-048 / PR #36 | Merged into BTC-046 feature branch, NOT into main | Branch merge `2c9ed330dcaa3197b608aafc879a3623f1a121ac`; run `45038793682` passed **286 tests** on feature branch |
| BTC-048 integration / PR #37 | Opened as a corrective integration PR | Must merge to main and rerun checks before stating BTC-048 is integrated |

**Do not conflate a GitHub PR marked “merged” with “merged into main.”** The base-branch distinction is material. Reinspect main and GitHub Actions after PR #37 merges. Historical BTC-039 fields are time-of-review snapshots and should not be silently rewritten as current state.

## Security claims grounded in the current code

- `btc_engine/offline_fixture_verifier.py` accepts only the known invented `golden.csv` and `golden.zip`, bound to source-controlled SHA-256. It does not authorize arbitrary market-data files.
- BTC-047 uses a POSIX `dir_fd` input open, best-effort no-follow and file-stat checks; a strict ~200 KB synthetic input cap, max 8 KiB `os.read` calls, pre-parsing physical CSV line bound, ZIP metadata/cumulative byte checks, and no archive extraction.
- BTC-048 extends instrumentation checks for read sizes, changed descriptors, symlink parents and report collision; they passed on the feature branch only at review time.
- Python mocked-network tests **are not OS-level isolation**; neither synthetic checks nor the CI test count establish secure processing of unknown or authentic Binance market data.

## Prioritized residual-risk register

| ID | Priority | Status | Contained next work (invented files only) | Closure evidence needed |
|---|---|---|---|---|
| R48-01: filesystem TOCTOU | P0 | Open | Test dirfd path confinement and malicious symlink/race scenarios in disposable temp roots; freeze trusted-root ownership assumptions | Reproducible OS-specific attack tests, unchanged source-hash gate |
| R48-02: runtime isolation | P0 | Open | Build an unprivileged no-network synthetic test subprocess/harness under supported CI OS; explicitly prohibit process/credential access | Enforced network denial, child process and privilege tests, not Python mocks alone |
| R48-03: parser/resource bounds | P0 | Open | Add bounded synthetic streaming/CSV row and ZIP size/failure instrumentation; do not generate true ZIP bombs | Measured memory/CPU/time ceilings, below/exact/above boundary cases and fail-closed behavior |
| R48-04: provenance | P0 real-data gate | Open | Specify separate raw integrity vs publisher authenticity evidence only | Authenticated source chain and separate authorized review; cannot be closed by synthetic fixtures |
| R48-05: report output | P1 | Open | Propose dirfd-rooted atomic/exclusive report output; collision/fault-injection/crash tests | Prove no overwrite, symlink confinement and partial-write recovery |
| R48-06: error mapping | P1 | Open | Inject read/stat/write/decode faults, map expected refusal codes, test cleanup | Deterministic errors and no orphaned descriptors/partial reports |
| R48-07: Windows parity | P1 | Open | Either constrain support to Linux/POSIX or add Windows-specific synthetic path tests | Recorded platform decision and supported-OS verification |
| R48-08: public vs private parsing | P1 | Open | Keep public frozen-hash gate; direct parser tests remain clearly labeled helpers | Never claim unknown input validation from passing golden-file checks |

**Priority is for planning only; no implementation permission beyond existing synthetic-fixture development is inferred.**

## Implementation order and review gates

1. **Integrate PR #37 into main**, verify clean diff against current main, rerun the full suite and capture exact SHA, run ID and test count.
2. **BTC-050 — Synthetic Runtime Isolation and File-Race Test Scope:** define a constrained, no-network test harness for P0 risks R48-01 through R48-03; keep no external market data, no Binance credentials and no strategy imports.
3. **BTC-051 — Synthetic Security Fault-Injection Tests:** executable negative controls and bounded observability. Distinguish observed test failures from hypothetical risks.
4. **BTC-052 — Residual-Risk Reassessment:** accept/reject changes based on fresh GitHub evidence and explicit limitations. Do not cross the real-market-data boundary without a separate owner-approved scope and the unresolved BTC-028 security assurance.

## Non-authorizations

BTC-049 is **documentation-only**. It does not modify `btc_engine/verifier_implementation_decision.py`, `btc_engine/offline_verifier_readiness.py` or historical approval records. No file verifier for arbitrary/real market data, Binance API/credentials, H01 backtest or indicator implementation, paper/testnet/live trading, automated orders, deployment or spending is authorized.

**Independent human security certification is absent**; AI-assisted findings are not substitutes. The existing synthetic-only implementation is research/test infrastructure, not a production security control.
