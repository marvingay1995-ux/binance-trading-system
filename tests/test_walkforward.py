import unittest

from btc_engine.market import Candle, STEPS
from btc_engine.walkforward import walkforward, fold_boundaries


def sample(n=420):
    step = STEPS["4h"]
    return [Candle(i*step, 100+(i%35)*.1, 102+(i%35)*.1,
                   99+(i%35)*.1, 100+(i%35)*.1, 2) for i in range(n)]


class WalkForwardTests(unittest.TestCase):
    def test_six_nonoverlapping_windows(self):
        folds = fold_boundaries(420)
        self.assertEqual(len(folds), 6)
        self.assertEqual(folds[0][0], 168)
        self.assertEqual(folds[-1][1], 420)
        self.assertTrue(all(b == c for (_, b), (c, _) in zip(folds, folds[1:])))

    def test_all_scenarios(self):
        result = walkforward(sample(), "4h")
        self.assertEqual(set(result["scenarios"]), {"baseline", "double_costs", "triple_costs"})
        self.assertEqual(result["decision"], "NO_GO_PAPER_AND_LIVE")
        self.assertFalse(result["parameter_optimization"])

    def test_deterministic(self):
        self.assertEqual(walkforward(sample(), "4h"), walkforward(sample(), "4h"))

    def test_same_candle_splits(self):
        result = walkforward(sample(), "4h")
        a = [w["start_ms"] for w in result["scenarios"]["baseline"]["windows"]]
        b = [w["start_ms"] for w in result["scenarios"]["triple_costs"]["windows"]]
        self.assertEqual(a, b)

    def test_gapped_data_rejected(self):
        x = sample()
        x.pop(9)
        with self.assertRaises(ValueError):
            walkforward(x, "4h")

    def test_insufficient_candles(self):
        with self.assertRaises(ValueError):
            walkforward(sample(299), "4h")


if __name__ == "__main__":
    unittest.main()
