from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict

from optimizer import run_optimization


class OptimizerHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, body: str, status: int = 200, content_type: str = "text/html") -> None:
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/index.html"}:
            html = Path("index.html").read_text(encoding="utf-8")
            self._send_text(html)
            return
        self.send_error(404, "Not Found")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/optimize":
            self.send_error(404, "Not Found")
            return
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            self._send_json({"error": f"Invalid JSON: {exc}"}, status=400)
            return
        try:
            result = run_optimization(payload)
        except (KeyError, TypeError, ValueError) as exc:
            self._send_json({"error": str(exc)}, status=400)
            return
        self._send_json(result)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = HTTPServer((host, port), OptimizerHandler)
    print(f"Serving optimizer UI on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
