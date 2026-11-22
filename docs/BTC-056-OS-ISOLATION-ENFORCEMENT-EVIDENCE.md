# BTC-056 — OS Isolation Enforcement Verification (Synthetic-Only)

**Baseline:** BTC-055 PR #45 merged to `main` at `ee0510e28bf3280c424f1386ced7b2e8369d1fbc`; merged-main GitHub Actions run `45042221171` passed **332** tests.

## Narrow enforcement experiment
The executable `btc_engine/synthetic_enforcement_probe.py` attempts an **unprivileged** Linux user/network namespace with no sudo, privilege escalation, container downloads, provider configuration, credentials or market-data files. Before any socket operation, a child must observe a distinct network namespace, the **loopback interface only**, and **no non-loopback routes**. Only after all those checks pass does it attempt a TCP connection to **198.51.100.1:9 (RFC 5737 TEST-NET-2)**, which must fail at the kernel routing layer with ENETUNREACH/EHOSTUNREACH. This experiment does not send traffic outside the isolated namespace when those strict preconditions hold. The child also verifies Linux CPU and virtual memory rlimits.

Unsupported runners, denied unprivileged namespaces, missing tools, preflight failures, unexpected connect results, malformed evidence, or timeouts produce **ENFORCEMENT_UNAVAILABLE** and never a passing security assertion. Actual CI output contains `BTC056_ACTUAL_PROBE=` with the capability verdict; a green suite alone does not demonstrate kernel enforcement.

Even on an observed kernel-route refusal, `comprehensive_network_isolation_verified=false` and `security_certified=false`. A route denial for one reserved address is **not** proof of a security policy covering all sockets, IPv6, Unix sockets, namespace transitions, privileged children, DNS, mounts or hostile code.

## Residual risks
- R48-01: filesystem ancestor TOCTOU and root ownership remain open.
- R48-02: comprehensive OS-level network, process, privilege and filesystem confinement remains open; a limited kernel egress refusal could reduce uncertainty only.
- R48-03: production resource limits and general CSV/ZIP parsing still unproven.
- R48-04: publisher authenticity and independent security review absent.
- R48-05/06: report crash durability and unmodeled failures remain.
- R48-07: Windows parity absent.
- R48-08: frozen synthetic fixture public-verifier scope unchanged.

**NO GO**: arbitrary or real Binance market data, exchange API or account credentials, H01 indicators/backtesting, paper/testnet/live orders, automated trading, deployment or spending. BTC-028/039 historical gates unchanged.

**Next:** Reassess actual CI probe verdict and plan further synthetic-only OS confinement tests only if the host supports them; do not broaden data scope on the strength of this experiment.
