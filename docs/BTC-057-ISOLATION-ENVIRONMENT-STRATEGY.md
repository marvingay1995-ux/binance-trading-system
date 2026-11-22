# BTC-057 — Isolation Environment Capability and Enforcement Strategy

**Result: NO GO for current runner as a verified OS sandbox.** This milestone is documentation/policy/tests only and does not provision containers, VMs, credentials or networking.

## Verified merged-main evidence
- BTC-056 PR #46 merged into `main`, SHA `f65da28e6cbe5c988971588d7c8a2d7b4a0d733b`.
- Merged-main GitHub Actions run `45046604431` passed **342 tests**.
- The actual `BTC056_ACTUAL_PROBE` value reported **`ENFORCEMENT_UNAVAILABLE`**, with `reason=UNPRIVILEGED_NAMESPACE_DENIED`. Its `kernel_egress_denial_observed=false`, `cpu_memory_limits_observed=false`, `filesystem_isolation_verified=false`, `comprehensive_network_isolation_verified=false`.
- Thus the runner cannot establish a usable namespace through the currently tested unprivileged invocation. This is not a comprehensive determination that all GitHub-hosted isolation options fail.

## Candidate execution environments

| Candidate | Status | Decision |
| --- | --- | --- |
| Re-run unprivileged `unshare` on the same hosted runner | Directly tested; denied | Not a useful next proof without a changed environment |
| Existing preinstalled rootless container runtime | Not inspected or executed | Preferred **evaluation candidate** if already available, explicitly authorized, and no privileged/paid action required |
| Existing disposable Linux VM | Not inspected or executed | Alternate candidate only after availability, operator authority, network policy and cost confirmed |
| CI container jobs with no network | Not inspected or executed | Evaluate provider constraints without inventing capability; no credential or runner changes in this milestone |
| Windows restricted job/runtime | Unverified | Outside Linux-first BTC-057 evaluation |

## Enforcement acceptance criteria

All required for a future **synthetic-only** sandbox experiment:

1. OS-enforced IPv4 and IPv6 egress denial, with safe negative controls and no external traffic; no reliance on Python socket monkeypatches as sole enforcement.
2. Non-root identity, no added capabilities, no-new-privileges, bounded descendant processes and PID/CPU/memory/wall-time limits.
3. Trusted frozen invented fixtures mounted read-only; unrelated repository secrets or host files unavailable; output directory separated from input.
4. Output refuses overwrites and handles failures; cleanup and race behavior tested under the actual runtime.
5. Signed or independently reproducible environment evidence: runtime version, policy, OS, exit status, negative-test results, resource metrics and CI commit.
6. Every unsupported condition fails closed. CI green without actual enforcement must be labeled **unavailable**, never a security pass.

No candidate is selected or approved by BTC-057; this is an inventory-first recommendation.

## Remaining risks and next gated work
- P0: real OS network restriction, process/privilege isolation, filesystem confinement, hostile path races and resource stress.
- P0: actual Binance publisher authenticity and independent security review remain absent, and are **outside synthetic scope**.
- P1: Windows parity and crash-safe output behavior.
- **Next possible BTC-058:** evaluate pre-existing container/VM capabilities without provisioning, then explicitly authorize a narrowly scoped disposable synthetic-only enforcement test if technically possible.

**Explicit prohibitions:** no real Binance files/API/credentials, H01 signals/backtests/optimization, paper/testnet/live orders, automated trading, privileged CI settings, new deployment, external services, downloads or spending. BTC-028/039 NO-GO remains unchanged. The review is AI-assisted, not an independent security audit.
