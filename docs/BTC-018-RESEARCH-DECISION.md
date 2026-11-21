# BTC-018 — Research Decision and Strategy Freeze

**Decision: RETIRE both fixed SMA 5/20 variants from trading consideration.** They may be retained in the repo only as reproducible historical comparators. Neither should be submitted to paper/testnet/live execution by an automation.

## Evidentiary record

- Source: [GitHub Actions archive validation run #44915102425](https://github.com/marvingay1995-ux/binance-trading-system/actions/runs/44915102425), using commit `4e5688b84619cc6f047b8592b4145bd3188e44a4` on `main`
- Two successful timeframes; each passed 63 unit tests; historical archive, BTC-012 diagnostics, BTC-013 qualification, BTC-014 retrospective stability checks succeeded
- **1h:** last-20%-window baseline -0.6653%; doubled friction -5.4336%; tripled friction -9.9870%; positive in 1/6 retrospective windows; full-period baseline max drawdown 29.5118%; 284 completed round trips
- **4h:** last-20%-window baseline +0.6167%; doubled friction -0.5826%; tripled friction -1.7129%; positive in 2/6 retrospective windows; full-period baseline max drawdown 8.9311%; 63 completed round trips
- These were simulated, path-dependent, retrospective results. The last 20% was already inspected before this decision. Do not portray previously reviewed data as an untouched new holdout.
- Cost sensitivity is based on synthetic fees, spreads, and slippage, **not verified actual Binance fills**. No profit is promised.

## Binding decision for future program work

1. Freeze SMA 5/20 1h and 4h as **benchmark only**. Do not optimize their parameters and re-label them as fresh qualified candidates.
2. Preserve BTC-015's December 1, 2026 preregistered 4h comparison window as *observational benchmark research only*. Admission of a future dataset does **not** reverse retirement or authorize paper/live trading.
3. Freeze the displayed BTC-017 evidence and source commit for audit. Any report generated on later/different data needs its own SHA and clearly labeled provenance.
4. Establish a **separate research protocol** for any new hypothesis, with a frozen entry/exit specification, realistic execution assumptions, rigorous independent out-of-sample evaluation, and explicit review. No new replacement strategy is selected in BTC-018.
5. Do not claim that software CI passing, sample profitability, or a paper simulator proves enforceable 2% loss cap or 30% portfolio exposure in real markets.

## Outstanding blockers

Real exchange-filter authentication, fee tier and quantity precision validation, market depth and partial fills, account balance reconciliation, recovery after failures, intrabar daily-loss handling, and unseen prospective evidence. BTC-018 introduces no exchange connection, credentials, order placement, recurring market monitoring, or permissions.

**Promotion authority:** DENIED for both existing SMA 5/20 strategies (paper and live). The software gate rejects both and unknown IDs; it is a research guard and does not claim to secure every possible future execution entrypoint.

## Follow-on

BTC-019 should propose and preregister **new hypotheses without using past BTC performance to choose optimal parameters**, alongside realistic and separately verified execution assumptions. Any future order execution remains contingent on a new explicit decision.
