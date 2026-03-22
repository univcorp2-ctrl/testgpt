from __future__ import annotations

import logging
import signal
import time

from .config import StockBotConfig
from .monitor import StockMonitor, StockStatus
from .notifier import DiscordWebhookNotifier
from .opener import open_product_page

LOGGER = logging.getLogger(__name__)


def run_forever() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    config = StockBotConfig()
    monitor = StockMonitor(config)
    notifier = DiscordWebhookNotifier(config.notify_webhook)
    should_stop = False

    def handle_signal(signum: int, _frame: object) -> None:
        nonlocal should_stop
        LOGGER.info("received signal %s, stopping stock monitor", signum)
        should_stop = True

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    interval = config.normalized_interval()
    LOGGER.info("starting Apple stock monitor with %s second interval", interval)
    while not should_stop:
        result = monitor.check_once(
            notify=lambda message: notifier.send(message, mention=config.mention),
            opener=open_product_page,
        )
        if result.status is StockStatus.IN_STOCK:
            LOGGER.warning(result.message)
        else:
            LOGGER.info(result.message)
        time.sleep(interval)


if __name__ == "__main__":
    run_forever()
