from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .models import Candle
from .strategy import MovingAverageRsiStrategy


@dataclass
class BacktestResult:
    final_equity: float
    trades: int
    win_rate: float


def parse_candles(rows: Iterable[list[str]]) -> list[Candle]:
    candles = []
    for row in rows:
        timestamp = datetime.fromtimestamp(int(row[5]) / 1000)
        candles.append(
            Candle(
                timestamp=timestamp,
                open=float(row[0]),
                high=float(row[1]),
                low=float(row[2]),
                close=float(row[3]),
                volume=float(row[4]),
            )
        )
    return candles


def run_backtest(candles: list[Candle], starting_cash: float = 1_000_000) -> BacktestResult:
    strategy = MovingAverageRsiStrategy()
    cash = starting_cash
    position = 0.0
    entry_price = 0.0
    wins = 0
    trades = 0

    closes = []
    for candle in candles:
        closes.append(candle.close)
        signal = strategy.evaluate(closes)
        if signal.side == "buy" and position == 0:
            position = cash / candle.close
            entry_price = candle.close
            cash = 0.0
            trades += 1
        elif signal.side == "sell" and position > 0:
            cash = position * candle.close
            if candle.close > entry_price:
                wins += 1
            position = 0.0

    final_equity = cash + position * candles[-1].close
    win_rate = (wins / trades) if trades else 0.0
    return BacktestResult(final_equity=final_equity, trades=trades, win_rate=win_rate)
