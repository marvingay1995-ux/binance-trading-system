# BTC-034 — Synthetic Fixture Specification Completion and Scoped Implementation Decision

**Decision: SYNTHETIC SPECIFICATION RECORDED; IMPLEMENTATION AUTHORIZATION WITHHELD.** No actual synthetic fixture files were generated or executed. No actual market files were inspected.

## Source and scope
BTC-033 PR #22 merged to `main` at commit `1c8ddb1f5af0760c60e30f5d5cf5849a9fc563f5` on November 22, 2026. Its design acceptance was conditional, with five blockers. BTC-034 provides a narrow **invented-data-only** wire specification, reproducible literal reference vectors and a refined single-fault matrix. This is not a security certification, local-file verifier implementation or permission to run synthetic fixtures.

### v1 illustrative 4h data encoding
Columns: `open_time_ms,open,high,low,close,volume`, UTF-8 **without BOM**, LF separators, header required. Numeric grammar is unsigned finite base-10 decimal without exponent or surrounding whitespace. Open timestamps are integer UTC milliseconds aligned to 14,400,000 ms; no silent timestamp-unit conversion. Preserve data order and reject duplicate or out-of-order records.

Canonical form: UTF-8 newline-delimited JSON objects in the fixed column order. `open_time_ms` is an integer; decimal OHLCV fields are strings normalized without trailing fractional zeros; each record ends with LF. This is a proposed synthetic-only contract, not necessarily the exact raw Binance CSV schema.

## Literal golden reference vector — invented values
```csv
open_time_ms,open,high,low,close,volume
1778803200000,100,105,99,103,1.5
1778817600000,103,108,102,107,2
```

The raw UTF-8 CSV including final LF has SHA-256 `788537557c96f0792654995f4ddbbf8b1508f4e6972ed7aaa98afeb9c3e890ed`. The corresponding canonical JSONL with final LF has SHA-256 `1ae0a6a2014338e2005da5de366173f1c62a25d5e5624d68ac73a19d63b395b2`. These digests were calculated from **literal invented two-row data**, not downloaded market archives. They establish a reproducible miniature format reference only, not the required 1,200-row warmup.

## Negative test contract
Eighteen `S01–S18` proposed single-fault scenarios cover timestamp precision, missing or duplicate bars, invalid OHLCV, oversized fields, checksum tampering, unsafe ZIP paths and member types, CRC mismatch, expansion and unsupported compression, symlink input, output collisions, unclosed candles, forged source claims, forbidden network/trading calls, and record limits.

Each scenario specifies its expected denial or unverified provenance state but **has not been constructed or run**. Some faults have OS/platform-dependent behavior and still need a concrete isolation test harness.

## Authorization boundaries

The user requested BTC-034 specification completion and an implementation decision. That request is not an explicit approval to create executable fixture-generating code, and BTC-033 requires a separate scope decision. All implementation and trading flags remain false.

A future explicit authorization could permit **only** a deterministic synthetic CSV/ZIP fixture generator, golden digest fixture tests and negative controls, within the proposed size/time limits and no-network/no-exchange runtime. It would not authorize a general verifier for real market files, source authentication, H01 strategy simulation, paper/live trading or API credentials.

### Outstanding before implementation
1. Explicit product-owner approval naming the narrow synthetic-only generator scope and repository reference.
2. Acceptance of deterministic fixture encoding, golden vectors and single-fault expected codes.
3. Test harness design documenting OS-specific symlink tests, no-network boundaries, and bounded resource behavior.
4. Distinct later review of whether an actual local market-data verifier may be built; BTC-028 NO-GO remains binding.

**Next technical step:** Request approval for a synthetic-only implementation with exact file list; do not infer approval from a merged PR. All trading remains disabled.
