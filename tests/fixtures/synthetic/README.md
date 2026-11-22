# Synthetic-only test fixtures

These files are generated in a new temporary directory by the offline BTC-036
generator. They are **invented test inputs**, not Bitcoin exchange data.

Run, from the repository root, with an absolute path that does not exist:

```bash
python -m btc_engine.synthetic_fixture_generator --output /tmp/btc036-invented-only
```

On Windows, supply a new absolute directory path. The tool refuses any existing
destination and writes `manifest.json` marked `SYNTHETIC_NOT_BINANCE_DATA`.

The generator and its tests do **not** run H01, verify Binance market archives,
or demonstrate that hostile ZIP/CSV files are safe. No orders or network calls.
