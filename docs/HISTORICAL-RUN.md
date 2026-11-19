# Real-data historical verification

The GitHub Actions workflow **Historical research validation** can be started manually with 180, 365, or 730 days of public BTCUSDT candles. It runs 1h and 4h independently, fails on incomplete market data, runs unit tests, then stores candle JSON and chronological evaluation reports as workflow artifacts for 14 days.

The workflow is **not scheduled**, does not use credentials and cannot submit orders. GitHub-hosted runners may be blocked from Binance public endpoints by regional network restrictions; that is a data-availability failure, not a strategy result.

A completed workflow with passing tests is not a profitability endorsement. Review both holdouts, trading fees, volatility regimes, order-size realism, model uncertainty and the historical BTC-008 failure before any decision about paper trading. The fixed 5/20 SMA baseline has not been optimized or independently proven.

Run location: repository → Actions → Historical research validation → Run workflow. Choose branch `feature/btc-009-research-engine`, select 365 days, and inspect both artifacts. Never add API keys or secrets.
