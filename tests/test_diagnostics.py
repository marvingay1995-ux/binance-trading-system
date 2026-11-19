import unittest
from btc_engine.market import Candle,STEPS
from btc_engine.diagnostics import trade_ledger,summarize_trades,drawdown_audit,diagnose

STEP=STEPS["1h"]
def candles(n=320):
    arr=[]
    for i in range(n):
        value=100+((i%40)-20)*0.65
        arr.append(Candle(i*STEP,value,value+2,value-2,value,10))
    return arr

class DiagnosticsTests(unittest.TestCase):
    def test_trade_pairing(self):
        ledger,open_entry=trade_ledger([{"side":"buy","time":1,"qty":.1,"price":100},
             {"side":"sell","time":2,"qty":.1,"price":110,"pnl":.8}])
        self.assertEqual((len(ledger),open_entry),(1,None))
        self.assertEqual(ledger[0]["net_pnl_usdt"],.8)

    def test_unmatched_exit_rejected(self):
        with self.assertRaises(ValueError):
            trade_ledger([{"side":"sell","time":1,"qty":.1,"price":99,"pnl":-1}])

    def test_partial_fill_rejected(self):
        with self.assertRaises(ValueError):
            trade_ledger([{"side":"buy","time":1,"qty":.1,"price":100},
                          {"side":"sell","time":2,"qty":.05,"price":99,"pnl":-.2}])

    def test_win_rate(self):
        result=summarize_trades([{"net_pnl_usdt":2},{"net_pnl_usdt":-1}])
        self.assertEqual((result["win_rate_pct"],result["profit_factor"]),(50.,2.))

    def test_no_trades_has_null(self):
        self.assertIsNone(summarize_trades([])["profit_factor"])

    def test_daily_risk_breach_flagged(self):
        curve=[{"time":0,"equity":100},{"time":STEP,"equity":97}]
        self.assertEqual(drawdown_audit(curve,100)["observed_daily_loss_breach_bars"],1)

    def test_sensitivity_deterministic(self):
        self.assertEqual(diagnose(candles(),"1h"),diagnose(candles(),"1h"))

    def test_fee_stress_not_better_in_sample(self):
        result=diagnose(candles(),"1h")["cost_sensitivity"]
        self.assertLessEqual(result["double_fees"]["full_net_pnl_usdt"],
                             result["baseline"]["full_net_pnl_usdt"]+1e-8)

    def test_unverified_filters(self):
        self.assertFalse(diagnose(candles(),"1h")["sizing"]["exchange_filters_verified"])

    def test_bad_history_rejected(self):
        a=candles();a.pop(10)
        with self.assertRaises(ValueError): diagnose(a,"1h")

if __name__=="__main__":
    unittest.main()
