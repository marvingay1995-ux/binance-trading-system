# BTC-028 — Local Verifier Implementation Decision

**Final decision for this review: NO GO — narrowly scoped local verifier implementation not authorized.**

## Evidence examined

- BTC-027 PR #15 merged into `main` on 2026-11-21 at `08925ddb327ac0e4211e220a1cdc2f7aa5d0e671`; the merged main-branch CI completed successfully.
- BTC-027 contains a drafted 10-threat model and 15 proposed synthetic test cases F01–F15. They are **contracts**, not actual run fixture artifacts or a verifier implementation.
- BTC-026 defined local-only capability constraints while leaving implementation sign-off and security-review approval false.
- GitHub PR #15 had no recorded reviews at BTC-028 inspection. A successful CI run and a merge do **not** establish an independent security sign-off.
- The H01-v2 specification and BTC-027 contract are hash-bound by `btc_engine/verifier_implementation_decision.py`.

## Findings and authorization matrix

| Proposed permission | Decision | Evidence still needed |
| --- | --- | --- |
| Implement strictly local CSV/ZIP byte/candle verifier | **NO GO** | Explicit named product-owner scope approval, signed independent security review and accepted test limits |
| Implement synthetic fixture suite F01–F15 | **NO GO** | Explicit implementation approval and signed acceptance criteria |
| Read real local market-data files through a new verifier | **NO GO** | Secure implementation and separate provenance validation |
| H01 SMA signal or offline strategy backtest | **NO GO** | Completely distinct H01 authorization (not under BTC-028) |
| Binance API, testnet, account access, paper/live orders | **NO GO** | Excluded from this program |

All BTC-028 permission fields are false. A merge of this PR merely records the NO-GO decision and does not approve implementation or waive external review.

## Required future authorization

A new separately reviewed and signed record must identify: the exact repository commit, BTC-027 threat-contract SHA256 and H01-v2 spec SHA256, the named reviewer, dated security acceptance and tested resource limits, and explicit product-owner permission for **only** the local data-file verifier. Source claims must remain unverified until separately corroborated. A new approval cannot be backdated or fabricated by changing a boolean.

The proposed verifier would use input files explicitly selected by the operator, strict file/ZIP bounds, explicit timestamp units, deterministic raw/canonical SHA256, UTC OHLCV integrity and partition validation. It would produce *data-integrity-only* reports and no H01 returns or orders.

## Follow-on milestone

**BTC-029 — Independent Security Review Evidence and Implementation Approval Request** should collect attributable review evidence and a narrow approval decision. If that evidence remains unavailable, do not construct a market-data verifier under this program. An additional optional doc-only handoff for security reviewers may be prepared without claiming approval.

**No real input data verified; no H01 strategy simulation; no paper/live trading; no Binance credentials or orders.**
