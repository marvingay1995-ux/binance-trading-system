# BTC-044 — Synthetic-Only Offline Fixture Verifier Evidence

BTC-043 PR #30 merged into `main` at `5fa441317e3aa4b863d68c6ab011036c08c3f2cb`. The user requested BTC-044 implementation. This authorizes code development and tests **only against generated invented fixtures**; it does not modify BTC-028/039 denials for general market-data verifier implementation, trading or H01 backtests.

## Exact implementation
- `btc_engine/offline_fixture_verifier.py`: accepts only `golden.csv` and `golden.zip` from the BTC-036 generator under a new local directory. Compares bytes to source-controlled deterministic fixtures before interpreting them. No user-provided arbitrary CSV/ZIP is trusted.
- `tests/test_offline_fixture_verifier.py`: positive invented data, altered bytes refusal, unknown files, symlink, out-of-root, no-overwrite report and patched-network tests.
- This evidence document records limitations.

## Security boundaries and limitations
The verification is **synthetic-only and tightly allowlisted**, using the exact source-controlled fixture hashes and the BTC-034 canonical digest. A passing result says only `SYNTHETIC_INTEGRITY_ONLY` and explicitly states `publisher_provenance_verified=false`. It is not authentication of actual Binance files.

Input size is capped at **200,000 bytes per local fixture**, not the larger unverified BTC-027 production proposals. It requires a new directory produced by the synthetic generator, only handles one ZIP member, does not extract archives, refuses symlink file entries at open and writes reports by exclusive-create. These controls are not an OS sandbox and do not fully eliminate malicious local TOCTOU races. Restricted filenames plus known fixture hash binding prevent this entry point from accidentally validating arbitrary exchange data.

Existing S01–S18 synthetic helper probes are not all executed end-to-end through this limited verifier. This milestone does not certify general-purpose file/ZIP security, production size/time/CPU bounds or real-data provenance. Network prohibition is checked with monkeypatch instrumentation, not independent OS isolation.

**No permissions changed** for real market data ingestion, H01 signals/backtesting, Binance account/API access, paper/testnet/live orders or automatic trading. BTC-028/039 NO-GO remains unchanged.
