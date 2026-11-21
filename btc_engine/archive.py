"""Research-only ingestion of official Binance Vision monthly Spot BTCUSDT kline ZIPs.

No account access, API credentials, proxies, or trading endpoints.
"""
import csv
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from .market import Candle, STEPS, validate

ARCHIVE_HOST = "https://data.binance.vision"
MAX_ZIP_BYTES = 12_000_000
MAX_CSV_BYTES = 45_000_000
MAX_ROWS = 31 * 24 + 2
HEADER_TOKENS = ("open_time", "open time")


def monthly_url(interval, year, month):
    if interval not in STEPS or not (2017 <= year <= 2100 and 1 <= month <= 12):
        raise ValueError("invalid interval or archive month")
    filename = f"BTCUSDT-{interval}-{year:04d}-{month:02d}.zip"
    return f"{ARCHIVE_HOST}/data/spot/monthly/klines/BTCUSDT/{interval}/{filename}"


def normalize_timestamp(value):
    """Explicit ms before 2025, microseconds from 2025 for Spot Vision."""
    raw = str(value).strip()
    if not re.fullmatch(r"[0-9]+", raw):
        raise ValueError("non-integer timestamp")
    value = int(raw)
    if value >= 10**15:
        if value % 1000:
            raise ValueError("non-millisecond microsecond timestamp")
        return value // 1000
    if value >= 10**12:
        return value
    raise ValueError("unexpected timestamp unit")


def parse_monthly_zip(payload, interval, year, month):
    if not isinstance(payload, bytes) or not 0 < len(payload) <= MAX_ZIP_BYTES:
        raise ValueError("missing or oversized archive")
    filename = f"BTCUSDT-{interval}-{year:04d}-{month:02d}.csv"
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            names = archive.namelist()
            if names != [filename]:
                raise ValueError("unexpected ZIP contents")
            info = archive.getinfo(filename)
            if info.file_size > MAX_CSV_BYTES:
                raise ValueError("oversized CSV")
            raw = archive.read(info)
    except (zipfile.BadZipFile, RuntimeError) as exc:
        raise ValueError("invalid ZIP archive") from exc
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("invalid CSV encoding") from exc
    rows = list(csv.reader(io.StringIO(text)))
    if rows and rows[0] and rows[0][0].strip().lower() in HEADER_TOKENS:
        rows.pop(0)
    if not 1 <= len(rows) <= MAX_ROWS:
        raise ValueError("empty or oversized CSV")
    candles = []
    for row in rows:
        if len(row) < 6:
            raise ValueError("incomplete candle row")
        t = normalize_timestamp(row[0])
        dt = datetime.fromtimestamp(t / 1000, timezone.utc)
        if dt.year != year or dt.month != month:
            raise ValueError("unexpected month in archive")
        candles.append(Candle(t, *(float(row[i]) for i in range(1, 6))))
    return validate(candles, interval)


def fetch_archive_month(interval, year, month, transport=None):
    url = monthly_url(interval, year, month)
    def default_transport(url):
        request = urllib.request.Request(url, headers={"User-Agent": "BTC-011-research/1.0"})
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = response.read(MAX_ZIP_BYTES + 1)
        return payload
    payload = (transport or default_transport)(url)
    candles = parse_monthly_zip(payload, interval, year, month)
    return candles, {"url": url, "zip_sha256": hashlib.sha256(payload).hexdigest(),
                     "rows": len(candles), "first_ms": candles[0].time, "last_ms": candles[-1].time}


def previous_month(year, month):
    return (year - 1, 12) if month == 1 else (year, month - 1)


def fetch_completed_months(interval, count=12, now=None, transport=None):
    if interval not in STEPS or not 3 <= count <= 24:
        raise ValueError("invalid interval or count")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("naive UTC time")
    year, month = previous_month(now.year, now.month)
    months = []
    for _ in range(count):
        months.append((year, month))
        year, month = previous_month(year, month)
    months.reverse()
    all_candles, manifest = [], []
    for y, m in months:
        candles, info = fetch_archive_month(interval, y, m, transport)
        all_candles.extend(candles)
        manifest.append(info)
    validate(all_candles, interval)
    # Reject incomplete calendar months and missing archive boundaries.
    start = int(datetime(months[0][0], months[0][1], 1, tzinfo=timezone.utc).timestamp() * 1000)
    end = int(datetime(now.year, now.month, 1, tzinfo=timezone.utc).timestamp() * 1000)
    validate(all_candles, interval, start=start, end=end)
    return all_candles, manifest
