import unittest
from btc_engine.market import Candle,STEPS
from btc_engine.evaluate import evaluate
STEP=STEPS["1h"]
def sample(n):
    return [Candle(i*STEP,100+i*.1,101+i*.1,99+i*.1,100+i*.1,1) for i in range(n)]
class EvaluationTests(unittest.TestCase):
    def test_split(self):
        r=evaluate(sample(500),"1h")
        self.assertEqual([r[x]["candles"] for x in ("train","validation","holdout")],[300,100,100])
        self.assertEqual(r["status"],"RESEARCH_ONLY_NOT_PROFIT_VERIFIED")
    def test_deterministic(self):
        self.assertEqual(evaluate(sample(500),"1h"),evaluate(sample(500),"1h"))
    def test_too_short(self):
        with self.assertRaises(ValueError):evaluate(sample(200),"1h")
    def test_gap_rejected(self):
        a=sample(500);a.pop(100)
        with self.assertRaises(ValueError):evaluate(a,"1h")
if __name__=="__main__":unittest.main()
