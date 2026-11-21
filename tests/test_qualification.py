import unittest
from btc_engine.market import Candle, STEPS
from btc_engine.qualification import parse_spot_filters, check_order_size, stress_qualification

def mock_snapshot():
    return {"symbols":[{"symbol":"BTCUSDT","status":"TRADING",
        "isSpotTradingAllowed":True,"filters":[
        {"filterType":"PRICE_FILTER","tickSize":"0.01"},
        {"filterType":"LOT_SIZE","minQty":"0.00001","stepSize":"0.00001"},
        {"filterType":"NOTIONAL","minNotional":"5.0","applyMinToMarket":True}]}]}

def sample(n=340):
    step=STEPS["4h"]
    out=[]
    for i in range(n):
        value=100+(i%40-20)*.5
        out.append(Candle(i*step,value,value+2,value-2,value,5))
    return out

class QualificationTests(unittest.TestCase):
    def test_filter_parsing(self):
        f=parse_spot_filters(mock_snapshot())
        self.assertEqual(f["step_size"],"0.00001")
        self.assertEqual(f["source_status"],"UNVERIFIED_SNAPSHOT")

    def test_disabled_spot_rejected(self):
        x=mock_snapshot()
        x["symbols"][0]["isSpotTradingAllowed"]=False
        with self.assertRaises(ValueError):parse_spot_filters(x)

    def test_missing_notional_rejected(self):
        x=mock_snapshot()
        x["symbols"][0]["filters"].pop()
        with self.assertRaises(ValueError):parse_spot_filters(x)

    def test_malformed_step_rejected(self):
        x=mock_snapshot()
        x["symbols"][0]["filters"][1]["stepSize"]="NaN"
        with self.assertRaises(ValueError):parse_spot_filters(x)

    def test_size_pass(self):
        f=parse_spot_filters(mock_snapshot())
        self.assertTrue(check_order_size("100000","0.0001",f,"30")["hypothetical_accepted"])

    def test_size_fails_step_and_notional(self):
        f=parse_spot_filters(mock_snapshot())
        r=check_order_size("100000","0.000011",f,"30")
        self.assertIn("STEP_SIZE",r["reasons"])
        self.assertIn("MIN_NOTIONAL",r["reasons"])

    def test_size_fails_budget(self):
        f=parse_spot_filters(mock_snapshot())
        self.assertIn("BUDGET",check_order_size("100000","0.0003",f,"20")["reasons"])

    def test_no_go(self):
        r=stress_qualification(sample(),"4h")
        self.assertEqual(r["decision"],"NO_GO_LIVE_AND_PAPER")
        self.assertFalse(r["filter_snapshot_authenticated"])
        self.assertEqual(set(r["scenarios"]),{"baseline","2x_costs","3x_costs"})

    def test_determinism(self):
        self.assertEqual(stress_qualification(sample(),"4h"),stress_qualification(sample(),"4h"))

    def test_gap_fails(self):
        x=sample();x.pop(7)
        with self.assertRaises(ValueError):stress_qualification(x,"4h")

if __name__=="__main__":
    unittest.main()
