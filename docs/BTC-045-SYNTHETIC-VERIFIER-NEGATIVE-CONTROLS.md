# BTC-045 — Synthetic Verifier Negative-Control Expansion

**Baseline:** BTC-044 PR #31 merged into main as `e59a7e84ed86fe594e2af8e9779f3f45725765fb`.

## Implemented and actually tested

- Additional unit tests directly call the BTC-044 `verify_generated` entry point with the known allowed synthetic filenames and modify their bytes to verify that **known-fixture SHA-256 allowlisting rejects tampering**.
- Separate tests call the verifier's internal CSV and ZIP parsers with deliberately malformed *invented* byte strings. These tests distinguish real parsing checks from the public entry point's earlier hash gate.
- Tests exercise the file size threshold, symlinks and nonregular inputs, missing/trailing newline, invalid UTF-8/BOM/CRLF, wrong columns, overlong CSV fields, duplicate/missing 4h timestamps, invalid OHLCV, unsafe ZIP members, symlink ZIP metadata, CRC failure, unsupported ZIP method, multiple ZIP entries and protected report output.
- The implementation now consistently returns `ROW_TOO_LARGE` for oversize CSV fields and `CSV_INVALID_ENCODING` for `csv.Error` rather than surfacing the lower-level parser exception.
- Network/process monkeypatch instrumentation remains restricted to fixture tests; it does **not** establish an OS sandbox or fully isolated process.

## Critical security interpretation

**Public verifier:** Only `golden.csv` and `golden.zip` with source-controlled, frozen synthetic hashes are accepted. Modified S01–S10/S15 artifacts are refused with `HASH_MISMATCH` at the public entry point, before specialized parsing. They are **not** claimed to produce their fixture-specific error codes through `verify_generated`.

**Parser probes:** Specialized error codes are tested by invoking private parsing helpers on invented bytes, not by bypassing the public allowlist for arbitrary real exchange files. This is not a production parser audit.

No new support for arbitrary CSV/ZIP files, Binance market data, account credentials, exchanges, H01 indicators, simulated/live trades or orders is introduced.

## Remaining gaps

- Only the small BTC-044 fixed fixture set is accepted; this does not test authentic publisher identity or full prospective data partitions.
- No verified protection against TOCTOU local adversaries, ZIP expansion at 50 MB, 100k records, 30-second deadlines or general malicious input.
- CSV/ZIP parser helper tests are useful but do not demonstrate general verifier security; future real market data processing would require a separately authorized and reviewed implementation.
- BTC-028/039 general market-file verifier NO-GO and all trading restrictions remain unchanged.

**Next recommended milestone:** BTC-046 — Synthetic-Verifier Security Evidence Review and Real-Data Boundary Decision (review-only).
