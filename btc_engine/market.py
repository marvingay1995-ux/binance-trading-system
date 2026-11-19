"""Public Binance Spot OHLCV retrieval with fail-closed validation."""
import json, math, urllib.parse, urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

STEPS = {"1h": 3600000, "4h": 14400000}
ENDPOINT = "https://api.binance.com/api/v3/klines"

@dataclass(frozen=True)
class Candle:
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float

def validate(candles, interval, start=None, end=None):
    step = STEPS[interval]
    if not candles:
        raise ValueError("empty series")
    previous = None
    for c in candles:
        if c.time % step or (previous is not None and c.time != previous + step):
            raise ValueError("gap, duplicate, unordered or unaligned candle")
        values = (c.open, c.high, c.low, c.close, c.volume)
        if not all(math.isfinite(v) for v in values) or min(values[:4]) <= 0 or c.volume < 0:
            raise ValueError("invalid price or volume")
        if not (c.low <= min(c.open,c.close) <= max(c.open,c.close) <= c.high):
            raise ValueError("invalid OHLC")
        previous = c.time
    if start is not None and candles[0].time != start:
        raise ValueError("missing first candle")
    if end is not None and candles[-1].time + step != end:
        raise ValueError("missing final candle")
    return candles

def fetch_klines(symbol, interval, start_ms, end_ms, transport=None):
    if symbol != "BTCUSDT" or interval not in STEPS:
        raise ValueError("only BTCUSDT 1h/4h allowed")
    step = STEPS[interval]
    if start_ms < 0 or end_ms <= start_ms or start_ms % step or end_ms % step:
        raise ValueError("unaligned range")
    if end_ms > int(datetime.now(timezone.utc).timestamp()*1000) - step:
        raise ValueError("unfinished bar possible")
    def default_transport(url):
        with urllib.request.urlopen(url, timeout=15) as response:
            return json.load(response)
    transport = transport or default_transport
    cursor, output = start_ms, []
    while cursor < end_ms:
        q = urllib.parse.urlencode({"symbol":symbol,"interval":interval,"startTime":cursor,"endTime":end_ms-1,"limit":1000})
        rows = transport(ENDPOINT+"?"+q)
        if not isinstance(rows,list) or not rows:
            raise ValueError("missing API page")
        batch = []
        for row in rows:
            if not isinstance(row,list) or len(row) < 6:
                raise ValueError("malformed API row")
            t = int(row[0])
            if not cursor <= t < end_ms:
                raise ValueError("unexpected API timestamp")
            batch.append(Candle(t, *(float(row[j]) for j in range(1,6))))
        validate(batch,interval,start=cursor)
        output.extend(batch)
        cursor = batch[-1].time + step
    return validate(output,interval,start=start_ms,end=end_ms)
