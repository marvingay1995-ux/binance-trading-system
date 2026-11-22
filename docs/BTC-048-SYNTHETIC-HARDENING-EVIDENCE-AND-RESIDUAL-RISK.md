# BTC-048 — Synthetic Hardening Verification and Residual Risk Review

**Review-only decision: synthetic regression evidence accepted with limitations; real-data verifier remains NO GO.**

## Exact repository merge state
- BTC-046 PR #33 merged to main as `2763e5d0389fabd13d9b3ba694ac1b470832cbee`.
- BTC-047 PR #34 merged into `feature/btc-046-synthetic-security-boundary-review` at `3d933898d47de1448c2bf7833fb52d3f40e9a2a1`, **not into main**.
- That feature branch passed **279 repository tests** in GitHub Actions run `45037460415`. Do not describe it as a main-branch CI run.
- Integration PR [#35](https://github.com/marvingay1995-ux/binance-trading-system/pull/35) was opened to bring BTC-047 into main. Merge and recheck it before concluding integration is complete.
- BTC-048 is based on the branch containing BTC-047 and must follow its integration. Its new tests are evidence checks, not verification of arbitrary files.

## Verified synthetic controls
- Strict filenames `golden.csv` and `golden.zip`, with exact source-controlled, invented payload SHA-256.
- POSIX directory-relative open using `dir_fd`, no-follow where supported, regular-file and descriptor stat checks.
- Input read chunk length bounded to 8 KiB; total fixture raw bytes capped at 200,000.
- CSV physical line bound before parsing and restricted numeric schema, no multiline quoted fields.
- ZIP single flat stored member; bounded metadata sizes and byte reads, with CRC checking through the standard Python library.
- Output collision refusal for reports; existing evidence file preserved.

## Residual risks (not closed by passing CI)

| ID | Severity | Finding | Required evidence for further expansion |
| --- | --- | --- | --- |
| R48-01 | HIGH | Root and output-parent checks are still path-based and may race with a malicious local actor; root trust and dirfd approach not independently stress-tested | Supported-OS adversarial TOCTOU and ownership tests; directory-fd output design |
| R48-02 | HIGH | No OS-level network/process sandbox. Monkeypatched socket/subprocess tests do not prove global isolation | Separate unprivileged, no-network process with enforced filesystem and resource policy |
| R48-03 | HIGH | 200KB allowlisted invented inputs are unlike arbitrary 25MB/50MB ZIP/CSV files; 100,000 records and 30s ceilings remain unproven | Measured bounded streaming tests in a restricted runtime with explicit peak memory/CPU |
| R48-04 | HIGH | No independently corroborated Binance origin; local hashes verify **only local integrity** | Separate provenance chain and owner/security authorization for real market files |
| R48-05 | MEDIUM | Report writer checks symlink parents before exclusive path creation and is not an atomic confined publication transaction | Dirfd-rooted exclusive output and crash/error/retry tests |
| R48-06 | MEDIUM | Python `os.read`, `os.fstat`, output writes and decoding can raise unclassified OS/resource exceptions; not every error is fail-closed with a stable error code | Fault injection and error-mapping policy before widening supported input |
| R48-07 | MEDIUM | Windows fallback lacks POSIX dirfd/no-follow equivalence; test coverage here is Linux CI only | Windows-specific boundary tests and explicit platform scope |
| R48-08 | MEDIUM | Parsing helpers may be called on invented malformed bytes, but public verifier refuses non-golden content by hash before parser | Separate general-parser security review; never infer it from frozen-golden-path tests |

## Decision and restrictions
**GO:** retain and improve the allowlisted synthetic-only fixture verifier, CI regressions and internal design review.

**NO GO:** accept arbitrary files, process real BTC/USDT candles, fetch Binance data, claim publisher authenticity, run H01 signals/backtesting, authorize paper/testnet/live orders or change BTC-028/039 historical gates.

This is AI-assisted technical evidence, **not** independent human security certification. A successful test run is not a blanket security approval.

## Immediate next action
Merge PR #35 (integration of BTC-047), validate merged `main` CI, then retarget/review BTC-048's PR against `main`. Keep the real-data boundary closed.
