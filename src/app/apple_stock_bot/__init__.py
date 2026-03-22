"""Apple stock monitoring helpers.

This package intentionally supports stock monitoring, notification, and opening
product pages for manual checkout only. It does not automate account login,
payment entry, or order submission.
"""

from .config import StockBotConfig
from .monitor import StockMonitor, StockStatus
from .notifier import DiscordWebhookNotifier, build_discord_payload

__all__ = [
    "DiscordWebhookNotifier",
    "StockBotConfig",
    "StockMonitor",
    "StockStatus",
    "build_discord_payload",
]
