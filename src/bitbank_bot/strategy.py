from __future__ import annotations

from dataclasses import dataclass

from .indicators import relative_strength_index, simple_moving_average
from .models import Signal


@dataclass
class StrategyConfig:
    fast_window: int = 10
    slow_window: int = 30
    rsi_window: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0


class MovingAverageRsiStrategy:
    def __init__(self, config: StrategyConfig | None = None) -> None:
        self.config = config or StrategyConfig()

    def evaluate(self, closes: list[float]) -> Signal:
        if len(closes) < self.config.slow_window + 1:
            return Signal(side="hold", reason="Not enough data")

        fast = simple_moving_average(closes, self.config.fast_window)
        slow = simple_moving_average(closes, self.config.slow_window)
        rsi = relative_strength_index(closes, self.config.rsi_window)

        if fast > slow and rsi < self.config.rsi_oversold:
            return Signal(side="buy", reason="MA uptrend with oversold RSI")
        if fast < slow and rsi > self.config.rsi_overbought:
            return Signal(side="sell", reason="MA downtrend with overbought RSI")
        return Signal(side="hold", reason="No edge")
