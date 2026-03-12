from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from app.config import AppSettings
from app.security import encrypt_to_file


def bootstrap_login(settings: AppSettings, encryption_key: str) -> Path:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(settings.login_url)
        page.wait_for_timeout(60000)
        state = context.storage_state()
        browser.close()
    payload = json.dumps(state, ensure_ascii=False).encode()
    encrypt_to_file(settings.session_state_path, payload, encryption_key)
    return settings.session_state_path
