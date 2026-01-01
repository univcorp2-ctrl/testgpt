from __future__ import annotations

import time
from dataclasses import dataclass

from .client import BitbankClient
from .models import Position, Signal
from .risk import RiskConfig, calculate_position_size
from .strategy import MovingAverageRsiStrategy


@dataclass
class TraderState:
    position: Position | None = None


class Trader:
    def __init__(
        self,
        client: BitbankClient,
        strategy: MovingAverageRsiStrategy,
        risk_config: RiskConfig,
        pair: str,
        timeframe: str,
        fee_rate: float,
        dry_run: bool = True,
    ) -> None:
        self.client = client
        self.strategy = strategy
        self.risk_config = risk_config
        self.pair = pair
        self.timeframe = timeframe
        self.fee_rate = fee_rate
        self.dry_run = dry_run
        self.state = TraderState()

    def _get_latest_closes(self, date: str) -> list[float]:
        candles = self.client.fetch_candles(self.pair, self.timeframe, date)
        candle_data = candles["data"]["candlestick"][0]["ohlcv"]
        return [float(item[3]) for item in candle_data]

    def _get_available_funds(self) -> float:
        assets = self.client.fetch_assets()
        for asset in assets["data"]["assets"]:
            if asset["asset"] == "jpy":
                return float(asset["free_amount"])
        return 0.0

    def _place_order(self, side: str, size: float) -> dict[str, str] | None:
        if self.dry_run:
            return {"status": "dry_run", "side": side, "size": size}
        payload = {
            "pair": self.pair,
            "amount": f"{size:.8f}",
            "side": side,
            "type": "market",
        }
        return self.client.create_order(payload)

    def _handle_signal(self, signal: Signal, price: float) -> dict[str, str] | None:
        if signal.side == "buy" and self.state.position is None:
            funds = self._get_available_funds()
            size = calculate_position_size(funds, price, self.risk_config)
            if size == 0:
                return {"status": "skip", "reason": "order size below min"}
            result = self._place_order("buy", size)
            if result is not None:
                self.state.position = Position(side="long", size=size, entry_price=price)
            return result
        if signal.side == "sell" and self.state.position is not None:
            size = self.state.position.size
            result = self._place_order("sell", size)
            if result is not None:
                self.state.position = None
            return result
        return None

    def run(self, poll_seconds: int = 60 * 15) -> None:
        while True:
            date = time.strftime("%Y%m%d")
            closes = self._get_latest_closes(date)
            signal = self.strategy.evaluate(closes)
            price = closes[-1]
            self._handle_signal(signal, price)
            time.sleep(poll_seconds)
