from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskConfig:
    max_position_pct: float
    min_order_size: float


def calculate_position_size(available_funds: float, price: float, config: RiskConfig) -> float:
    target_value = available_funds * config.max_position_pct
    size = target_value / price
    if size < config.min_order_size:
        return 0.0
    return size
