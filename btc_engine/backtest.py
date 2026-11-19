"""Research-only SMA cross baseline; signal on completed bar, fill next open."""
from dataclasses import dataclass
from math import floor
from .market import validate

@dataclass(frozen=True)
class Config:
    starting_usdt: float = 100.0
    max_exposure: float = 0.30
    daily_loss_limit: float = 0.02
    fee_rate: float = 0.001
    slippage_rate: float = 0.0005
    spread_rate: float = 0.0002
    step_size: float = 0.00001
    min_qty: float = 0.00001
    min_notional: float = 5.0
    fast: int = 5
    slow: int = 20

def backtest(candles, interval, config=Config()):
    validate(candles, interval)
    c = config
    if not (0 < c.max_exposure <= .30 and 0 < c.daily_loss_limit <= .02 and c.starting_usdt > 0
            and 1 < c.fast < c.slow and c.step_size > 0 and c.min_qty > 0 and c.min_notional > 0
            and 0 <= c.fee_rate < 1 and 0 <= c.slippage_rate < 1 and 0 <= c.spread_rate < 1):
        raise ValueError("invalid risk configuration")
    if len(candles) <= c.slow + 1:
        raise ValueError("insufficient history")
    cash, qty, basis = c.starting_usdt, 0., 0.
    fees, turnover, trades, wins, profit, loss = 0., 0., 0, 0, 0., 0.
    peak, max_dd, curve, events = cash, 0., [], []
    day, day_start, halted = None, cash, False
    closes = [x.close for x in candles]
    def sma(end, n):
        return sum(closes[end-n:end])/n
    for i, bar in enumerate(candles):
        today = bar.time // 86400000
        if today != day:
            day, day_start, halted = today, cash+qty*bar.open, False
        if cash+qty*bar.open <= day_start*(1-c.daily_loss_limit):
            halted = True
        signal = None
        if i >= c.slow+2:
            # i is the execution bar. Both cross observations end
            # strictly before its open: previous close at i-1.
            pf, ps = sma(i-2,c.fast), sma(i-2,c.slow)
            lf, ls = sma(i-1,c.fast), sma(i-1,c.slow)
            if pf <= ps and lf > ls: signal = "buy"
            if pf >= ps and lf < ls: signal = "sell"
        if qty and (halted or signal == "sell"):
            price = bar.open*(1-c.slippage_rate-c.spread_rate/2)
            proceeds = qty*price
            fee = proceeds*c.fee_rate
            pnl = proceeds-fee-basis
            profit += max(pnl,0)
            loss += max(-pnl,0)
            cash += proceeds-fee
            fees += fee
            turnover += proceeds
            trades += 1
            wins += int(pnl>0)
            events.append({"time":bar.time,"side":"sell","qty":qty,"price":price,"pnl":pnl})
            qty, basis = 0., 0.
        if signal == "buy" and not halted and not qty:
            price = bar.open*(1+c.slippage_rate+c.spread_rate/2)
            budget = min(cash/(1+c.fee_rate),cash*c.max_exposure/(1+c.fee_rate))
            amount = floor((budget/price+1e-12)/c.step_size)*c.step_size
            notional = amount*price
            if amount >= c.min_qty and notional >= c.min_notional:
                fee = notional*c.fee_rate
                cash -= notional+fee
                qty, basis = amount, notional+fee
                fees += fee
                turnover += notional
                events.append({"time":bar.time,"side":"buy","qty":qty,"price":price})
        equity = cash+qty*bar.close
        peak = max(peak,equity)
        max_dd = max(max_dd,1-equity/peak)
        curve.append({"time":bar.time,"equity":equity})
    end = curve[-1]["equity"]
    return {"starting_usdt":c.starting_usdt,"ending_usdt":end,"net_pnl_usdt":end-c.starting_usdt,
            "return_pct":100*(end/c.starting_usdt-1),"max_drawdown_pct":100*max_dd,
            "closed_trades":trades,"win_rate_pct":100*wins/trades if trades else None,
            "profit_factor":profit/loss if loss else (float("inf") if profit else None),
            "fees_usdt":fees,"turnover_usdt":turnover,
            "buy_hold_upper_bound_usdt":c.starting_usdt*candles[-1].close/candles[0].open,
            "no_trade_usdt":c.starting_usdt,"open_qty":qty,"events":events,"equity_curve":curve}
