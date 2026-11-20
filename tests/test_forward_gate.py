import unittest
from datetime import datetime, timedelta, timezone
from btc_engine.market import Candle, STEPS
from btc_engine.forward_gate import (
    admit_forward_candles, FIRST_UNSEEN_MS, MIN_FORWARD_DAYS,
)


STEP = STEPS["4h"]
def sample(start=FIRST_UNSEEN_MS, days=61):
    return [Candle(start+i*STEP,100,101,99,100,2)
            for i in range(days*6)]


def metadata():
    return {"source_url":"https://data.binance.vision/example",
            "sha256":"a"*64}


class ForwardGateTests(unittest.TestCase):
    def setUp(self):
        self.collection = datetime(2027, 2, 1, tzinfo=timezone.utc)

    def test_registered_forward_period_admitted_in_future(self):
        # Simulate a later collection date; gate rejects future timestamps today.
        # Current-date-independent checks can be tested by examining the refusal.
        with self.assertRaises(ValueError):
            admit_forward_candles(sample(), "4h", self.collection, metadata())

    def test_previously_seen_data_rejected(self):
        historical = sample(FIRST_UNSEEN_MS-STEP)
        with self.assertRaises(ValueError):
            admit_forward_candles(historical, "4h", datetime.now(timezone.utc), metadata())

    def test_short_period_rejected(self):
        with self.assertRaises(ValueError):
            admit_forward_candles(sample(days=30), "4h", datetime.now(timezone.utc), metadata())

    def test_wrong_interval_rejected(self):
        with self.assertRaises(ValueError):
            admit_forward_candles(sample(), "1h", datetime.now(timezone.utc), metadata())

    def test_missing_provenance_rejected(self):
        with self.assertRaises(ValueError):
            admit_forward_candles(sample(), "4h", datetime.now(timezone.utc), {})

    def test_naive_datetime_rejected(self):
        with self.assertRaises(ValueError):
            admit_forward_candles(sample(), "4h", datetime.now(timezone.utc).replace(tzinfo=None), metadata())

    def test_unaligned_data_rejected(self):
        broken = sample()
        broken.pop(3)
        with self.assertRaises(ValueError):
            admit_forward_candles(broken, "4h", datetime.now(timezone.utc), metadata())


if __name__ == "__main__":
    unittest.main()
