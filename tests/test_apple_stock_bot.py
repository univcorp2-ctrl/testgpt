from __future__ import annotations

from app.apple_stock_bot.config import MIN_CHECK_INTERVAL_SECONDS, StockBotConfig
from app.apple_stock_bot.monitor import StockMonitor, StockStatus, build_availability_url, parse_availability
from app.apple_stock_bot.notifier import build_discord_payload


def test_build_availability_url_encodes_product_code() -> None:
    assert build_availability_url("MLKQ3J/A") == "https://www.apple.com/jp/shop/product/availability?product=MLKQ3J%2FA"


def test_parse_availability_detects_in_stock() -> None:
    payload = {"stores": [{"partsAvailability": {"foo": {"availability": "available"}}}]}
    assert parse_availability(payload) is StockStatus.IN_STOCK


def test_parse_availability_detects_out_of_stock() -> None:
    payload = {"stores": [{"partsAvailability": {"foo": {"availability": "unavailable"}}}]}
    assert parse_availability(payload) is StockStatus.OUT_OF_STOCK


def test_config_enforces_minimum_interval() -> None:
    config = StockBotConfig(check_interval_seconds=5)
    assert config.normalized_interval() == MIN_CHECK_INTERVAL_SECONDS


def test_monitor_notifies_once_when_stock_appears() -> None:
    config = StockBotConfig(product_code="SKU123", target_model="iPhone 17 Pro Max")
    monitor = StockMonitor(config)
    notifications: list[str] = []
    opened: list[str] = []

    def fetcher(_url: str) -> dict[str, object]:
        return {"availability": "available"}

    result_one = monitor.check_once(
        fetcher=fetcher,
        notify=notifications.append,
        opener=lambda url: opened.append(url) or True,
    )
    result_two = monitor.check_once(
        fetcher=fetcher,
        notify=notifications.append,
        opener=lambda url: opened.append(url) or True,
    )

    assert result_one.status is StockStatus.IN_STOCK
    assert result_two.status is StockStatus.IN_STOCK
    assert len(notifications) == 1
    assert opened == []


def test_monitor_reports_rate_limit_once() -> None:
    config = StockBotConfig(product_code="SKU123")
    monitor = StockMonitor(config)
    notifications: list[str] = []

    result_one = monitor.check_once(fetcher=lambda _url: {"status": 429}, notify=notifications.append)
    result_two = monitor.check_once(fetcher=lambda _url: {"status": 429}, notify=notifications.append)

    assert result_one.status is StockStatus.RATE_LIMITED
    assert result_two.status is StockStatus.RATE_LIMITED
    assert len(notifications) == 1


def test_build_discord_payload_includes_optional_mention() -> None:
    payload = build_discord_payload("stock found", mention="@here")
    assert payload == {"content": "@here stock found"}
