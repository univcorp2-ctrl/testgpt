from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str
    api_secret: str
    pair: str
    timeframe: str
    base_url: str
    max_position_pct: float
    min_order_size: float
    fee_rate: float
    dry_run: bool


def load_settings() -> Settings:
    return Settings(
        api_key=os.getenv("BITBANK_API_KEY", ""),
        api_secret=os.getenv("BITBANK_API_SECRET", ""),
        pair=os.getenv("BITBANK_PAIR", "btc_jpy"),
        timeframe=os.getenv("BITBANK_TIMEFRAME", "15min"),
        base_url=os.getenv("BITBANK_BASE_URL", "https://api.bitbank.cc/v1"),
        max_position_pct=float(os.getenv("MAX_POSITION_PCT", "0.2")),
        min_order_size=float(os.getenv("MIN_ORDER_SIZE", "0.0001")),
        fee_rate=float(os.getenv("FEE_RATE", "0.0012")),
        dry_run=os.getenv("DRY_RUN", "true").lower() == "true",
    )
