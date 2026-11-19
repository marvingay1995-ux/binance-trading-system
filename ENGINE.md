# BTC-009 research-only reconstruction

This project has **no authenticated API, credentials, account access, order placement, or live trading**. The original source was inaccessible; this is new code, not a source transfer.

Python 3.10+, standard library only:

```sh
python -m unittest discover -s tests -v
python -m btc_engine.cli fetch --interval 1h --start-ms 1704067200000 --end-ms 1704153600000 --output candles.json
python -m btc_engine.cli backtest --interval 1h --input candles.json
```

The fetcher uses public Binance Spot klines, validates complete UTC-aligned 1h/4h series, and fails on gaps, duplicate timestamps, bad OHLCV or incomplete pages. The baseline is a **non-optimized 5/20 SMA crossover** with signals from closed bars and fills at next-bar opens. Synthetic fees, spread, slippage, minimum quantity/notional and step-size are modeled. Exposure is capped at 30%, with a UTC-day 2% open-mark loss halt and next-open liquidation. Gaps can exceed that limit. Filters are **illustrative, not verified Binance filters**.

**Verification limits:** Unit tests use synthetic candles; they do not establish profitability. No real historical data was fetched or backtested, no untouched holdout/walk-forward analysis has been completed, no restart/reconciliation or partial-fill simulator exists, and no live execution is authorized. Benchmark buy-and-hold ignores costs. Open inventory is marked at the final close and excluded from closed-trade win rate. BTC-008 historical results remain unverified.
