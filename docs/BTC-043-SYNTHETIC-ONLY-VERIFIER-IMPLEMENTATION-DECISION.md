# BTC-043 — Synthetic-Only Offline Verifier Implementation Decision

**Decision: EXACT SCOPE PROPOSED. NO GO for implementation until a separate, explicit owner approval of this file-level scope.**

## Baseline and evidence

BTC-042 PR #29 is merged into `main` at `0c174f37b7ab6d883e3081c8569a410d16399cd5`. BTC-037 through BTC-039 are also on main. The BTC-042 proposal establishes a narrower **invented-data-only local verifier** as a possible development next step, without modifying BTC-028/039's historical NO-GO decision.

The original BTC-028 required independent human review for the **general market-data verifier**. An AI-assisted review and passing synthetic tests do **not** satisfy that standard. An invented-only test harness is a different, strictly limited possible development scope; its approval must be an attributable, explicit owner action, not inferred from this PR's title or merge.

## Exact proposed next implementation files

1. `btc_engine/offline_fixture_verifier.py`: read-only validator for locally generated `SYNTHETIC_NOT_BINANCE_DATA` CSV/ZIP, rejecting unlabeled or untrusted input.
2. `tests/test_offline_fixture_verifier.py`: deterministic positive/negative cases using BTC-034 through BTC-038 synthetic examples; bounds checked at below/exact/over limits where practical.
3. `docs/BTC-043-OFFLINE-FIXTURE-VERIFIER-EVIDENCE.md`: outcomes, fixture SHA-256, limits, environment, and independently identifiable residual risks; never claim real-market authentication.

A proposed follow-up branch is `feature/btc-044-synthetic-only-verifier-implementation`, to be created **only after** scoped approval.

## Required boundaries

- Strictly offline and local; no Binance API, sockets, subprocess execution, credentials, exchange packages, real BTCUSDT archives, or H01 indicator/return calculations.
- Only a configured input root containing generated synthetic fixtures; no arbitrary file picker. No extraction from ZIP. Reject symlinks/special files and unsafe ZIP members.
- Reject malformed CSV, duplicates, gaps, timestamp misalignment, invalid OHLCV and corrupted content. Separate raw-file SHA-256, canonical-data SHA-256 and *unverified* publisher provenance.
- Enforce bounded reads and fail closed. Proposed limits inherited from BTC-027 (25MB raw, 50MB expanded, 100K candles, 4KB row, 100:1 ZIP ratio, 30 seconds) are **not yet validated as safe production guarantees**.
- No overwriting existing evidence files, and no deployment or trading activation.

## Missing authorization and evidence

- Explicit owner acceptance of **these exact three implementation paths**, synthetic-only data restriction and all exclusions.
- Reviewed fixture expected outcomes and accepted bounded test plan with well-defined memory/CPU assumptions.
- Proof of an enforceable offline runtime isolation design for later claims of secure arbitrary-file handling.

**Outcome:** BTC-043 records the decision requirements only. It builds no verifier, processes no real or synthetic file with verifier logic, opens no trades, and changes no historical authorization switches.

## Next action

Review and merge BTC-043, then expressly approve an invented-only implementation for **BTC-044**, if desired. Approval of BTC-044 would not relax BTC-028/039 prohibitions on a real-data verifier or any trading-related capability.
