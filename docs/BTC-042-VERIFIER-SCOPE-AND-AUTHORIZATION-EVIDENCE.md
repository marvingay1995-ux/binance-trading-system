# BTC-042 — Offline Verifier Scope Finalization and Authorization Evidence

**Status: implementation scope proposed for owner review; NO GO for implementation under existing BTC-028/039 authority.**  
**Baseline main:** `eaa47c020b85ddd136aa97686047e69f9102e727` (BTC-037, BTC-038 and BTC-039 merged).  
**Review type:** internal AI-assisted scope/evidence reconciliation, not independent security certification.

## Verified repository context

- BTC-037 PR #26 merged to main; BTC-038 PR #27 had merged into the BTC-037 branch, so both programs are present on main.
- BTC-039 PR #28 merged to main; GitHub Actions passed **232 repository tests** at the merged main revision.
- BTC-036 through BTC-038 exercise **synthetic-only** fixture generation, byte/ZIP metadata checks and small bounded isolation probes. There is **no validated general local market-data verifier** and no proven full production resource boundary.
- `btc_engine/verifier_implementation_decision.py` (BTC-028) and `btc_engine/offline_verifier_readiness.py` (BTC-039) still fail closed and deny local verifier implementation and real data ingestion. Historical status fields describing earlier PR states are immutable **time-of-review snapshots**, not current merge state.

## Exact proposed implementation scope — NOT AUTHORIZED HERE

Suggested future isolated branch: `feature/btc-043-synthetic-only-offline-verifier` (name is illustrative, not created here).

Proposed source and test files, only after an explicit scope decision:

1. `btc_engine/offline_fixture_verifier.py` — network-free, read-only **synthetic-fixture-only** CSV/ZIP validator that accepts an explicit local input root, no archive extraction, one flat CSV ZIP member, and deterministic errors.
2. `tests/test_offline_fixture_verifier.py` — positive and negative tests using BTC-034–038 invented data; no real exchange archives.
3. `docs/BTC-043-OFFLINE-FIXTURE-VERIFIER-EVIDENCE.md` — precise input hashes, environment, measured bounds, observed verdicts, remaining caveats and unsupported claims.

Any future general verifier handling real Binance archives requires **different, separately authorized scope and review**. No “read-only” label is a substitute for safe path-opening, ZIP resource budgets, malformed CSV defenses or hard network isolation.

### Proposed input and output contract

- Only a configured local directory of invented files labeled `SYNTHETIC_NOT_BINANCE_DATA`. No download, URI fetching, exchange library, credentials, strategy module, subprocess launching or network operation.
- Use a known synthetic schema from BTC-034: `open_time_ms,open,high,low,close,volume`, UTF-8 without BOM, LF delimiters, explicit UTC 4h timestamps, finite nonnegative volume and consistent OHLC.
- Reject path traversal, symlink/nonregular file, multiple ZIP entries, encrypted/nested/unsafe member names, unsupported compression, malformed CSV, timestamp gaps/duplicates and bad CRC.
- Stream under bounded counters; refuse at a specified maximum without trusting ZIP headers. BTC-027 proposed ceilings are 25,000,000 raw bytes, 50,000,000 expanded bytes, 100,000 records, 4,096 bytes per row, compression ratio 100:1 and 30 seconds; **these are not yet demonstrated or accepted as safe**.
- Compute raw and canonical SHA-256 on the same controlled input bytes; never mark publisher authenticity true because a self-declared hash or URL matches.
- Produce deterministic JSON evidence in a dedicated output directory with collision refusal and no overwrite; keep output handling distinct from source identity claims.
- Execute in constrained local/CI runtime; a Python socket monkeypatch alone is *not* an OS network sandbox.

## BTC-042 evidence register and decisions

| Evidence item | Verified finding | Authorization consequence |
| --- | --- | --- |
| Repository integration | BTC-037–039 merged; 232 tests passed on main | Repository baseline reconciled |
| Synthetic positive/negative samples | Invented bytes and bounded helper probes exist | Useful fixture-test inputs; no actual verifier security verdict |
| Raw / expanded / row / time ceilings | Proposals only; no full stress evidence | Must be independently measured before general-file use |
| File-safety / TOCTOU / OS isolation | No complete implementation or evidence | Cannot claim general file processing safe |
| Publisher provenance | Not independently corroborated | Must default to unverified |
| AI security review | Internal model-generated technical assessment | Not independent human certification |
| Exact owner authorization for verifier implementation | Not evidenced by milestone title or PR merge | **Implementation withheld** |

## Required BTC-043 decision

To develop the narrow **synthetic-only** verifier above, record an attributable owner decision naming this exact file list, branch/commit baseline and explicit exclusions. Also record the accepted resource budget, synthetic fixture outcomes, and security limitations. That decision would authorize **development and tests against invented files only**, never real exchange data or strategy execution.

BTC-028's independently authenticated security sign-off prerequisite remains unresolved for any actual market-data verifier. Do not silently mark it satisfied by AI analysis or successful unit tests.

**Prohibitions unchanged:** No real BTC/USDT candle ingest, Binance API/keys, source-authenticity claims, H01 indicators/backtesting/optimization, paper/testnet/live orders, automated trading, spending or deployment.

**BTC-042 decision: SPECIFICATION READY FOR REVIEW; NO IMPLEMENTATION OR TRADING AUTHORITY GRANTED.**
