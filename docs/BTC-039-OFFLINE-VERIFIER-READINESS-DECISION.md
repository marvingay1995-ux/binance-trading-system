# BTC-039 — Offline Verifier Readiness Decision

**Decision: NO GO for local CSV/ZIP market-data verifier implementation at this point.** This is a review-only decision, not a request to delay or abandon synthetic research.

## Checked repository state (November 22, 2026)
- `main` commit `da139ff65d447d804359a7c1c82ebdb2e6fb0efe` contains BTC-036 and earlier.
- BTC-037 PR #26 was still **OPEN**, not merged into `main`.
- BTC-038 PR #27 was **MERGED INTO BTC-037'S FEATURE BRANCH**, not into `main`. Its branch merge SHA was `2d32328b96a43fda9d336dd70b7533c2b142acc9`.
- GitHub Actions passed **225 tests** on that BTC-037 feature-branch SHA. This does not establish passing main-branch integration.

## What the tests do and do not prove

BTC-036 creates nine invented CSV/ZIP/JSONL fixtures. BTC-037 adds twelve small S01–S10/S15–S16 synthetic scenario byte sequences. BTC-038 contains small controlled **harness checks** for S11–S14/S17–S18: test-only expansion counter, unsupported ZIP-method library behavior, simple symlink refusal, generator output-collision rejection, monkeypatched network/process functions, and a tiny record counter.

Those are useful, executable research artifacts. They **do not verify an actual market-data verifier**, prove production-scale ZIP resource caps, prevent filesystem races, demonstrate an OS sandbox, or establish publisher authenticity. The 18 registered scenarios are not 18 successful tests of a verifier.

## Blocking findings
1. Merge dependency: PR #26 remains open; BTC-038 is not on main.
2. Missing verifier runtime: file/ZIP protections have not been built or validated against hostile inputs.
3. Unverified production resource caps (25 MB raw, 50 MB expansion, 100,000 records, 30 seconds).
4. Unverified atomic file safety, isolation and output-report handling.
5. No independent publisher corroboration or authenticated real market data.
6. Previous BTC-028 authorization record still denies implementation; owner approval and independent security evidence requirements are outstanding.

## Reconsideration checklist
- Merge PR #26 and verify the synthetic suite on `main`, including BTC-038.
- Freeze the scope and paths of a **separate** read-only verifier implementation proposal.
- Provide a measurable constrained negative-test plan for the real resource limits and path isolation.
- Preserve separate content integrity and publisher authenticity statuses.
- Record attributable owner authorization for the specific offline verifier scope, with explicit security-review limitations and without granting data/trading access by inference.

**No-go is narrower than the entire trading project:** continued offline research and synthetic fixture refinement can proceed. H01 strategy implementation/backtests, Binance API access, credentials, paper/live execution and automated orders all remain unauthorized.

## Recommended next milestone
**BTC-040 — Merge-State Reconciliation and Offline Verifier Scope Proposal**. Resolve feature-branch-to-main dependency first and prepare one concise, bounded verifier implementation proposal for a separate owner decision. Do not construct the verifier or process real BTC data under BTC-039.
