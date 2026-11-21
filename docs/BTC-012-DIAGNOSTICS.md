# BTC-012 — Strategy diagnostics and risk verification

**Decision gate remains NO GO for live trading.** Research-only: read-only archives, no authenticated exchange access, no orders, no credentials, no margin/futures.

## Evidence from BTC-011 run 44541647360
The official monthly archive workflow passed on 2026-11-19 (29 unit tests per job), with 8,760 1h candles and 2,190 4h candles for 12 complete months. The continuous-equity holdout produced -0.6653% for 1h (max holdout drawdown 6.5219%), and +0.6167% for 4h (max holdout drawdown 4.2317%). BTC benchmark price change was +11.8948% over the holdout, uncosted. These are simulated and not evidence of robust advantage.

## New diagnostic checks
- Reconstruct each full round-trip long trade from events; reject unmatched exits or quantity discrepancies
- Compute closed-trade win rate, mean P&L, gross win/loss and profit factor; attribute exit events to holdout separately
- Audit closing-equity drawdowns and flag periods where the modeled 2% UTC-day loss threshold is exceeded
- Compare baseline to double-fee, double-slippage, double-spread, and combined-stress scenarios **without retuning parameters**
- Report sample budget/minimum-notional feasibility; **exchange filters remain unverified**; initial assumed budget of 30 USDT at 100 USDT capital is illustrative and not valid at every price
- Report holdout equity change without pretending the split resets positions
- Fail closed if candle data is missing or inconsistent

## Known model gaps
The 2% daily-loss rule is checked at candle opens, so its limit is **not guaranteed**. Intrabar stops, live-order book liquidity, partial fills, price/quantity filters, fees-by-account, market impact, Binance availability, state persistence and outage handling are **not implemented**. Trade entry could predate the holdout boundary. The cost-sensitivity analysis is a diagnostic, not optimization or reliable profitability proof.

## Reproduction
```
python -m unittest discover -s tests -v
python -m btc_engine.diagnostics --input BTCUSDT-1h-candles.json --interval 1h --output BTCUSDT-1h-diagnostics.json
python -m btc_engine.diagnostics --input BTCUSDT-4h-candles.json --interval 4h --output BTCUSDT-4h-diagnostics.json
```

**Exit criteria:** verified exchange filters, data provenance/hashes, stress testing, risk-limit remediation, reproducible independent review, and paper-only authorization after a fresh decision. No live trading authorization.
