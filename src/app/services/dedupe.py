from __future__ import annotations

from app.services.parser import ParsedListing, fallback_hash


def dedupe_key(item: ParsedListing) -> str:
    if item.site_listing_id:
        return f"id:{item.site_listing_id}"
    if item.canonical_url:
        return f"url:{item.canonical_url}"
    return f"hash:{fallback_hash(item.title, item.canonical_url)}"
