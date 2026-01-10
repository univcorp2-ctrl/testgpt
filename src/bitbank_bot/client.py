from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any

import requests


def _sign_message(secret: str, message: str) -> str:
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


@dataclass
class BitbankClient:
    api_key: str
    api_secret: str
    base_url: str = "https://api.bitbank.cc/v1"

    def _headers(self, path: str, body: str = "") -> dict[str, str]:
        nonce = str(int(time.time() * 1000))
        signature = _sign_message(self.api_secret, f"{nonce}{path}{body}")
        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-NONCE": nonce,
            "ACCESS-SIGNATURE": signature,
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        body = json.dumps(data) if data else ""
        headers = self._headers(path, body)
        response = requests.request(method, url, params=params, data=body, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def public_request(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def fetch_candles(self, pair: str, candle_type: str, date: str) -> dict[str, Any]:
        path = f"/candlestick/{pair}/{candle_type}/{date}"
        return self.public_request(path)

    def fetch_ticker(self, pair: str) -> dict[str, Any]:
        return self.public_request(f"/ticker/{pair}")

    def fetch_assets(self) -> dict[str, Any]:
        return self._request("GET", "/user/assets")

    def create_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/user/spot/order", data=payload)
