# BTC-011: Offline/public archive historical data path

Run **Archive historical validation** from GitHub Actions on `main`. The workflow checks out the research branch and downloads official public *Spot* monthly BTCUSDT 1h and 4h ZIP archives. It uses complete calendar months (6, 12, or 24), rather than exactly 365 rolling days, and publishes an explicit source manifest with per-archive SHA-256 hashes and a candle-data hash.

Important: Spot Binance Vision timestamps are **microseconds from 2025-01-01**, milliseconds before then. The archive importer handles both and rejects sub-millisecond timestamp ambiguity, invalid prices, duplicates, missing hours, truncated months, and unexpected ZIP contents. No credentials and no live orders.

The system **will fail closed** if the archive host returns HTTP 451 or other errors. It does not bypass geographical restrictions and does not mask missing candles. GitHub may be blocked from the archive service as well as from the trading API. In that case import an independently obtained dataset in an authorized environment; do not mislabel synthetic fixtures as historical results.

**No profitable strategy is established** until real data is processed and reported. Execution assumptions (fees, spread, filters, fills, BTC-008 failure) remain unresolved. Do not activate live trading.
