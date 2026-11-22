# BTC-052 — Residual-Risk Reassessment and Synthetic Evidence Acceptance Decision

**Decision: CONDITIONALLY ACCEPT existing synthetic-only evidence. NO GO for real data and trading.**

## Snapshot and chain of evidence
- Reviewed `main`: `bfee4cbd4e7b732297ce67a723710ea9d7859490` (BTC-050, PR #39, merged).
- At review time BTC-051 PR #40 is **OPEN**, targeting main. Its branch CI run [45039910593](https://github.com/marvingay1995-ux/binance-trading-system/actions/runs/45039910593) passed **305 tests**. That is **not a main test count**.
- Last verified main test count before BTC-051 is **294**. BTC-052 is based on the BTC-051 feature branch and must be merged **after** BTC-051.
- Historical BTC-028 and BTC-039 NO-GO gates are unchanged. Program claims and historical reviews must remain time-of-review snapshots; no retroactive rewrite.

## Evidence accepted
- Source-controlled invented `golden.csv` and `golden.zip` accepted only when both names and raw hashes match. Content integrity never implies publisher provenance.
- BTC-047/048: POSIX directory-relative file-opening, controlled symlink replacement tests, 200KB file cap, 8KiB read chunks, bounded synthetic CSV/ZIP checks and no-overwrite report tests.
- BTC-050: isolated Python child interpreter, real Linux CPU/address-space process limits, parent wall timeout and deterministic race simulations. It is *not* an OS network sandbox.
- BTC-051: passing branch negative tests for injected EIO on `os.open`, `os.fstat` and `os.read`, incomplete reads, subprocess timeouts/launch errors, malformed child responses and report collisions.

## Residual risk reassessment
| ID | Risk | Reassessment |
|---|---|---|
| R48-01 HIGH | TOCTOU | **OPEN, partially tested**. Two deterministic POSIX symlink/race cases; hostile root/ancestor concurrency not proven safe |
| R48-02 HIGH | OS isolation | **OPEN**. Python mocks and `-I -S` do not prevent sockets, process spawning or filesystem escape by hostile code |
| R48-03 HIGH | Production resource bounds | **OPEN**. 200KB invented files only; proposed 25MB/50MB/100k rows/30s remain unvalidated |
| R48-04 HIGH | Publisher identity | **OPEN**. No corroborated Binance authenticity, owner authorization or independent security assessment for real data |
| R48-05 MEDIUM | Report durability | **OPEN**. Collision tests, no fully atomic/crash-safe directory-confined publication |
| R48-06 MEDIUM | Error mapping | **OPEN, partially tested**. BTC-051 catches modeled I/O and child failures, but ENOSPC/partial writes and other platform faults remain |
| R48-07 MEDIUM | Windows parity | **OPEN**. CI tests focus on Linux/POSIX; Windows fallback not security verified |
| R48-08 MEDIUM | Parser scope | **OPEN, scope clarified**. Public verifier only processes frozen invented bytes; internal parser negative tests are not general-file assurance |

## Authorization and next gating steps
**Accepted:** Keep and improve synthetic-fixture tests and bounded research. Accept the 305-test branch run as narrowly scoped evidence, **conditional on merging BTC-051 and verifying fresh main CI**.

**Not accepted:** Arbitrary/real BTC/USDT CSV/ZIP files, publisher source authenticity, general data processing, Binance API/credentials, H01 signals/backtesting/optimization, paper/testnet/live orders, deployment, spending or independent security certification.

**Required sequence:** merge PR #40; verify the new main SHA and full CI; then retarget/merge the BTC-052 PR with a fresh main CI run and record new observations in a new evidence update if needed.

**Recommended next milestone:** BTC-053 — Synthetic-Only Residual Risk Remediation, prioritizing actual OS network isolation design and safe output publication, while keeping all market-data and trading authority disabled.
