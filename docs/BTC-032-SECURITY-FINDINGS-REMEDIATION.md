# BTC-032 — AI Security Findings Remediation Contract

**Status:** Security design contract amended for review. **Not** an implemented verifier, completed security test, independent certification or implementation authorization.

## Evidence and scope
BTC-031 PR #20 was merged into `main`; the review reports eight findings AI-SEC-01–AI-SEC-08, three high and five medium, against the proposed local-only BTCUSDT 4h CSV/ZIP data verifier. This revision retains `btc_engine/verifier_threat_contract.py` (BTC-027) unchanged, and records a separate BTC-032-v1 proposal in `btc_engine/verifier_security_v2.py`. It binds the inherited BTC-027 contract SHA and frozen H01-v2 SHA.

No model-driven claim of independent human security assurance is made. The review remains an internal AI-assisted assessment. Existing BTC-028/029 NO-GO decisions stay in force.

## Remediation decisions

| BTC-031 finding | Change in BTC-032 | Status |
|---|---|---|
| AI-SEC-01 resource limits | Counter semantics for raw/expanded bytes, rows, fields, ratio and processing time; below/equal/above boundary fixtures | Specification only |
| AI-SEC-02 paths/ZIP/TOCTOU | Safe input-root, regular-file/symlink refusal, one-open snapshot, one flat ZIP member, protected atomic output | Specification only |
| AI-SEC-03 publisher authenticity | Distinct content-integrity and publisher-provenance evidence, both initially false; forged URL negative case | Specification only |
| AI-SEC-04 canonical data | Proposed versioned 4h candle schema, explicit time units, numeric normalization, UTC ordering, JSON Lines contract | Needs schema agreement and golden digests |
| AI-SEC-05 candle finality | Injected synthetic clock explicitly labeled test-only, real-data trusted clock and separate 60-day completion status | Specification only |
| AI-SEC-06 fixtures | Expand F08–F12 into granular fault scenarios, introduce stable error-code catalogue and boundary tests | Registry only; no hostile file executed |
| AI-SEC-07 isolation | Require an OS/runtime no-network boundary and negative capability tests, not just policy flags | Not implemented |
| AI-SEC-08 signoff | Separate human review evidence and owner authority; AI review and PR merges never count as certification | Missing |

### Critical clarification on semantics

The proposed CSV parser is deliberately *not built*. The BTC-032 module records target behavior, not enforcement, and the new tests validate only the declaration schema. A test passing here does not mean ZIP safety, data integrity, authentication, memory caps or an enforceable deadline have been proven.

Some proposed error codes and fixture definitions remain design choices requiring review. In particular, the row-count boundary case needs its own distinct future error code rather than reusing `RAW_SIZE_EXCEEDED`; and the compound ZIP-entry test should be split into targeted single-fault scenarios during subsequent fixture implementation. Treat these as **open review issues**, not silently fixed implementation details.

## Proposed verifiable acceptance criteria

For a separately authorized implementation, demonstrate bounded read/decompression under a constrained process, all counter boundaries including exact-limit allowance, secure path refusal without TOCTOU substitution, identical bytes for SHA and parsing, deterministic schema and golden-digest fixtures, explicit source-provenance gating, and runtime isolation from Binance/strategy code.

Compare recorded pass/fail evidence to the actual input hashes, environment, versions and runtime traces. The present BTC-032 registry has none of that executed evidence.

## Follow-on

**BTC-033** should review this revised contract for internal inconsistencies, finalize error codes and golden synthetic fixture definitions, then request a *narrow, explicit* authorization if executable **synthetic-only** tests are desired. Such approval is separate from real market-data verification or H01 backtesting.

All BTC-032 evidence and authorization fields remain false: no local data verifier, no actual candle processing, no Binance credentials, no trades.
