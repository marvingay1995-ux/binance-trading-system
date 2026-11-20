# BTC-015 — Registered forward strategy research

**Status:** Experimental data-admission safeguards only. No trading, live orders, paper orders, keys, or new performance claims.

## Evidence freeze

On November 19, 2026, BTC-014 demonstrated 1/6 positive windows for the 1h SMA 5/20 and 2/6 for 4h, with worst-window returns approximately -5.78% and -2.92% respectively. These were retrospective, previously viewed periods. The BTC-008 earlier holdout was also reported unsuccessful but cannot be independently reproduced from the lost original code.

The 1h SMA 5/20 baseline is rejected for promotion. The 4h SMA 5/20 is a **comparison benchmark**, not a selected winning strategy. Do not tune the known 2025-11 through 2026-10 dataset, retrofit regimes, or claim that previously observed windows became fresh holdouts.

## Preregistered prospective evidence

- Symbol: BTCUSDT Spot; interval: **4h** only
- Beginning of unseen period: **2026-11-01T00:00:00Z** (strict exact start; historical data through 2026-10-31 was already evaluated)
- Minimum unseen contiguous interval: 60 complete calendar days
- Strategy: fixed SMA 5/20 with signals only from completed bars, and next-open simulated execution
- Costs and constraints: frozen in `REGISTERED_CONFIG`; they are **illustrative** and not verified exchange values
- Data: full unmodified candle JSON, source URL and SHA256, collection time, complete-bar checks, and a research commit identifier
- Evaluation: return, worst drawdown, transaction costs, closed trades, no-trade and buy-and-hold context, sensitivity and significance review; **not** a paper/live permission
- Promotion: none automatic. Separate human review and an additional genuinely fresh confirmatory period are required

Because 60 days after 2026-11-01 is 2026-12-31, the minimum forward interval does not exist yet on November 19, 2026. The gate should reject premature submissions.

## Research hypotheses for future separate preregistrations

1. Trend regime hypothesis: simple long-only exposure only during a long-term upward trend might reduce churn versus the baseline; **no parameters selected or code executed under this hypothesis**.
2. Volatility control hypothesis: rejecting especially volatile entries might improve the simulated downside tail; **not tested and no performance claim**.

These are exploratory ideas, not approved replacement strategies. Any specific entry/exit rules must be frozen and separately versioned *before* a new untouched future sample is analyzed.

## Remaining engineering blockers

The baseline's 2% intraday loss is not guaranteed, public exchangeInfo snapshots are unverified, realistic partial fills and restart reconciliation are missing, and evidence from future-market data cannot guarantee profits. BTC-015 is a data-integrity/preregistration foundation only. **NO GO: paper and live trading.**
