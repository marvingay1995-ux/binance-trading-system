# BTC-050 — Synthetic Runtime Isolation and File-Race Testing

**Baseline:** PR #37 merged to main at `dee8ef908e2373e973c3c548e269e530ab0aeb9f` and PR #38 merged to main at `89380d6ffc689f04a68d6e3dd4462942216ff064`. GitHub Actions run `45039311802` passed **286 tests** on that main revision.

## Executed work
- `btc_engine/synthetic_isolation_probe.py` launches an isolated Python interpreter (`-I -S`) against only source-controlled, invented BTC-036 `golden.csv` or `golden.zip`. Child process receives a stripped environment and uses Python-level socket and subprocess instrumentation.
- On Linux only, child sets real OS `RLIMIT_AS` (256 MiB), `RLIMIT_CPU` (4 seconds), and `RLIMIT_CORE=0`. Parent applies a 5-second wall timeout through `subprocess.run`; child status and authorization flags are checked.
- `tests/test_btc050_synthetic_runtime_races.py` deterministically swaps known synthetic file or input root to symlinks at the point of `os.open`, checking POSIX `O_NOFOLLOW` refuses the substitution. This is deterministic fault injection and does not prove full TOCTOU resistance.
- Tests assert unapproved fixture names and relative roots are rejected before spawning a child.

## Evidence boundaries and residual risks
- **Not an OS network sandbox.** Python monkeypatches, Python isolated mode, and environment filtering cannot prevent a malicious interpreter or native code from creating sockets. `os_network_isolation_verified=false` must remain explicit until independently verified kernel/container network-denial policy is deployed.
- **Not full privilege isolation.** Child still runs with runner's user privileges and inherits the basic accessible filesystem, subject to its host configuration. The program does not implement chroot, namespaces, seccomp, or sandbox profiles.
- **Not complete filesystem race immunity.** The two controlled POSIX substitution tests do not cover attackers renaming parent directories repeatedly or a concurrently writable source file.
- **Not production memory/CPU certification.** Linux resource caps demonstrate child process bounds for small invented data only, not safety for the proposed 25 MB raw / 50 MB ZIP / 100,000 candles / 30 seconds production limits.
- **Not publisher authentication.** `golden.csv` and `golden.zip` are invented bytes. Authentic Binance archives, H01 signals/backtesting and all trading remain unauthorized.
- Windows subprocess verification may run without POSIX resource limits; platform-specific security parity remains unverified. Linux-specific caps are honestly reported as null elsewhere.

## Decision
**GO** for synthetic-only regression research and bounded demonstration. **NO GO** for real market-data verification, exchange API or credentials, H01 backtesting, simulated orders and live/automated trading. Historical BTC-028 and BTC-039 gates remain untouched.

## Follow-up
BTC-051 should expand controlled synthetic fault-injection of failed descriptor reads, stat failures, parent timeout and output collisions, with explicit measured results. Real data remains outside scope.
