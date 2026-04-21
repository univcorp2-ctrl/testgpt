from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
from urllib import parse, request

from .config import StockBotConfig

LOGGER = logging.getLogger(__name__)
DEFAULT_TIMEOUT_SECONDS = 10


class StockStatus(str, Enum):
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    UNKNOWN = "unknown"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


@dataclass(frozen=True)
class StockCheckResult:
    status: StockStatus
    checked_at: datetime
    message: str
    product_url: str


def build_availability_url(product_code: str) -> str:
    query = parse.urlencode({"product": product_code})
    return f"https://www.apple.com/jp/shop/product/availability?{query}"


def parse_availability(payload: dict[str, Any]) -> StockStatus:
    serialized = json.dumps(payload, ensure_ascii=False).lower()
    if '"availability": "available"' in serialized or '"state": "available"' in serialized:
        return StockStatus.IN_STOCK
    if '"availability": "unavailable"' in serialized or '"state": "unavailable"' in serialized:
        return StockStatus.OUT_OF_STOCK
    return StockStatus.UNKNOWN


Fetcher = Callable[[str], dict[str, Any]]
Notifier = Callable[[str], Any]
Opener = Callable[[str], bool]


class StockMonitor:
    def __init__(self, config: StockBotConfig) -> None:
        self.config = config
        self._last_status: StockStatus | None = None

    def fetch_json(self, url: str) -> dict[str, Any]:
        req = request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 stock-monitor/1.0 (+manual-checkout-only)"},
            method="GET",
        )
        with request.urlopen(req, timeout=DEFAULT_TIMEOUT_SECONDS) as response:  # noqa: S310
            if response.status == 429:
                return {"status": 429}
            return json.loads(response.read().decode())

    def check_once(
        self,
        *,
        fetcher: Fetcher | None = None,
        notify: Notifier | None = None,
        opener: Opener | None = None,
    ) -> StockCheckResult:
        self.config.validate()
        fetch = fetcher or self.fetch_json
        product_url = self.config.target_url
        checked_at = datetime.now(timezone.utc)
        availability_url = build_availability_url(self.config.product_code)

        try:
            payload = fetch(availability_url)
        except Exception as exc:  # noqa: BLE001
            message = f"Apple stock check failed: {exc}"
            LOGGER.exception(message)
            if notify is not None:
                notify(message)
            result = StockCheckResult(StockStatus.ERROR, checked_at, message, product_url)
            self._last_status = result.status
            return result

        if payload.get("status") == 429:
            message = "Apple stock check was rate-limited (HTTP 429); backing off and keeping manual checkout only."
            if notify is not None and self._last_status != StockStatus.RATE_LIMITED:
                notify(message)
            result = StockCheckResult(StockStatus.RATE_LIMITED, checked_at, message, product_url)
            self._last_status = result.status
            return result

        status = parse_availability(payload)
        if status is StockStatus.IN_STOCK:
            message = (
                f"Stock detected for {self.config.target_model} / {self.config.target_storage} / "
                f"{self.config.target_color}. Open the Apple page and complete checkout manually."
            )
            if notify is not None and self._last_status != StockStatus.IN_STOCK:
                notify(message)
            if opener is not None and self.config.open_product_page_on_hit:
                opener(product_url)
        elif status is StockStatus.OUT_OF_STOCK:
            message = (
                f"Still unavailable for {self.config.target_model} / {self.config.target_storage} / "
                f"{self.config.target_color}."
            )
        else:
            message = "Availability response did not contain a recognizable stock state."
            if notify is not None and self._last_status != StockStatus.UNKNOWN:
                notify(message)

        result = StockCheckResult(status, checked_at, message, product_url)
        self._last_status = result.status
        return result
