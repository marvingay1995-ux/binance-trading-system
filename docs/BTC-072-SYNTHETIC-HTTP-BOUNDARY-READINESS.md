# BTC-072 — Synthetic HTTP Boundary Review and R1 External-Data Readiness Decision

**Decision: NO GO for authentic public BTCUSDT data, external JSON admission, any network fetch, backtesting, paper/live orders. GO only for already-approved *invented fixture* testing.**

## Repository evidence checked

- BTC-071 PR #61 **merged** to `main` at `cfb8cdf6f45f73c4bf3e6a2f9d7488d15dffecba`.
- Merged-main Actions run `45184893342` **passed 493 tests**.
- Reviewed `btc_engine/r1_offline_http_response.py` and its BTC-071 documentation against BTC-069/070 security and authorization boundaries, not merely against prior summaries.
- Owner's existing approval applies **only** to offline invented BTCUSDT 1h/4h JSON fixtures. No fresh owner authorization for authentic data has been recorded.

## Actual control boundary

`invented_response` constructs a Python dictionary with status, headers and bytes, but makes **no HTTP request**. `review_invented_response` validates status 200, two exact headers, a maximum 8,192-byte body, SHA-256 equality to a registered invented fixture, kline checks and finality relative to one **fixed synthetic UTC clock**. It explicitly refuses a modified payload. No transport, account access, or genuine data handling is present.

This is useful internal validation, but cannot be promoted into an external-data security assessment.

## Findings grounded in the implementation

| Finding | Evidence | Required remediation |
| --- | --- | --- |
| F072-01 — mutable fixture registry | `SYNTHETIC_FIXTURES` is a module-level Python dict; BTC-071's digest check derives expected bytes from this mutable registry at runtime | For any future externally exposed boundary, pin a separately reviewed immutable fixture ID/digest; distinguish trusted-code mutation from remote adversaries |
| F072-02 — no network security implementation | No TLS, hostname pinning, DNS/redirection, response size/decompression, rate or timeout transport controls | Separate bounded client threat model, code, offline negative tests and independent sign-off before any connection |
| F072-03 — internal parser not safe for untrusted data | `_validate_json_klines` accepts arbitrary bytes if directly called; only the BTC-071 wrapper enforces frozen fixture membership | Do not expose that internal parser as a generic authenticated market-data gateway; develop separate reviewed admission controls |
| F072-04 — precision and clock limits | Invented values validated via Python `float`; finality uses fixed `SYNTHETIC_AS_OF_MS` only | Define Decimal-safe exchange precision, timestamp/time trust, duplicates, depth/resource limits and completed-candle semantics |
| F072-05 — no separate approval or independent review | BTC-068/BTC-069 owner consent authorizes invented fixtures; BTC-071 record states independent reviewer unverified | Obtain attributable independent review of exact future implementation plus distinct owner permission for real public data |

BTC-072 adds regression evidence for the mutable fixture registry, exact synthetic boundary and non-authorization, but **does not repair every finding or perform an external security audit**. In-process registry mutation requires a caller able to execute code in the Python process; it is not presented as a remotely exploitable issue.

## Critical-path decision

The next useful engineering task is **bounded remediation for in-process fixture integrity plus an offline hostile-JSON response parser proposal**, staying within the existing invented-fixture approval unless the owner explicitly broadens it. Any processing of external JSON, generic HTTP response bytes, authentic Binance market data, network call or trading is a separate authorization and review decision, not a natural consequence of merging BTC-072.

This milestone must not be interpreted as a signed independent review. BTC-018 retirement of SMA 5/20, BTC-028/039 historical NO GO, BTC-064 stage restrictions and the owner's original R1 approval remain unchanged.

No network, real market files, credentials, backtests, Docker, paper/testnet/live orders or spending.
