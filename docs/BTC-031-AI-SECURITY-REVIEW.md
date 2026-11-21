# BTC-031 — AI-Assisted Security Assessment of the Proposed Local Data Verifier

**Review status: AI analysis completed; independent human certification NOT performed.**  
**Reviewed commit:** `8df979ba208e648e436140ee9a767592b9817157` on `main`.  
**Scope:** BTCUSDT 4h **local CSV/ZIP provenance-verifier proposal**, not an implemented verifier.  
**Decision:** **NEEDS CHANGES** to the proposed controls and test contract before any verifier implementation decision. No permission granted.

## Method and evidence boundary

Reviewed the current repository contracts in `btc_engine/verifier_threat_contract.py`, `btc_engine/verifier_authorization_review.py`, `btc_engine/provenance_readiness.py`, `btc_engine/simulator_architecture.py`, and `btc_engine/security_review_request.py`. Checked their expressed trust boundaries, proposed limits, F01–F15 fixture outcomes, and fail-closed authorization fields.

This is a **model-produced design review**, not a penetration test, independent human security sign-off, implementation test, verified data-source inspection, or proof that any runtime is safe. The 15 scenarios are descriptions, not executed attack samples. The issues below are design/assurance gaps, not confirmed exploitable vulnerabilities in running verifier code.

## Prioritized findings

### AI-SEC-01 — HIGH: Resource ceilings are declarative, not enforceable protections

**Evidence:** `btc_engine/verifier_threat_contract.py:15-27, 38-40, 78-80`. The proposed 25 MB raw / 50 MB expanded / 100:1 compression / 100,000 row / 30-second limits are merely stored as values; `contract_report()` checks positivity, not enforcement or their adequacy. The contract has no overall per-process memory budget, bounded parser-field growth, or clear behavior when a deadline is reached during a blocking read.

**Risk:** Future code may claim limits are met while decompression, malformed CSV rows or resource exhaustion bypasses simple metadata checks.

**Required change:** Add precise *enforcement points* and budget semantics: refuse before and during reads, cap cumulative and per-member expansion, cap rows/fields/line lengths, use bounded chunks, fail closed on CPU/time/memory exhaustion, avoid trusting ZIP header size fields, and document safe cancellation. Test limit-minus-one, exact-limit and limit-plus-one for each ceiling. Benchmark under a constrained CI environment before accepting numerical limits.

### AI-SEC-02 — HIGH: File safety / TOCTOU and ZIP identity contracts are incomplete

**Evidence:** `btc_engine/verifier_threat_contract.py:38-41, 57-60`. T01 and T04 require rejecting symlinks and processing the same opened bytes but do not specify accepted input-root canonicalization, secure open flags, hardlink policy, ZIP filename encoding and Unicode normalization, entry-type permission bits, or safe output location/overwrite policy.

**Risk:** A future implementation could open an unintended file, parse a different file than it hashed, or write evidence to an attacker-controlled destination.

**Required change:** Specify a single allowed input directory, reject symlink/nonregular inputs (including substituted file descriptors), open once with platform-appropriate no-follow and regular-file checks, hash and parse that same immutable stream/snapshot, disallow ZIP extraction and all ZIP members except a single flat regular CSV, and create output atomically in a dedicated protected directory with no overwrite. Tests: symlink inside/outside root, symlink swap before open, Unicode/encoded separators, absolute Windows/POSIX names, ZIP directory/symlink metadata, CRC and duplicate-entry behaviors.

### AI-SEC-03 — HIGH: Source provenance could be confused with local integrity

**Evidence:** `btc_engine/simulator_architecture.py:98-113, 129-135` validates `source_uri` using `https://` and only syntactic SHA-256 checks; `btc_engine/provenance_readiness.py:18-23, 69-72` acknowledges separate source verification. `btc_engine/verifier_threat_contract.py:44-45, 62` says to refuse fabricated source claims but does not define a corroboration chain or authentic trust anchor.

**Risk:** Correctly hashed malicious or synthetic data could be labeled as authentic exchange data.

**Required change:** Define mutually exclusive report fields `content_integrity_verified` and `publisher_provenance_verified`. Both default false; the latter requires a separately trusted publisher artifact/checksum or independently corroborated retrieval audit tied to raw bytes. A URL and self-declared hash are insufficient. Add a fixture containing perfectly valid OHLC and matching local hashes with a forged Binance URL; expected result `CONTENT_VALID_SOURCE_UNVERIFIED`, not generic `PASS`.

### AI-SEC-04 — MEDIUM: Canonical candle serialization and timestamp rules lack exact normative schema

**Evidence:** `btc_engine/provenance_readiness.py:22-33`, `btc_engine/verifier_threat_contract.py:41-44, 54-56`. The proposals require explicit millisecond/microsecond units and canonical SHA-256 but do not define accepted CSV columns, numeric normalization, decimal zero handling, canonical encoding, hashing of sorted or unsorted rows, and schema versions.

**Risk:** Different implementations may compute different SHA-256 values, silently coerce timestamps, or disagree about malformed rows.

**Required change:** Freeze one versioned record schema (open time, open/high/low/close, volume, optional fields policy), ASCII/UTF-8 and BOM policy, decimal finite-value normalization, newline handling, canonical JSON/CSV encoding, exact timestamp conversion with divisibility checks, and whether input order is preserved (reject reordering rather than sorting away anomalies). Add golden digests for independently generated fixtures; specifically test microsecond values not divisible by 1,000 and out-of-order otherwise-valid records.

