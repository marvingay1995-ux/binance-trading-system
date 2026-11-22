# BTC-033 — Security Contract Acceptance and Synthetic Test Authorization

**Decision: CONDITIONAL DESIGN ACCEPTANCE ONLY. NO authorization for executable synthetic fixture generation or testing has been granted by this program.**

## Baseline and evidence

BTC-032 PR #21 merged on 2026-11-22 at `4f99e21706d75d27f604f4500005bee610784835`. Its revised contract `btc_engine/verifier_security_v2.py` addresses eight BTC-031 design findings in written requirements, not running file I/O controls. This review binds the exact report fingerprint and unchanged H01-v2 specification fingerprint in `btc_engine/security_contract_acceptance.py`.

BTC-032 passing unit tests demonstrate registry consistency, not successful ZIP traversal defense, data-integrity validation, independent human certification or deployment safety.

## Acceptance findings

| Item | Review result | Required closure |
| --- | --- | --- |
| ACPT-01 | Canonical OHLCV, CSV column mapping, encoding and golden hashes not final | Version a complete wire schema and deterministic synthetic golden vectors |
| ACPT-02 | Some F08–F12-derived cases remain compound | Split into independent single-fault cases with stable error codes |
| ACPT-03 | Budget and timeout limits are not measured/enforced | Set precise bounded test-runner and boundary evidence rules |
| ACPT-04 | File/ZIP/TOCTOU and network restrictions are requirements only | Define platform-specific isolation and test arrangements before verifier implementation |
| ACPT-05 | No external security sign-off or scoped owner authorization | Keep both distinct; do not mark approved based on AI findings or merge |

### Separate synthetic-only scope proposed for a future authorization

**Allow only after explicit scope approval:** generate *invented* CSV/ZIP fixtures that cannot be confused with authentic exchange market data; store immutable expected-output golden digests; test fixture generator determinism and negative fault injection in an isolated environment.

**Do not allow under this scope:** processing genuine BTC exchange archives, building a general Binance file verifier, downloading market data, computing H01 SMA signals or P&L, trading, credentials or API calls.

No synthetic generator or fixtures are implemented in BTC-033. All implementation, synthetic execution, data-verifier, H01 backtest, paper and live permissions remain false.

## Decision clarification

The requested **Synthetic Test Authorization** has been *reviewed*, not granted. Earlier BTC-026–029 records require explicit, attributable product-owner approval before implementation; the milestone title alone is not that permission. The accepted design work is not an independent security certification.

A future explicitly scoped decision can permit **synthetic-only test generation** without permitting actual data-verifier implementation. Such a decision must name the exact repository version, expected files, bounded resources, fixtures and negative controls. Keep separate any later permission to verify real data or run strategy simulations.

## Next step

**BTC-034 — Synthetic Fixture Specification Completion and Scoped Implementation Decision**: finalize wire schema, golden synthetic vectors and one-fault test matrix, then seek an explicit owner decision for synthetic-only generator implementation. No progress to strategy backtesting is implied.

**No real data accessed, no Binance credentials, no live/paper orders.**
