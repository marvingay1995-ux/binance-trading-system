# BTC-029 — Independent Security Review Evidence and Implementation Approval Request

**Decision: REVIEW REQUEST READY, NOT SUBMITTED; NO VERIFIER IMPLEMENTATION AUTHORIZED.**

## Verified repository state

BTC-028 (PR #16) merged on 2026-11-21 at commit `e6242e1819577bc11ac1232cad2907cd090b1c6b`; main-branch CI succeeded. BTC-028 recorded a formal **NO GO** on local-file verifier implementation, because no explicit product-owner approval, independent security signoff, or validated negative-control/limit acceptance was evidenced. BTC-029 does **not** infer approval from PR #16's merge or successful unit tests.

## Reviewer handoff

Review exactly the **BTC-027** threat contract SHA256 and **H01-v2** specification SHA256 emitted by `btc_engine.security_review_request`. Examine the proposed narrowly scoped, offline **BTCUSDT 4h local CSV/ZIP provenance verifier**, including:

1. Ten threat categories T01–T10: ZIP traversal and bombs, symlink/TOCTOU file handling, malformed CSV, timestamp precision, invalid OHLCV, source impersonation, bounded compute and forbidden network/trading capabilities.
2. Fifteen proposed synthetic negative/positive fixture cases F01–F15, their expected reject/pass outputs, reporting provenance and repeatability. The fixture cases currently exist only as **registry descriptions**, not generated runnable adversarial datasets.
3. Proposed numerical ceilings: maximum 25 MB raw input, 50 MB expanded data, a single ZIP entry, 100:1 compression ratio, 100,000 candle records and 30 seconds. Review these as *unvalidated drafts* requiring safe stress tests.
4. Separation of (a) well-formed metadata, (b) locally hashed bytes and verified candle content, and (c) independently authenticated publisher provenance. A declared `source_uri`, checksum or reviewer form is never alone source authentication.
5. Explicit prohibition on Binance API/credentials, account access, trading indicators or optimizers, strategy backtests, paper/testnet/live execution and orders.

## Evidence required for any future GO decision

The independent reviewer must identify themselves and their role, cite the exact GitHub commit plus both SHA256 bindings, provide a dated review with signed or otherwise independently attributable evidence, list accepted/rejected threat controls and resource limits, describe residual risks, and record one of: `APPROVE_SCOPE_FOR_SEPARATE_OWNER_DECISION`, `REJECT`, or `NEEDS_CHANGES`.

**A security review outcome is not product-owner approval.** The owner must separately approve a particular local-verifier implementation scope after examining that evidenced review. Neither act automatically authorizes processing real data or executing H01 or exchange orders. A signed form without independently verified provenance must be treated as unverified.

## Proposed approval request (not sent)

> Review BTC-027 threat model and F01–F15 synthetic fixture contract for a proposed local-only BTCUSDT 4h CSV/ZIP data verifier. Assess path safety, malformed archives, hard resource limits, timestamp units, candle integrity and independent source-provenance labeling. Please identify the exact source commit and frozen contract SHA256 in a signed decision, describe residual risks and accept, reject or request changes. This request does not include any exchange API, H01 backtesting or trading authority.

BTC-029 intentionally does not name, contact, claim acceptance by or impersonate an external reviewer. No review request or email has been dispatched.

## Current disposition and follow-on

The new `btc_engine/security_review_request.py` only constructs a deterministic request and validates the **shape** of future proposed reviewer records, always returning `VALID_BUT_UNAUTHENTICATED`. No signature cryptography, actual human signoff, data-source authentication or implementation authority has been obtained. A complete-looking form cannot toggle permissions.

**Next meaningful action:** arrange attributable independent security review, obtain a scoped owner decision, and only then consider a new implementation authorization PR; the current **NO GO** remains binding. Do not create a succession of “approved” review stages without evidence.

**No local-file verifier, market-data inspection, H01 signal code, backtesting, Binance account access or paper/live trading was created or authorized.**
