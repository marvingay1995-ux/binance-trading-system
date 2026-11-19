# Binance Trading System

Migration destination for the previously planned BTC/USDT automated Spot trading project.

**Status: documentation-only migration; no live trading authorized.** The prior repository is inaccessible, and its source code has not been recovered. Historical completion claims are unverified in this repository.

- Exchange: Binance; BTCUSDT; 1h and 4h research timeframes.
- Spot only; no futures, margin, or leverage.
- Maximum total exposure: 30% of account equity.
- Maximum daily loss: 2% of account equity; fail closed when reached or when risk data is unavailable.
- First 20 live orders/trades require explicit human approval; no automatic live execution currently authorized.
- Withdrawal permission must remain disabled on any future exchange API key.
- No API credentials, real orders, spending, or deployments in this migration.

Next: BTC-009 independent strategy recovery and validation. See migration documentation in the proposed pull request.
