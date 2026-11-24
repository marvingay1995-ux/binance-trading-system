# BTC-076 — Independent Security Review Execution and Findings Register

**Baseline:** `main` after BTC-075 merge `16ca2f3c83412eafa5a20a17ab23a2e93824b36a` (2026-11-24).  
**Review status:** PRELIMINARY SOURCE TRIAGE ONLY — **NOT** an independent security review.  
**Independent reviewer:** UNASSIGNED. **Independent sign-off:** NOT OBTAINED.  
**Authorization verdict:** **NO GO** for external JSON/market data, Binance network requests, credentials, backtesting, trading, Docker, deployment and spending.

## Method and limitations

Read directly from `main`: `btc_engine/r1_offline_synthetic_json.py`, `btc_engine/r1_offline_http_response.py`, `btc_engine/r1_pinned_fixture_integrity.py`, and `docs/BTC-075-INDEPENDENT-SECURITY-REVIEW-HANDOFF.md`. Read PR #65 and its successful **PR-head** workflow [45417123963](https://github.com/marvingay1995-ux/binance-trading-system/actions/runs/45417123963). No independent reviewer was engaged, no dynamic tests or external input were executed for BTC-076. This is a review preparation and preliminary findings register; it does not assert absence of vulnerabilities.

## Preliminary findings register (not independently validated)

| ID | Severity / class | Source evidence | Finding and risk | Disposition / closure requirement |
| --- | --- | --- | --- | --- |
| F076-01 | BLOCKING — trust boundary | `r1_offline_synthetic_json.py::_validate_json_klines(raw, interval)` calls `json.loads(raw)`; approved `review_frozen_fixture` checks pinned body before calling it | Internal validator can structurally accept arbitrary caller bytes; it is explicitly not an external-data gateway. Risk arises **if a future caller bypasses pinned admission**. No remote exploit is claimed. | Keep utility internal; independent reviewer maps all call sites and tests bypass/negative cases at pinned SHA; any external admission requires separately authorized and reviewed gateway |
| F076-02 | BLOCKING — transport readiness | `r1_offline_http_response.py::invented_response` builds a Python dictionary; `review_invented_response` validates its fixed synthetic envelope. `security_decision()` states real HTTP client and TLS/DNS/redirect verification are false | No real TLS, DNS, redirects, SSRF prevention, bounded decompression, retry/rate-limiting, or network provenance can be inferred from simulated envelopes | Independent reviewer documents transport threat model and mandatory controls; separate owner authorization required **before implementation or real fetch** |
| F076-03 | BLOCKING — financial data semantics | `r1_offline_synthetic_json.py::_finite_nonnegative_number` parses numeric strings via `float`; `r1_offline_http_response.py` uses fixed `SYNTHETIC_AS_OF_MS` | Floating-point and fixed synthetic clock are not validated for authentic prices, quantities, exchange timestamps, or finalized candles | Independent reviewer evaluates exact decimal semantics, time/finality and adversarial values; no authentic data until approved design |
| F076-04 | BLOCKING — process-integrity limit | `r1_pinned_fixture_integrity.py::EXPECTED_SHA256` is a `MappingProxyType`; gateway functions call `assert_registered_invented_bytes` | Static pins guard normal registry mutation but do not defend against arbitrary code execution or monkeypatching in the same Python process. No claim of attacker reachability | Reviewer defines attacker capabilities; records residual risk and necessary isolation if future trust model changes |
| F076-05 | EVIDENCE MISSING — reproducibility | PR-head run 45417123963 succeeds; the GitHub connector's commit-run lookup is limited to PR-triggered workflows | No independently verified `main` push CI record for exact BTC-075 merge commit is attached. Missing evidence is **not** failed CI | Attach exact SHA, `main` event run, jobs, conclusions and logs, or explicitly retain missing-evidence state |
| F076-06 | BLOCKING — governance | `security_decision()` and `authorization_record()` contain false external-data, credentials, execution and independent-review flags | Neither a named independent reviewer nor distinct owner consent exists for authentic data admission, network or orders | Obtain identifiable independent reviewer verdict and separate explicit owner authorization for each proposed capability; no self-certification |

## Existing verified positive controls

- Separate literal SHA-256 pins for invented 246-byte BTCUSDT 1h and 4h bodies; checks at frozen fixture and simulated response entry points.
- Fixed simulated status/header/body envelope, strict fixed clock, byte caps, and tests on restricted synthetic inputs.
- `require_live_fetch_or_order` and `require_network_or_order` are unconditional denials in examined modules.
- GitHub reports BTC-075 PR #65 merged and its PR-head Research engine tests run 45417123963 successful. This is **not** post-merge `main` CI verification or a full code audit.

## Independent-review execution record

| Field | Required evidence | State |
| --- | --- | --- |
| Reviewer identity and independence | Name/affiliation, conflict-of-interest declaration, scope and review date | NOT ASSIGNED |
| Exact pinned source | Commit, source inventory and dependency versions | BASELINE RECORDED; INDEPENDENT FREEZE PENDING |
| Test execution and exploit-negative cases | Commands, logs, reproducible results, attack assumptions | NOT EXECUTED IN BTC-076 |
| Findings adjudication | Confirm/disprove IDs, severity, reachability, corrective owner, tests | PENDING INDEPENDENT REVIEW |
| `main` CI | Exact merge SHA and successful push workflow evidence | UNVERIFIED |
| Independent sign-off | Signed decision, accepted residual risks | NOT OBTAINED |
| Owner authorization | Explicit separate scope for any non-synthetic activity | NOT GRANTED |

## Instructions for independent reviewer

1. Freeze `main` at a SHA, inventory entry points, review source and test evidence rather than relying on milestone documents.
2. Verify or reject each preliminary finding with file/line references, reachable scenarios and reproducible offline negative controls. No authentic market data or network calls.
3. Distinguish a missing implementation from an exploitable bug in the current intentionally offline design.
4. Add evidence links and clear pass/fail/evidence-missing statuses, remediation owners and residual-risk decisions. Confirm reviewer's independence explicitly.
5. Keep the external-data decision at **NO GO** until independent review is finished **and** the owner separately authorizes a specifically scoped next step.

## BTC-076 completion criteria

The **findings register and source triage** can be merged as documentation after normal PR checks, but BTC-076 **independent-review execution cannot be marked complete** without real reviewer engagement, adjudicated findings, CI evidence and attributable sign-off. No code, fixture, runtime, network or trading permission is altered by this register.
