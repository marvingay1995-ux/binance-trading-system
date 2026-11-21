# BTC-014 — Fixed-strategy chronological stability review

This is a **walk-forward-style diagnostic**, not a completed independent walk-forward optimization/validation experiment. Parameters are frozen (SMA 5/20). We do **not** select better parameters based on previously viewed BTC-011/012/013 data.

## Implementation
- Start observation after 40% of each historical candle set.
- Report six consecutive, non-overlapping 10%-length windows, each using the continuous full-history simulation state.
- Compare baseline transaction costs with doubled and tripled fees, spread, and slippage.
- Report per-window returns, drawdowns, positive-window counts and simple uncosted BTC price benchmarks.
- Bind output to source candle SHA-256; no credentials, real orders, providers, or account balances.

## Critical interpretation
These datasets and the last 20% holdout have already been examined. The six windows are **not six new independent holdouts**. Financial markets are nonstationary; window stability here does not prove a persistent edge or statistical significance. For trustworthy evidence, freeze the research specification and evaluate genuinely later unseen periods, with a verified, exchange-complete execution model.

BTC-013 exchange filters, partial fills, loss-limit enforcement, and restart/reconciliation remain blockers. Automatic paper trading and live trading both remain **NO GO**.

## GitHub verification
Use the existing `Archive historical validation` manual workflow on `main`; it checks out the research branch and generates 1h/4h BTC-014 reports alongside BTC-011–013 results. This workflow is manually triggered, not scheduled.
