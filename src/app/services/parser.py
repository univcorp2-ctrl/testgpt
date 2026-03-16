from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass
class ParsedListing:
    site_listing_id: str | None
    canonical_url: str
    title: str | None
    price_yen: float | None
    gross_yield_pct: float | None


def parse_listing(raw_text: str, url: str) -> ParsedListing:
    sid = None
    if "listing_id=" in url:
        sid = url.split("listing_id=")[-1].split("&")[0]
    title = raw_text[:80].strip() if raw_text else None
    return ParsedListing(site_listing_id=sid, canonical_url=url, title=title, price_yen=None, gross_yield_pct=None)


def fallback_hash(title: str | None, url: str) -> str:
    return hashlib.sha256(f"{title or ''}|{url}".encode()).hexdigest()
