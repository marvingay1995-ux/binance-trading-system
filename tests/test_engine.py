import unittest
from urllib.parse import urlsplit,parse_qs
from btc_engine.market import Candle, validate, fetch_klines, STEPS
from btc_engine.backtest import backtest, Config

STEP = STEPS["1h"]
def sample(n=90):
    return [Candle(i*STEP,100+i*.2,101+i*.2,99+i*.2,100+i*.2,5) for i in range(n)]

class MarketTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(len(validate(sample(),"1h")),90)
    def test_gap(self):
        a=sample(); a.pop(5)
        with self.assertRaises(ValueError): validate(a,"1h")
    def test_duplicate(self):
        a=sample(); a.insert(5,a[4])
        with self.assertRaises(ValueError): validate(a,"1h")
    def test_invalid_price(self):
        a=sample(); a[2]=Candle(2*STEP,-1,100,1,5,2)
        with self.assertRaises(ValueError): validate(a,"1h")
    def test_nan(self):
        a=sample(); a[2]=Candle(2*STEP,100,101,99,float("nan"),2)
        with self.assertRaises(ValueError): validate(a,"1h")
    def test_pagination(self):
        calls=[]
        def transport(url):
            t=int(parse_qs(urlsplit(url).query)["startTime"][0]); calls.append(t)
            return [[i,100,101,99,100,1] for i in range(t,min(t+2*STEP,5*STEP),STEP)]
        a=fetch_klines("BTCUSDT","1h",0,5*STEP,transport)
        self.assertEqual((len(a),len(calls)),(5,3))
    def test_empty_page(self):
        with self.assertRaises(ValueError): fetch_klines("BTCUSDT","1h",0,STEP,lambda _:[])
    def test_future(self):
        with self.assertRaises(ValueError): fetch_klines("BTCUSDT","1h",0,999999999999999,lambda _:[])
    def test_symbol(self):
        with self.assertRaises(ValueError): fetch_klines("ETHUSDT","1h",0,STEP,lambda _:[])

class BacktestTests(unittest.TestCase):
    def test_determinism(self): self.assertEqual(backtest(sample(),"1h"),backtest(sample(),"1h"))
    def test_no_trades_monotonic(self):
        r=backtest(sample(),"1h")
        self.assertEqual((r["closed_trades"],r["ending_usdt"]),(0,100))
    def test_exposure(self):
        with self.assertRaises(ValueError): backtest(sample(),"1h",Config(max_exposure=.31))
    def test_daily_loss(self):
        with self.assertRaises(ValueError): backtest(sample(),"1h",Config(daily_loss_limit=.03))
    def test_short(self):
        with self.assertRaises(ValueError): backtest(sample(10),"1h")
    def test_no_future_signal(self):
        a=sample(); b=list(a); b[-1]=Candle(a[-1].time,1000,1001,999,1000,5)
        self.assertEqual(backtest(a,"1h")["events"],backtest(b,"1h")["events"])

if __name__ == "__main__": unittest.main()
