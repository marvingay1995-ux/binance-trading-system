import io
import unittest
import zipfile
from datetime import datetime, timezone
from btc_engine.archive import (normalize_timestamp, parse_monthly_zip,
                                fetch_completed_months, monthly_url)


def archive(interval, year, month, times):
    name = f"BTCUSDT-{interval}-{year:04d}-{month:02d}.csv"
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as z:
        lines = []
        for t in times:
            value = t * 1000 if year >= 2025 else t
            lines.append(f"{value},100,101,99,100,1,0,0,0,0,0,0")
        z.writestr(name, "\n".join(lines))
    return stream.getvalue()


class ArchiveTests(unittest.TestCase):
    def test_millisecond_timestamp(self):
        self.assertEqual(normalize_timestamp("1704067200000"), 1704067200000)

    def test_microsecond_timestamp(self):
        self.assertEqual(normalize_timestamp("1735689600000000"), 1735689600000)

    def test_microsecond_precision_rejected(self):
        with self.assertRaises(ValueError):
            normalize_timestamp("1735689600000001")

    def test_known_month(self):
        t = 1735689600000
        a = parse_monthly_zip(archive("1h", 2025, 1, [t, t + 3600000]), "1h", 2025, 1)
        self.assertEqual(len(a), 2)

    def test_wrong_month(self):
        t = 1735689600000
        with self.assertRaises(ValueError):
            parse_monthly_zip(archive("1h", 2025, 2, [t]), "1h", 2025, 2)

    def test_gap(self):
        t = 1735689600000
        with self.assertRaises(ValueError):
            parse_monthly_zip(archive("1h", 2025, 1, [t, t + 7200000]), "1h", 2025, 1)

    def test_zip_contents_rejected(self):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as z:
            z.writestr("../bad.csv", "garbage")
        with self.assertRaises(ValueError):
            parse_monthly_zip(stream.getvalue(), "1h", 2025, 1)

    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            monthly_url("1m", 2025, 1)

    def test_missing_month_rejected(self):
        now = datetime(2025, 4, 15, tzinfo=timezone.utc)
        def fake(url):
            # Supply one candle per month; continuity must be rejected.
            date = url.rsplit("-", 2)
            month = int(url[-6:-4])
            year = int(url[-11:-7])
            t = int(datetime(year, month, 1, tzinfo=timezone.utc).timestamp() * 1000)
            return archive("1h", year, month, [t])
        with self.assertRaises(ValueError):
            fetch_completed_months("1h", 3, now=now, transport=fake)


if __name__ == "__main__":
    unittest.main()
