# BTC-058 — Isolation Runtime Capability Inventory and Selection

**Decision: NO GO for selecting a verified runtime.** BTC-058 is read-only evaluation; no container daemon is contacted, no container/VM launched, no image pulled and no credentials/provisioning/spend authorized.

## Reconciled baseline

- BTC-057 PR #47 merged into `main` at `12410dce113379a387891dcee0bc8c8bd2c23d4d`.
- Merged-main GitHub Actions run `45046974338` succeeded with **349 tests**.
- BTC-056 actually returned `ENFORCEMENT_UNAVAILABLE` / `UNPRIVILEGED_NAMESPACE_DENIED`. No OS sandbox had been proven.

## Read-only capability inventory

`btc_engine/synthetic_runtime_inventory.py` records OS type and the mere presence of `podman`, `docker`, `nerdctl`, `unshare`, `bwrap` and `firejail` on `PATH`. These checks do not run the tools and do not contact container daemons or outside networks. The CI test prints `BTC058_CI_INVENTORY=` so the *actual runner's* result can be inspected.

A CLI present on PATH **does not prove** daemon accessibility, rootless privileges, a compatible container image, policy enforcement or safety for hostile input. Podman, Docker or nerdctl CLI presence only identifies a **candidate to evaluate next**, never a selected verified runtime.

## Selection criteria for any later experiment

- Existing authorized disposable environment; no privilege escalation, paid provider or new image download implied.
- Enforced IPv4 and IPv6 egress denial (not just Python socket monkeypatch), with strictly bounded local negative controls.
- Frozen invented input bytes read-only; output separately confined; no host secrets visible.
- Non-root user, dropped capabilities, no-new-privileges, bounded CPU/memory/PIDs/wall-time and descendant cleanup.
- Reproducible runtime/policy version evidence, detailed negative-control results and explicit supported OS.
- Fail closed if any requirement cannot be demonstrated.

**Current selection:** `selected_verified_runtime=null` regardless of tool presence. This milestone selects no execution environment.

## Limitations and strict boundary

CI runner PATH metadata is a snapshot, not a host inventory outside the runner. The pre-existing `unshare` denial is specific to the test runner at BTC-056's execution. No assertion is made about available VMs, paid accounts, local hardware or provider entitlements.

No real exchange archives, Binance API/credentials, H01 indicators/backtesting/optimization, paper/testnet/live orders, automated trading, privileged CI changes, new secrets, external providers or spending. Historical BTC-028/039 NO-GO remains unchanged.

**Next:** BTC-059 — Read-Only Runtime Access Feasibility Gate. Evaluate one candidate only after verifying authority and non-privileged access; do not execute a container or loosen safety gates without explicit approval.
