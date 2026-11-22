# BTC-051 — Synthetic Security Fault-Injection Tests

**Reviewed baseline:** BTC-050 PR #39 merged to main at `bfee4cbd4e7b732297ce67a723710ea9d7859490`. This milestone uses controlled BTC-036 invented fixtures, not actual market-data files.

## Executable controls

- Inject `EIO` into `os.open`, `os.fstat`, and `os.read` in the synthetic verifier's `_safe_read` and assert deterministic `INPUT_IO_ERROR` refusals, with descriptor-close instrumentation.
- Simulate interrupted/zero-byte reads and assert `INPUT_CHANGED` instead of a successful hash result.
- Inject `subprocess.TimeoutExpired`, launch `OSError`, nonzero child exit, invalid JSON, and falsely positive trading/network isolation claims into the BTC-050 probe. Reject them with stable codes, not authorization.
- Test exclusive report collision preserving a sentinel file. Observe missing-output-directory failures without pretending crash-safe atomic output has been implemented.
- Retain positive known-fixture validation and historical BTC-028 real-data/trading NO-GO.

## Remediations in this PR

1. `btc_engine/offline_fixture_verifier.py`: unknown file descriptor I/O `OSError` now fails closed with `INPUT_IO_ERROR`. Existing mapped symlink/path refusal codes are unchanged.
2. `btc_engine/synthetic_isolation_probe.py`: subprocess timeout and launch errors now raise deterministic `SYNTHETIC_CHILD_TIMEOUT` and `SYNTHETIC_CHILD_START_FAILED`, respectively.
3. `tests/test_btc051_synthetic_fault_injection.py`: direct executable negative controls.

## Evidence limitations

These are reproducible **mocked errors**, not physical disk failures, adversarial penetration tests, genuine process sandboxing, network namespace tests, memory-pressure certification or realistic market-data verification. Closing one exception-mapping gap does not prove safe file handling under hostile local concurrency. Report publication remains path-based and is not independently proven atomic. Filesystem race coverage is narrow and POSIX CI-centric. Parent process timeout does not establish all descendant cleanup in arbitrary adversarial code.

**Strict prohibitions maintained:** no general verifier, unknown or real BTC/USDT files, publisher authenticity claims, Binance network/API/credentials, H01 strategy/backtesting, paper/testnet/live orders, automated execution or deployment. BTC-028/039 decisions remain unchanged.

## Next

BTC-052 — Residual-Risk Reassessment and Synthetic Evidence Acceptance Decision: compare verified merged CI with R48-01–R48-08 and explicitly leave OS isolation, real-data provenance and unsupported operating systems open.
