# BTC-074 — Post-Merge Integrity Verification and Security Gate Reconciliation

**Decision (2026-11-23): NO GO for all external-data, network, credentials, strategy and trading activity.** Offline invented BTCUSDT 1h/4h fixture testing remains the only previously authorized activity. This document records evidence rather than promoting any capability.

## Verified repository facts

| Evidence | Observation | Status |
| --- | --- | --- |
| BTC-072 | PR #62 merged into `main`, merge commit `e542700f6999e5f3ed23355a586dd373ac3db71d` | VERIFIED |
| BTC-073 | PR #63 merged into `main` at 2026-11-23T14:14:33Z, merge commit `17671cb39877ea8a9ca4d52b043e1127cdbd9e99` | VERIFIED |
| Merged source | `btc_engine/r1_pinned_fixture_integrity.py` present on `main`; separately pinned literal SHA-256 digests for `1h` and `4h`, exactly 246 bytes each | VERIFIED BY SOURCE READ |
| Existing admission paths | `review_frozen_fixture`, `invented_response`, and `review_invented_response` enforce independent pinned-byte integrity before successful synthetic admission | VERIFIED BY SOURCE READ |
| Regression coverage | `tests/test_r1_pinned_fixture_integrity.py` contains tests for digest pinning, mutation/substitution rejection, both intervals, unsupported inputs, offline negative controls, and unchanged denial flags | VERIFIED BY SOURCE READ, NOT RE-EXECUTED LOCALLY |
| BTC-073 PR CI | GitHub Actions run [45187217062](https://github.com/marvingay1995-ux/binance-trading-system/actions/runs/45187217062), `Research engine tests`, completed successfully for PR head `477ac78acafa92079fb6941ed1ec80791449bbd7`; job's unittest-discovery step succeeded | VERIFIED PR-HEAD CI |
| Post-merge `main` CI | Connector's commit-workflow lookup returned no PR-triggered runs for merge commit `17671cb...`; combined-status lookup returned an empty statuses list | **UNVERIFIED**, NOT FAILED OR PASSED |

Important CI limitation: the connector's commit-workflow lookup filters to pull-request-triggered runs, and so an empty result does not prove no `push`-triggered `main` workflow exists. A reviewer must inspect the [Actions page](https://github.com/marvingay1995-ux/binance-trading-system/actions) for a `main` push run on the exact merge SHA, verify conclusion and required jobs, and attach its run ID/log reference. Do not substitute a passing PR-head run for merged-main verification.

## Integrity and trust-boundary reconciliation

- Pinned expected digests: `1h = a4b2e8cb1f225712f4803f4c1eefdeaf2a6cb1dfb94f52dbdd6f4bb9585cbb68`; `4h = 1b187fb2888816428a0aa3ac3edfb7ffb9e30d3e0b6597d95dff56f131bbbddf`. These identify **invented fixture bytes**, not authentic Binance content.
- The protected entry points reject in-process fixture registry substitution against immutable-in-normal-use static pins. This does **not** establish code-integrity protection against an attacker able to execute arbitrary Python in the process.
- `_validate_json_klines` remains an **internal untrusted structural utility**, not an approved external-data admission endpoint. Tests explicitly demonstrate that the utility can parse altered caller-provided bytes; only existing pinned gateways are allowed.
- The existing simulated HTTP envelope is an in-memory structure, **not a network client**. No real TLS, DNS, redirects, compression, retries, content provenance, response limits over the network, or exchange clock/finality properties are verified.
- Floating-point/decimal precision suitability for real market data remains unresolved. No market strategy performance claims follow from passing synthetic tests.
- The existing `security_decision()` retains `False` for independent security review, real HTTP, external JSON admission, real market-data ingestion, H01 backtesting, paper/live Spot, Binance credentials, order execution, Docker and spending. No permission change is made by BTC-074.

## Required closeout checks

1. Locate a `main` workflow run for exact merge SHA `17671cb39877ea8a9ca4d52b043e1127cdbd9e99`; record workflow ID, conclusion, required jobs, and test output. If unavailable, preserve **MAIN_CI_EVIDENCE_MISSING**.
2. Confirm merged tree remains unchanged in protected synthetic modules and tests, or document any later commits and repeat the verification against the new SHA.
3. Obtain identifiable independent security review and separate owner authorization **before any work that admits external JSON or requests genuine public Binance data**. Treat these as distinct gates: code review cannot grant owner authorization.
4. Do not interpret BTC-074's documentation PR CI as proof of BTC-073's historical `main` push CI.

## Prohibited changes under BTC-074

No external/public Binance endpoints; no credentials, authentic or downloaded market samples, background HTTP, strategy signals/H01 backtesting, paper/testnet/live trading, Docker, deployment, provider access, or spending. No runtime source, fixtures, or risk-policy modifications in this milestone.

**Disposition:** BTC-073 merge and static source presence verified; PR-head CI verified; post-merge `main` CI unverified. Security and authorization gates remain **NO GO**.
