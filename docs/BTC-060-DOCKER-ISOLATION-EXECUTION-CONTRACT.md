# BTC-060 — Docker Isolation Execution Authorization and Synthetic Test Contract

**Decision: Docker execution NOT AUTHORIZED.** This is a static, reviewable scope and acceptance contract, not permission to launch containers or process real data.

## Verified baseline (November 23, 2026)

- BTC-059 PR #49 merged into `main`: `d2655d8f822840e662c97544151c9dbd3a7bdbb3`.
- Merged-main CI [run 45170296024](https://github.com/marvingay1995-ux/binance-trading-system/actions/runs/45170296024) passed **366 tests**.
- Actual CI `BTC059_CI_RUNTIME_ACCESS`: Docker `LOCAL_ENGINE_RESPONDED`, reason `VERSION_METADATA_ONLY`; Podman `UNAVAILABLE`, reason `VERSION_QUERY_REJECTED`.
- Docker metadata response **does not establish** rootless mode, runtime authority, an existing trusted image, network-none enforcement or secure filesystem confinement.

## Proposed future experiment (NOT approved or implemented)

One explicitly authorized disposable Docker container may eventually evaluate only the frozen invented BTC-036 `golden.csv`/`golden.zip` bytes. The intended controls are:

| Boundary | Required proposed property |
|---|---|
| Network | `--network=none`, test IPv4 and IPv6 policy without external connections |
| Filesystem | `--read-only`; exact allowlisted invented inputs mounted read-only; dedicated output mount; no host secrets |
| Identity | `--user=65534:65534`, `--cap-drop=ALL`, `--security-opt=no-new-privileges:true` |
| Process and resources | `--pids-limit=32`, `--memory=256m`, `--cpus=1`, strict parent deadline and descendant cleanup |
| Image provenance | Existing locally available trusted image with recorded digest; **no pulls** |
| Runtime context | Explicit owner approval and validated rootless/daemon scope; **no privilege escalation** |

The flags are **future design constraints**, not a runnable command or proof that a host enforces them. Required negative controls must observe kernel/runtime denials, not simply Python mocks; enforcement of mount restrictions, no-network configuration, privilege constraints, cleanup and policy must all be verified.

## Decision / authority separation

1. BTC-060 authorizes **only code, documentation and static regression tests** describing a possible future synthetic test. It explicitly withholds all execution permission.
2. A future owner decision must specify the exact experiment, image identity, trusted runtime, mounting plan, costs (none by default), and scope. Such approval would still cover **only synthetic fixtures**.
3. Any unsupported control yields **FAIL CLOSED**, not a simulated security success.
4. Do not modify BTC-028/039 historical gates or claim independent human security certification.

**Non-authorizations:** no Docker/container `run`/`create`/`start`/`pull`, no privileged runner or network changes, no external files or real Binance data, no Binance credentials/API, no H01 signals/backtesting, paper/testnet/live orders, automated execution, deployment or spending.

## Next gated step

BTC-061 may verify *static* Docker contract completeness and collect independent policy evidence for a future separately authorized synthetic execution experiment. The evidence must distinguish runtime accessibility from effective isolation.
