# BTC-059 — Read-Only Runtime Access Feasibility Gate

## Dependency
BTC-058 PR #48 was **open** when BTC-059 was created. BTC-059 targets BTC-058's branch. After merging PR #48, retarget BTC-059 to main and verify CI before merging.

## Scope and safe metadata checks
This program checks whether local Podman and Docker **version metadata** can be returned without launching a container, pulling images, downloading software, creating networks, elevating privileges or accessing an exchange. CLI version queries may access existing local runtime sockets; they are not a blanket guarantee against side effects from the installed tooling. The wrapper uses `subprocess.run` without shell, a fixed argument allowlist, 3-second timeout, sanitized environment and suppresses raw version text in its output. It does not run Podman/Docker `info`, `run` or `pull`.

Podman version access and Docker local server version are weaker than rootless daemon availability, actual authorization to create a container, or enforceable network and filesystem policy. The result explicitly keeps `selected_verified_sandbox=null` and `os_network_isolation_verified=false` even if version metadata is returned.

BTC-058 CI previously observed Podman, Docker and bwrap command presence. BTC-056 namespace creation failed with `UNPRIVILEGED_NAMESPACE_DENIED`. Neither observation certifies a usable sandbox.

## Acceptance criteria for subsequent work
1. Evidence of existing operator authorization for a disposable *synthetic-only* runtime; no privileged runner changes or new spending.
2. Rootless and daemon access independently validated without external services.
3. Separately approved disposable container experiment with `--network=none`, read-only invented inputs, confined output, no-new-privileges, dropped capabilities, non-root identity and hard memory/CPU/PID/time bounds.
4. Negative controls produce actual kernel/runtime-enforced refusals, not Python mocks.
5. Explicit failure if the runtime is unavailable or any control cannot be verified.

**Decision:** read-only access metadata may identify a candidate, but **NO GO** for actual sandbox readiness, real Binance data, Binance API/credentials, H01 backtesting, paper/testnet/live orders or automated execution. BTC-028/039 remain fail-closed.
