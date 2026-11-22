# BTC-047 — Offline Verifier Security Hardening (Synthetic-Only)

**Depends on BTC-046 PR #33.** At the time this branch was created, BTC-046 was not merged into `main`; therefore BTC-047 targets its feature branch. Merge BTC-046 before retargeting BTC-047 to `main`.

## Implementation changes
- `_safe_read`: on POSIX opens the trusted synthetic input root once as a directory descriptor and opens allowlisted basenames relative to it with `O_NOFOLLOW` where available; checks regular-file identity and stat stability; reads in bounded 8KB chunks. On platforms without POSIX `dir_fd` support this falls back to a less-assured path open and does **not** claim equivalent security.
- `_csv_canonical`: validates small synthetic row lengths *before* materializing the CSV parser's row list; explicitly rejects quoted/multiline values outside `synthetic-candle4h-v1`.
- `_zip_csv`: checks compressed and declared expanded sizes, as well as a ratio ceiling, before reading a single stored `invented.csv` member. No extraction or general archive acceptance.
- `write_report_new`: refuses symlinked output-parent paths and existing report destinations. It still relies on path-based exclusive creation; it is not a fully atomic, directory-FD-confined transaction.
- Unit tests exercise deterministic synthetic golden hashes, below/exact file limits, known basenames, symlink and directory rejection, overlong/quoted CSV, ZIP metadata sizes, output-root refusal and no-network instrumentation.

## Remaining security and authorization limitations
- All public verification remains tied to exact BTC-036 invented golden CSV/ZIP hashes; arbitrary files cannot pass. The test helpers themselves are not a general malicious-file verifier.
- This is **defense-in-depth**, not a proof of safety against a privileged local attacker racing directory moves, modifying files during reads, or manipulating writable parent directories.
- BTC-027's proposed 25 MB raw / 50 MB expanded / 100K records / 30-second deadline are **not validated**. BTC-047 keeps the narrow 200KB fixture guard.
- File parsing still uses an in-memory 200KB cap; input-root owner, OS sandbox, hard runtime memory/CPU enforcement, atomic output publication and authentic exchange provenance require separate evidence.
- No independent human certification has been performed. Historical BTC-028/039 NO-GO remains in force for real market-data verification.
- No Binance network/API access, credentials, H01 indicators/backtests, paper/testnet/live orders or automated trading.

## Review standard
Treat GitHub Actions results as evidence only for these synthetic regression cases. Before any real-data boundary decision, test on supported OSes and produce explicit file race, resource, network isolation and provenance evidence.
