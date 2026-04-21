from __future__ import annotations

import webbrowser


def open_product_page(url: str) -> bool:
    """Open the Apple product page for a human to complete checkout manually."""

    return webbrowser.open(url)
