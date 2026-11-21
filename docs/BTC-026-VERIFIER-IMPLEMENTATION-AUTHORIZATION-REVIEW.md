# BTC-026 — Local Provenance Verifier Implementation Authorization Review

**Formal decision: NO GO to implementation.** This review defines a potentially approvable **strictly local, data-only verifier** scope, but does not invent product-owner authorization or external security review that has not occurred. No actual candle files were accessed or processed.

## Reviewed evidence and authority boundary

BTC-025 PR #13 merged into `main` on 2026-11-21 at `13ae165d66dba3d0a3ec747df7a95ecc081961a4`, and its CI passed. Its twelve evidence requirements are still not verified by any real dataset. BTC-024's manifest validator checks declared metadata only. BTC-023 withheld H01 implementation and backtesting authority; BTC-026 cannot override that.

The code in `btc_engine/verifier_authorization_review.py` is a **permission ledger and proposed scope**, not a data-verifier implementation. It does not read ZIP/CSV market data, validate market candles or authenticate source records. Passing the repository tests confirms only that this permission record behaves as written.

## Scope that may be approved by a later explicit decision

- Files must be **explicitly supplied local** immutable BTCUSDT 4h datasets. The process must not fetch URLs, use API keys, account balances, or submit orders.
- Use a capped byte/record budget and limit ZIP entry names, number, compression ratios, expanded bytes and path traversal; reject malformed or nested archives.
- Explicitly declare the timestamp unit for each source: milliseconds vs microseconds; no silent inference. Require completed UTC-aligned 4h bars, no duplicates, gaps, bad OHLC or negative volumes.
- Recompute SHA-256 of **actual source bytes** and deterministic canonical candle encoding; record original source identity and retrieval provenance. Content-hash verification is distinct from independent source authentication.
- Verify **1,200** warmup candles from 2026-05-15 00:00 UTC to 2026-12-01 00:00 UTC exclusive, preserving prospective data separation. A prospective dataset must contain only candles from December 1 onwards and must not be represented as having passed the 60-day minimum before 2027-01-30 00:00 UTC.
- Report results strictly as dataset integrity, provenance evidence and explicit blockers. Never compute H01 SMA signals, positions, strategy P&L, optimized variants or recommendations.

## Decision conditions and required proof

1. Product owner explicitly authorizes implementation of the *exact limited local-file scope*; a generic “next” program request is not a trading or implementation approval.
2. An independent security reviewer accepts the input threat model and safeguards, including ZIP and decompression limits, malformed data, time units, symlinks and path traversal.
3. Predefine passing and failing synthetic fixtures. Reject mismatched actual-byte hashes, untrusted metadata, duplicate/missing timestamps, bar finality violations, overlapping periods and missing source evidence.
4. Preserve BTC-022 specification digest, BTC-018 retirement of previous SMA candidates and all H01 no-backtest/no-trade prohibitions.
5. The local verifier must remain entirely separate from the historical archive research engine and must not call a market-data network endpoint.

## Decision and follow-on

This program approves **only the reviewable scope definition**, not implementation. Missing product-owner signoff and independent security review mean a granted permission would be unsupported. All authorization switches stay false.

**Suggested BTC-027:** Local Provenance Verifier Security Threat Model and Test Fixture Contract. Deliver threat modeling and fixed negative-control tests and invite the product owner to approve the narrow implementation scope in a distinct explicit decision. Do not implement the real verifier unless those approval requirements are met.

**No H01 backtesting, paper or live trading, account access or automated execution is authorized.**
