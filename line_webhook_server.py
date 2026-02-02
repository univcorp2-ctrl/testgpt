from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Iterable, List

from line_storage import StoredMessage, store_messages


TEXT_MESSAGE_TYPE = "text"
CALLBACK_PATH = "/callback"


@dataclass(frozen=True)
class LineWebhookConfig:
    channel_secret: str | None
    db_path: Path


def load_config() -> LineWebhookConfig:
    return LineWebhookConfig(
        channel_secret=os.getenv("LINE_CHANNEL_SECRET"),
        db_path=Path(os.getenv("LINE_DB_PATH", "line_messages.sqlite3")),
    )


def verify_signature(channel_secret: str, body: bytes, signature: str) -> bool:
    digest = hmac.new(channel_secret.encode("utf-8"), body, hashlib.sha256).digest()
    computed = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(computed, signature)


def extract_links(text: str) -> List[str]:
    pattern = re.compile(r"https?://[^\s<>]+|line://[^\s<>]+")
    return pattern.findall(text)


def build_messages(payload: Dict[str, Any]) -> Iterable[StoredMessage]:
    for event in payload.get("events", []):
        message = event.get("message")
        if not message or message.get("type") != TEXT_MESSAGE_TYPE:
            continue
        source = event.get("source", {})
        source_type = source.get("type", "unknown")
        source_id = source.get("groupId") or source.get("roomId") or source.get("userId") or "unknown"
        text = message.get("text", "")
        yield StoredMessage(
            source_type=source_type,
            source_id=source_id,
            message_id=message.get("id", ""),
            text=text,
            links=extract_links(text),
            timestamp_ms=int(event.get("timestamp", 0)),
            raw_event=event,
        )


class LineWebhookHandler(BaseHTTPRequestHandler):
    config = load_config()

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != CALLBACK_PATH:
            self.send_error(404, "Not Found")
            return
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        signature = self.headers.get("X-Line-Signature")
        if self.config.channel_secret:
            if not signature:
                self._send_json({"error": "Missing X-Line-Signature"}, status=400)
                return
            if not verify_signature(self.config.channel_secret, body, signature):
                self._send_json({"error": "Invalid signature"}, status=400)
                return
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            self._send_json({"error": f"Invalid JSON: {exc}"}, status=400)
            return
        messages = list(build_messages(payload))
        stored = store_messages(self.config.db_path, messages)
        warning = None
        if not self.config.channel_secret:
            warning = "LINE_CHANNEL_SECRET is not set; signature verification skipped."
        self._send_json({"stored": stored, "warning": warning})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def run_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    server = HTTPServer((host, port), LineWebhookHandler)
    print(f"LINE webhook server listening on http://{host}:{port}{CALLBACK_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
