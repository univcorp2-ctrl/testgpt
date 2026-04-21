from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib import request

DEFAULT_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class NotificationResult:
    delivered: bool
    status_code: int | None
    detail: str


def build_discord_payload(message: str, mention: str | None = None) -> dict[str, Any]:
    content = message if mention is None else f"{mention} {message}"
    return {"content": content}


class DiscordWebhookNotifier:
    def __init__(self, webhook_url: str, *, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> None:
        self.webhook_url = webhook_url
        self.timeout_seconds = timeout_seconds

    def send(self, message: str, *, mention: str | None = None) -> NotificationResult:
        if not self.webhook_url:
            return NotificationResult(False, None, "webhook URL is not configured")

        payload = json.dumps(build_discord_payload(message, mention=mention)).encode()
        req = request.Request(
            self.webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=self.timeout_seconds) as response:  # noqa: S310
            return NotificationResult(
                delivered=200 <= response.status < 300,
                status_code=response.status,
                detail="ok",
            )