### AI-SEC-05 — MEDIUM: Finality and future-dataset fixture expectations are date-dependent

**Evidence:** `btc_engine/verifier_threat_contract.py:51-52, 60-61`, `btc_engine/simulator_architecture.py:118-127`. F02 declares 360 fully closed synthetic prospective 4h bars; any real 60-day interval starting December 1, 2026 cannot finish before January 30, 2027. Existing shape validation also depends on a declared `retrieved_utc` rather than a trusted clock.

**Risk:** A fixture could pass as authentic, future-complete data by using a fabricated collection time.

**Required change:** Keep synthetic fixture time explicitly injected/test-only, prohibit synthetic acceptance as real-market evidence, use a trusted evaluation clock for real-data finality, and separate `CANDLE_INTEGRITY_VALID` from `MINIMUM_PROSPECTIVE_WINDOW_COMPLETE`. Include boundary tests immediately before/equal/after the 4h close and the full 60-day end.

### AI-SEC-06 — MEDIUM: Threat/fixture coverage is good but gaps remain

**Evidence:** `btc_engine/verifier_threat_contract.py:38-64`. The 15 named fixtures cover many core cases, but several distinct failure modes are grouped into single tests, and their expected statuses are not consistently precise (e.g. `REJECT` versus `SOURCE_UNVERIFIED`).

**Risk:** An incomplete set of negative controls could be reported as a comprehensive security pass.

**Required change:** Split F08–F12 into independently testable single-fault cases; add cases for ZIP data descriptors, extra fields, unsupported compression, oversize CSV quoted fields/multiline records, BOM and encoding, formulas/CSV injection in generated reports, ZIP CRC mismatch, output collisions, zero-width timestamps and malformed numeric exponent bombs. Ensure each scenario has deterministic expected error codes and evidence requirements.

### AI-SEC-07 — MEDIUM: No-network and no-trading isolation is policy only

**Evidence:** `btc_engine/verifier_authorization_review.py:15-40`, `btc_engine/verifier_threat_contract.py:46, 62-71`. The restrictions are prose and flags, not a sandbox, automated import denylist or runtime network blockade.

**Risk:** A future verifier could accidentally import or call existing market-fetch/backtest code.

**Required change:** When implementation is separately authorized, run the verifier in a minimal process with no network credentials, verify imports and subprocess usage, deny network at the runtime layer where available, and add an offline test that fails if any socket/exchange/strategy call occurs. Do not pretend a no-network Boolean guarantees isolation.

### AI-SEC-08 — MEDIUM: Ownership and review attestation remain unverified

**Evidence:** `btc_engine/security_review_request.py:18-30, 91-111` validates reviewer-record field shape without authenticating identity/signature, correctly returning `VALID_BUT_UNAUTHENTICATED`. `btc_engine/verifier_threat_contract.py:66-74` denies every permission.

**Risk:** A plausible document could be confused with independently authenticated sign-off.

**Required change:** Keep a separate evidence ledger recording reviewer identity, external verification method, reviewed exact commit and contract digests, observations, acceptance/rejection, and accountable owner decision. AI findings must be labeled AI-assisted, never independent human assurance. No automatic authorization from a complete form or merged PR.

## T01–T10 coverage assessment

| Threat | Assessment | Follow-up |
| --- | --- | --- |
| T01 ZIP traversal/symlink entries | Partial specification | Clarify ZIP filename normalization, metadata types, and no-extract rule |
| T02 ZIP bombs/resource exhaustion | Partial specification | Instrument runtime budgets and boundary fixture series |
| T03 Corrupt/encrypted/nested ZIP/CSV | Partial specification | Separate CRC, encryption, data descriptor, compression-method fixtures |
| T04 Symlink/path/TOCTOU | Partial specification | Secure root, single opened file snapshot, safe output writes |
| T05 Timestamp units/gaps | Partial specification | Freeze unit conversion and canonical record schema |
| T06 Invalid OHLCV | Partial specification | Exact Decimal grammar, exponent and boundary tests |
| T07 Finality/partition | Partial specification | Trusted clock and explicit synthetic-only override |
| T08 Tampered data/source spoofing | Partial specification | Content/provider integrity status separation |
| T09 Resource/output/report misuse | Partial specification | Deterministic errors, atomic no-overwrite report path |
| T10 Unwanted exchange/trading behavior | Policy specified only | Future runtime sandbox and negative imports/network test |

## F01–F15 coverage assessment

F01 and F02 are positive **synthetic** scenario definitions, not observed verification results. F03–F12 and F14 are proposed rejection cases; F13 must preserve unverified source status even when local content matches its own hash; F15 specifies reproducibility. None has been run against a verifier.

**Priority:** before any later verifier implementation, split the compound negative cases into independently checkable fixtures, freeze exact error codes, provide golden synthetic raw/canonical hashes, and document safe no-network execution.

## Decision / evidence

- **AI technical review:** completed as a document inspection of the stated baseline.
- **Independent human security certification:** **NOT obtained**.
- **ZIP/CSV verifier implementation:** **NOT authorized or performed**.
- **Synthetic adversarial fixture execution:** **NOT performed**.
- **Source authenticity and real-market candle-file integrity:** **NOT established**.
- **H01 strategy simulation, paper/live orders and credentials:** **NOT authorized**.

**Recommended next action:** Treat this draft as a security review artifact; resolve findings in a separately versioned revised contract and determine whether a **narrow, synthetic-fixture-only** preparatory implementation may be explicitly authorized. No bypass of BTC-028 or BTC-029 NO-GO gates.
