# BTC-064 — Consolidated Trading Readiness and Critical-Path Decision

**Decision: no data acquisition, strategy backtesting, paper trading or live orders are approved by BTC-064.** This milestone identifies a shorter evidence-backed sequence of *separately authorized* work, rather than extending the Docker-only track indefinitely.

## Verified repository snapshot

- BTC-063 PR #53 merged into `main` at `0ef335d5a6ed32f8b2999366bb031a465e9e5986`.
- Merged-main GitHub Actions run `45175767479` completed successfully with **404 tests**.
- BTC-028's historical decision remains `NO_GO_LOCAL_VERIFIER_IMPLEMENTATION`. BTC-039 was also a narrower no-go for actual CSV/ZIP market-data verification. Neither is silently rewritten.
- BTC-060/061/063 reject Docker execution. CI passing synthetic tests is not an isolation certificate.
- BTC-018 *retired* both fixed SMA 5/20 variants. On the already inspected last-20% window, 1h baseline was **-0.6653%**; 4h baseline **+0.6167%**, becoming **-0.5826%** under doubled friction and **-1.7129%** under tripled friction. The six retrospective windows are not six independent holdouts; historical inspection cannot count as a genuinely new unseen test.

## Critical path: four separate gates

| Stage | Output sought | Minimum preconditions | Current authority |
| --- | --- | --- | --- |
| **R1: Public market-data research** | Bounded read-only BTCUSDT 1h/4h acquisition with logged provenance | Explicit narrow owner approval; specified public source; licensing/rate policy; independent security review of ingestion route; no account keys or order endpoints | **NO GO until separately approved** |
| **R2: New, preregistered backtest** | Reproducible evaluation of a new hypothesis, realistic fees/slippage/exchange filters, genuinely unseen prospective data | Authenticated data + separate strategy-spec approval; retire SMA 5/20 remains binding; independent validation | **NO GO** |
| **R3: Supervised paper trading** | Real-time simulated state, fills, reconciliation, risk and recovery evidence | Review strategy evidence and approve simulator; prove synthetic balance/exposure/loss enforcement, logging and kill switch | **NO GO** |
| **R4: Controlled live Spot** | Manual approval for first 20 live trades, within 2% daily-loss and 30% exposure policies | Distinct owner authorization; exchange constraints and real-risk controls; proper key scope, no withdrawals/leverage; demonstrated reliable recovery | **NO GO** |

**Important distinction:** a public, keyless read-only market-data workflow might be supportable with a narrowly reviewed parser/API route that does not use Docker at all. This is an *engineering recommendation*, not a finding that authentic market-data acquisition is presently safe or permitted. A hostile local ZIP/CSV verifier still needs its own authorization and negative tests. Do not weaken the existing historical review records to introduce an alternate implementation.

## Prioritization and explicit non-prerequisites

**Next highest-value step:** BTC-065 — read-only BTCUSDT data-source, provenance and specific approval proposal. It should present a bounded request with no account authorization, no trading, no real data fetching before approval, and a clear independent security review plan.

**Not required to scope R1:** proving all six local Docker images safe, automated trading, live order credentials, reoptimizing retired SMA 5/20, paid infrastructure. Such work may become relevant later for specific runtime choices, but it is not the sole technical path to keyless read-only research.

**Not optional for R4:** independent forward strategy evidence, realistic costs and filters, order/recovery controls, actual risk budgets and live operational safeguards. The user's indicative capital under $100 makes minimum-order/fee feasibility and non-meaningful position sizing key issues; no trading profits are guaranteed.

## BTC-064 governance

This is documentation and deterministic regression checks only. No network, data/file ingestion, strategy signals/backtesting, Binance credential handling, order placement, container execution or spending. All stage flags stay false, including after future PR merges unless a later separately approved decision explicitly changes them. Paper trading can be the first operational goal; live Spot requires an additional independent gate.
