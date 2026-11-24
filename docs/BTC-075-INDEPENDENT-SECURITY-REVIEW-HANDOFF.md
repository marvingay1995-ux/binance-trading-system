# BTC-075 — Independent Security Review Handoff and External-Data Authorization Gate

**Classification:** Documentation-only security review preparation. **Decision:** NO GO for external data, external JSON admission, network requests, Binance credentials, H01 backtesting, paper/testnet/live orders, Docker, deployments or spending.

## Verified dependency baseline
- BTC-073 PR #63 merged into `main` as `17671cb39877ea8a9ca4d52b043e1127cdbd9e99`; immutable-in-normal-use pinned SHA-256 digests protect the frozen invented BTCUSDT 1h/4h fixtures at the documented synthetic entry points. No arbitrary in-process code execution protection is claimed.
- BTC-074 PR #64 merged into `main` on 2026-11-24 as `daac60c618318160d3d7722611a5762f2c58d1c1`. Its PR-head Actions run [45193832598](https://github.com/marvingay1995-ux/binance-trading-system/actions/runs/45193832598) succeeded, including `python -m unittest discover -s tests -v`.
- The available GitHub connector's commit-workflow lookup excludes push-triggered runs. The post-merge `main` CI result for BTC-073/BTC-074 is **NOT independently verified**, not equivalent to failed CI. Reviewer must obtain exact-SHA `main` push-run evidence before claiming integrated CI success.

## Review package and evidence to gather
| Gate | Independent reviewer evidence required | Current disposition |
| --- | --- | --- |
| Scope and provenance | Independently named reviewer, review date, source commit SHA, scope limitations and signed verdict | MISSING |
| Input trust | Audit entry points, mutable registry substitute controls, fixture pins and treatment of arbitrary caller-provided JSON; negative tests at all admission paths | SYNTHETIC SOURCE/TESTS EXIST; EXTERNAL INPUT UNREVIEWED |
| Network transport | TLS verification, DNS/SSRF protections, redirects, origin allowlist, rate limits, timeouts, retries, content-type/encoding, content length/decompression caps | NOT IMPLEMENTED/REVIEWED |
| Data semantics | Schema and bounds validation, timestamp ordering/finality, duplicate candles, strict numeric parsing/Decimal precision, exchange clock offset, malformed and adversarial samples | EXTERNAL INPUT UNREVIEWED |
| Credentials and order isolation | Proof of no secrets, privileged order calls, testnet/live connections or unapproved side effects during data assessment | NO AUTHORIZATION |
| CI and reproducibility | Verified `main` push checks for exact merged commits, test logs, artifact hashes, branch protection and required-check names | POST-MERGE EVIDENCE MISSING |
| Owner consent | New explicit, narrow authorization for each proposed next capability and an approved implementation scope | NOT GRANTED |

## Reviewer instructions
1. Review actual repository source and tests at a pinned SHA, not only prior self-reported security summaries.
2. Identify every reachable entry point for caller bytes; distinguish offline frozen-fixture admission from untrusted parser utility `_validate_json_klines`. Demonstrate exploit/negative controls against defined attacker capabilities.
3. Document severity, reproducible evidence, residual risks, owner, remediation acceptance criteria and independent sign-off for each finding.
4. Do not fetch real Binance data to validate the review. Any future external-data design is a separate owner decision and follow-up milestone.
5. Record `PASS`, `FAIL` or `EVIDENCE MISSING` per gate; unknown evidence must never silently become `PASS`.

## Decision record template
- Reviewer and independence basis: **UNASSIGNED**
- Reviewed commit SHA: **PENDING**
- Review date: **PENDING**
- `main` integration CI run URL, exact SHA and required jobs: **MISSING**
- Findings and remediation evidence: **PENDING**
- Independent review verdict: **NOT OBTAINED**
- Owner's separate authorization for any genuine market data or external JSON: **NOT GRANTED**
- External market-data readiness: **NO GO**

## Authorized BTC-075 work
Only write and review this evidence-handoff documentation on an isolated feature branch. No live credentials, API access, network requests, real market-data downloads, trading activity, production changes or spending. A documentation PR, even with green CI, **cannot** authorize a new capability or certify an independent review.
