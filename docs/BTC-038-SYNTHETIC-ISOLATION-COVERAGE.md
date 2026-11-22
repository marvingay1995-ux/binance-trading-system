# BTC-038 — Remaining Synthetic Security Coverage & Isolation Testing

**Status:** Six remaining S11–S14 and S17–S18 scenarios receive **bounded local harness probes only**. There is still **no real-data verifier** and no verified end-to-end hostile-file refusal.

## Dependency
BTC-037 PR #26 was open when BTC-038 was prepared; BTC-038 is a dependent PR based on the BTC-037 feature branch, not directly on main. Merge BTC-037 first, then retarget/rebase BTC-038 to main. Do not merge BTC-038 before its dependency.

## Checks and exact limits
- **S11 expansion:** Create a 256-byte repetitive invented payload in a tiny ZIP, reject using a **128-byte test-only streamed cap** and accept at 256 bytes. This is NOT a test of the proposed 50 MB production cap.
- **S12 compression:** Patch method 99 in a tiny synthetic ZIP's local and central headers; verify the Python standard library rejects reading it. This tests standard library behavior, not a future verifier.
- **S13 paths:** Create a temporary symlink and test a simple path-based refusal. This does NOT protect against TOCTOU or prove safe file-descriptor opening.
- **S14 output collision:** Verify that the BTC-036 generator refuses an existing directory and does not overwrite a sentinel file.
- **S17 network/process:** Patch socket creation, network connections and subprocess launch during generation, failing the test on attempted calls. This is an instrumentation test, not an OS sandbox or universal denial of external capabilities.
- **S18 records:** Check 99, 100 and 101 invented iterator entries against a **100-entry test-only cap**; demonstrate a fail-fast counter without creating 100,001 rows. This does NOT prove the proposed 100,000-record verifier limit.

All tests are offline, require no accounts or credentials and generate only small controlled synthetic inputs. CI can validate these probes but does not certify file-verifier security.

## Security decision
The BTC-034 S01–S18 registry now has twelve small generated artifacts and six additional bounded probes. **Not all 18 cases are materialized fixture bytes, and none has been executed against an actual market-data verifier.** The reported security verdict remains `SYNTHETIC_HARNESS_CHECKS_ONLY_VERIFIER_NOT_IMPLEMENTED`.

**No changes to BTC-028/029 authorization blocks:** market archive verification, H01 backtesting, Binance access, testnet/paper/live trading and automated orders all remain prohibited.

## Subsequent step
Only after merged dependency and reviewed evidence, decide whether to propose a separate offline market-data verifier scope. No implementation approval is inferred from these passing synthetic tests.
