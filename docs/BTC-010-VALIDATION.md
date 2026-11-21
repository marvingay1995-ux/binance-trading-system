# BTC-010 — Historical verification protocol

## Current status
The rebuilt engine is a research prototype, not a proven strategy. No live trading.

## Required sequence
1. Obtain public BTCUSDT 1h and 4h historical klines with `python -m btc_engine.cli fetch`. Choose complete UTC-aligned start/end timestamps; store input file hashes, collection date, source URL and code commit.
2. Run `python -m btc_engine.evaluate --input candles.json --interval 1h --output report.json` (repeat for 4h). This is a **fixed 5/20 SMA baseline**, not a strategy chosen by optimizing on the holdout.
3. Review chronological train/validation/holdout returns, drawdown, event count and buy-and-hold price comparison. The split evaluator carries positions across boundaries and its split returns are not independent restart simulations.
4. Do not promote on the basis of a single backtest. Add realistic exchange filters, sensitivity to fees/spread/slippage, multiple market regimes, trade-level holdout metrics, statistical uncertainty, and walk-forward testing.
5. Record explicit decision: reject / research further / authorize **paper trading only**.

## No-go conditions
Missing data, insufficient sample, inconsistent timestamps, unverified Binance filters, losses exceeding tolerance, insufficient independent evidence, or any request to use credentials or place real orders.

## Important limitations
The 2% loss halt is evaluated at bar opens, not a guaranteed stop-loss: gaps and intrabar moves can exceed 2%. The present simulator assumes instant full fills, no market impact and fixed costs. The profit factor is closed-trade-only; final open inventory is marked to market. No automatic live trading or real-account integration is included.
