# BTC-013 — Execution realism and qualification gate

**Status: research-only. Decision: NO GO for paper or live trading.**

The first BTC-011 historical run generated full-year data and fixed 5/20 SMA holdout returns of -0.6653% (1h) and +0.6167% (4h). BTC-012 diagnosed 2% daily-loss limitations. None of these results proves positive expectancy.

## Delivered
- Decimal-based BTCUSDT Spot filter *snapshot parser*, rejecting missing or untradable Spot information, malformed values and missing min-notional market applicability.
- Hypothetical quantity, step-size, notional and budget checks, *not* an authorized exchange order submission or exact market-order validation.
- Historical 1x, 2x, 3x friction sensitivity on fixed strategy without modifying its SMA parameters.
- Explicit blocker report for unverified filters, unmodeled partial fills and restart recovery, unenforceable intrabar loss caps, absent independent walk-forward tests, and absent live authorization.
- No credentials, exchange account access, endpoints for orders, or any autonomous trading.

## Critical limitations
A downloaded exchangeInfo JSON snapshot would need independent source, timestamp, authenticity, symbol permissions, market lot size, notional applicability, fee tiers and refresh checks before it can support any order decisions. This module cannot certify an external snapshot. Its order-check examples are neither exchange-complete nor live safe.

OHLC bars do not prove worst-case intrabar execution, liquidity, position reconciliation or the 2% daily-loss bound. Cost stress does not prove statistical significance. **No live trading and no paper-trading promotion should follow solely from these outputs.**

## Next stage after reviewed diagnostics
Build verified filter snapshot acquisition, reproducible walk-forward methodology, and a separate paper-only execution emulator after independent review and explicit approval. Do not optimize the previously viewed holdout.
