from __future__ import annotations

from collections import deque
from typing import Iterable


def simple_moving_average(values: Iterable[float], window: int) -> float:
    values_list = list(values)
    if len(values_list) < window:
        raise ValueError("Not enough values for SMA")
    return sum(values_list[-window:]) / window


def relative_strength_index(values: Iterable[float], window: int) -> float:
    values_list = list(values)
    if len(values_list) < window + 1:
        raise ValueError("Not enough values for RSI")

    gains = deque(maxlen=window)
    losses = deque(maxlen=window)
    for idx in range(-window, 0):
        delta = values_list[idx] - values_list[idx - 1]
        if delta >= 0:
            gains.append(delta)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(delta))
    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))
