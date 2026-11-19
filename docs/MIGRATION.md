# Migration provenance and limits

## Origin
Previous project: `donmax46/Btc-market-watcher-`. The user reports losing access to both `donmax46` and `lastchrisedxb-cmd`. Destination: `marvingay1995-ux/binance-trading-system`.

The original source files, commit history, tests, configurations, and artifacts were **not transferred** because the original repository was inaccessible. This is a **reconstruction of the documented requirements and reported historical results**, not a code migration. Never mark earlier implementation stages as verified here without recovered source and fresh testing.

## Reported historical stages
- BTC-001–005: previously reported as merged, with historical backtesting, simulated positions, order-size validation, testnet order execution and reconciliation. None of these claims is independently verified in this destination.
- BTC-008: reported failed holdout: -4.794656 USDT, win rate 33.33%, profit factor 0.38. Original raw trade ledger, timeframe, sample size, fee model and code are unavailable; treat these as **reported**, not independently reproduced.
- BTC-009: next proposed stage is strategy diagnosis, recovery and independent validation; no strategy performance claim or live execution permission.

## Transfer acceptance
1. Preserve historical provenance and distinguish reported results from fresh verified results.
2. Reconstruct components only after requirements and independent tests are written.
3. Keep credentials out of repository and CI logs.
4. Keep live execution disabled until a separate, explicit authorization after validation.
5. Never assume profitable trading, even if a backtest passes.

## Access and privacy
This destination repository was observed as **public** at migration time. Do not store secrets, account identifiers, balances, private logs, or API keys here. Consider making it private before adding sensitive operational material.
