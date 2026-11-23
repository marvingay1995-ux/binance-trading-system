# BTC-061 — Docker Isolation Contract Verification and Execution Readiness Decision

**Decision: STATIC CONTRACT ACCEPTED FOR SYNTHETIC-ONLY RESEARCH; DOCKER EXECUTION NO GO.** This is a review of the exact BTC-060 contract, not authorization to run it.

## Verified source and CI lineage

- At review, `main` was `d2655d8f822840e662c97544151c9dbd3a7bdbb3` (BTC-059), and BTC-060 **PR #50 was open** targeting `main`.
- BTC-060 branch CI run `45171490604` passed **374** repository tests, while the earlier BTC-059 merged-main run `45170296024` passed **366**. Do not describe 374 as a verified main-branch count.
- BTC-059 CI reported Docker local server `Version` metadata (not verified container-launch authority), and a rejected Podman version query.
- The BTC-060 code explicitly sets `docker_execution_authorized=false`, `docker_run_allowed=false`, and raises a refusal on all execution gate calls.

## Static contract verification

BTC-061 adds `btc_engine/synthetic_docker_readiness_decision.py` and deterministic unit tests to verify the BTC-060 policy still contains all proposed safeguards: `--network=none`, `--read-only`, `--cap-drop=ALL`, `--security-opt=no-new-privileges:true`, bounded `--pids-limit=32`, `--memory=256m`, `--cpus=1`, and `--user=65534:65534`. These are **not run arguments** in BTC-061; they remain inert strings, not evidence of enforcement.

The tests fail closed for incomplete flags, `--privileged`, changed execution flags, or unverified approval claims. They also verify the report's negative authorizations and serialization. No Docker process, image inspection, container launch or network request is performed.

## Readiness evidence gaps (all open)

| Required gate | Status at review |
| --- | --- |
| BTC-060 merged into main and new main CI verified | Not yet |
| Explicit owner approval for a specific single synthetic experiment | Not recorded |
| Existing trusted local image identity and immutable digest | Unverified |
| Local daemon authorization and nonprivileged runtime context | Unverified |
| Actual IPv4 and IPv6 runtime network denial | Unverified |
| Frozen invented inputs read-only and separately confined output | Unverified |
| Non-root identity, zero capabilities, no-new-privileges | Unverified |
| CPU/memory/PID/deadline and descendant cleanup | Unverified |
| Negative-control enforcement logs | Unavailable |
| Runtime policy, exact CI commit and cleanup evidence | Incomplete |

**Static policy presence is not actual OS isolation.** Version queries, mocks and successful CI do not close these gates. BTC-061 does not accept arbitrary input or real Binance data.

## Required merge sequence and following step

1. Merge [BTC-060 PR #50](https://github.com/marvingay1995-ux/binance-trading-system/pull/50) into `main` and verify its new main Actions run.
2. Retarget BTC-061's dependent PR to `main`, rerun CI and merge after review.
3. Future work may inventory trusted local Docker images or inspect runtime policy **only under a separately defined, non-mutating scope**. Any actual synthetic container execution requires additional explicit authorization and evidence; do not auto-activate it.

**Hard NO GO:** Docker run/create/start/pull, privileged changes, real Binance CSV/ZIP or API/credentials, H01 signals/backtests/optimization, paper/testnet/live orders, automated execution, deployment or spending. BTC-028/039 historical boundaries remain untouched.
