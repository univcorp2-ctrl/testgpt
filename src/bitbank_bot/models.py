from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Signal:
    side: str  # "buy" or "sell" or "hold"
    reason: str


@dataclass
class Position:
    side: str
    size: float
    entry_price: float
