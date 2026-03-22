from __future__ import annotations

import os
from dataclasses import dataclass

MIN_CHECK_INTERVAL_SECONDS = 30


@dataclass(frozen=True)
class StockBotConfig:
    target_url: str = os.getenv("APPLE_TARGET_URL", "https://www.apple.com/jp/shop/buy-iphone/")
    check_interval_seconds: int = int(
        os.getenv("APPLE_CHECK_INTERVAL_SECONDS", str(MIN_CHECK_INTERVAL_SECONDS))
    )
    target_model: str = os.getenv("APPLE_TARGET_MODEL", "iPhone 17 Pro Max")
    target_storage: str = os.getenv("APPLE_TARGET_STORAGE", "256GB")
    target_color: str = os.getenv("APPLE_TARGET_COLOR", "ナチュラルチタニウム")
    product_code: str = os.getenv("APPLE_PRODUCT_CODE", "")
    notify_webhook: str = os.getenv("APPLE_NOTIFY_WEBHOOK", "")
    open_product_page_on_hit: bool = os.getenv("APPLE_OPEN_PRODUCT_PAGE_ON_HIT", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    mention: str | None = os.getenv("APPLE_NOTIFY_MENTION") or None

    def normalized_interval(self) -> int:
        return max(self.check_interval_seconds, MIN_CHECK_INTERVAL_SECONDS)

    def validate(self) -> None:
        if not self.product_code:
            raise ValueError("APPLE_PRODUCT_CODE must be set to the Apple product/SKU code to monitor")
