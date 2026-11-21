# BTC-027 — Local Verifier Security Threat Model and Test Fixture Contract

**Decision: proposed threat model and fixed synthetic test fixture specification; NO GO to data-verifier implementation without a separately recorded authorization and security review.** This PR neither implements the ZIP/CSV verifier nor validates market data.

## Context
BTC-026 PR #14 merged into main at `f6e4056e01d6efde1a99d94a8f73c236b48bba63`. BTC-026 defined a possible narrow **local BTCUSDT 4h data-only** verification scope and explicitly denied implementation in the absence of product-owner and independent security approval. BTC-023 continues to prohibit H01 strategy simulation. The proposed controls below are specifications, not evaluated protections.

## Trust boundaries and attacker model
Treat every file path, ZIP/CSV byte, claimed origin URL, timestamp-unit declaration, SHA256 value, untrusted metadata and source statement as attacker-controlled. The potential attacker may submit malformed, expensive or misleading files, seek unauthorized reads/writes, mislabel time series or persuade a future reviewer that a matched hash proves Binance originated the file.

Only local explicitly supplied regular files would be eligible under a later approved implementation. A report must separate **format checked**, **content hash matched**, **candles verified** and **publisher authenticated**. A plausible URL and SHA256 never establish provider provenance by themselves.

## Threat classes and planned mitigations
- **Archive and filesystem:** reject symlink/device/FIFO inputs, path traversal, absolute ZIP entries, nested archives, encrypted entries, CRC failure and ZIP bombs; do not extract ZIP entries to disk.
- **Resource exhaustion:** proposed upper limits of 25 MB raw bytes, 50 MB expanded bytes, 1 archive entry, 100:1 compression ratio, 100,000 rows, 4096 bytes per CSV row and 30 seconds processing. These numerical limits are **draft controls requiring review**; do not treat them as already measured or safe in every environment.
- **Parsing and time:** explicit per-file millisecond or microsecond timestamps; reject inference, mixed units, duplicates, missing 4h intervals, invalid OHLCV, timestamp misalignment and non-final candles.
- **Tampering and source impersonation:** recompute digests from the same opened bytes that are parsed, preserve file-byte sizes and hashes, and require externally corroborated source information for authentication claims.
- **Capability isolation:** never include network, API-key, portfolio, SMA signal, optimizer, backtest or order capabilities in the verifier process.

## Synthetic test fixture contract — future tests only
`btc_engine/verifier_threat_contract.py` records **15 named cases** F01–F15 with expected acceptance/rejection behavior. The accepted examples represent **synthetic** complete 1200-bar warmup data and 360-bar future data; other cases force hash mismatch, missing data, mixed timestamps, malformed OHLCV, archive traversal/expansion, incomplete candles, fake source assertions and prohibited features.

**These fixtures are a contract, not actual ZIP/CSV samples.** The unit tests in this PR only verify registry completeness, immutable digests, denied permissions and declared limits; they do not run an unbuilt verifier against hostile inputs. The F02 60-day synthetic fixture must not be misrepresented as presently available market data; the registered real window cannot complete before **2027-01-30 00:00 UTC**.

## Proposed independent security acceptance criteria
1. Reviewer confirms the exact file/ZIP threat model, local-only I/O boundary, no symlinks/extraction/network, bounded memory/runtime and explicit documented timestamp units.
2. Reviewer signs off the maximum-file-size, expanded-ZIP and row/time ceilings after measuring realistic synthetic stress cases.
3. All F01–F15 cases must be implemented as reproducible synthetic fixtures **only after separately authorized code implementation**. A source authenticity check must not silently pass from an unverified manifest.
4. Approval ledger must reference the immutable H01-v2 specification hash and this contract SHA256, reviewer identity, review time and scope; any material amendment receives a new version.
5. Separate explicit product-owner authorization must name the strictly local-file data-verifier implementation. A generic milestone request or PR merge does not itself authorize an exchange connector or strategy simulator.

## Remaining gates
All authorizations in the contract remain false. Next proposed milestone **BTC-028 — Local Verifier Implementation Decision** may record either approval or refusal for a strictly data-only offline implementation after the above review; it must **not** extend to H01 signals, strategy backtests, paper trading or live orders. In the absence of independent signoff, the correct decision remains NO GO.

**No real candle data inspected or authenticated; no market or trading outcomes produced.**
