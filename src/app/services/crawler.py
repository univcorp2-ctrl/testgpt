from __future__ import annotations

import hashlib
import random
import time
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from app.config import AppSettings
from app.db.models import ListingCurrent, ListingRaw, ManualReviewQueue
from app.services.dedupe import dedupe_key
from app.services.history import detect_changes
from app.services.parser import parse_listing


class CrawlerService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def fetch(self, url: str) -> tuple[str, str | None, str | None]:
        retries = 4
        for i in range(retries):
            try:
                resp = httpx.get(url, timeout=20)
                if resp.status_code in {429, 403, 500, 502, 503, 504}:
                    raise httpx.HTTPStatusError("retryable", request=resp.request, response=resp)
                return resp.text, resp.headers.get("ETag"), resp.headers.get("Last-Modified")
            except Exception:
                if i == retries - 1:
                    raise
                time.sleep((2**i) + random.uniform(self.settings.min_wait_sec, self.settings.max_wait_sec))
        raise RuntimeError("unreachable")

    def run_urls(self, db: Session, urls: list[str]) -> None:
        seen: set[str] = set()
        for url in urls:
            time.sleep(random.uniform(self.settings.min_wait_sec, self.settings.max_wait_sec))
            body, etag, last_modified = self.fetch(url)
            parsed = parse_listing(body, url)
            key = dedupe_key(parsed)
            if key in seen:
                continue
            seen.add(key)
            raw_hash = hashlib.sha256(body.encode()).hexdigest()
            db.add(
                ListingRaw(
                    site_name=self.settings.target_site_name,
                    site_listing_id=parsed.site_listing_id,
                    canonical_url=parsed.canonical_url,
                    response_body=body,
                    raw_hash=raw_hash,
                    etag=etag,
                    last_modified=last_modified,
                )
            )
            row = db.query(ListingCurrent).filter(ListingCurrent.canonical_url == parsed.canonical_url).first()
            incoming = {
                "title": parsed.title,
                "price_yen": parsed.price_yen,
                "gross_yield_pct": parsed.gross_yield_pct,
                "raw_hash": raw_hash,
            }
            if row:
                changes = detect_changes(row, incoming)
                for k, v in incoming.items():
                    setattr(row, k, v)
                if changes:
                    db.add(
                        ManualReviewQueue(
                            queue_type="listing_change",
                            target_id=str(row.id),
                            reason_code="TRACKED_FIELD_CHANGED",
                            payload=changes,
                        )
                    )
            else:
                row = ListingCurrent(
                    site_name=self.settings.target_site_name,
                    site_listing_id=parsed.site_listing_id,
                    canonical_url=parsed.canonical_url,
                    title=parsed.title,
                    raw_hash=raw_hash,
                    first_seen_at=datetime.utcnow(),
                    last_seen_at=datetime.utcnow(),
                    last_changed_at=datetime.utcnow(),
                )
                db.add(row)
        db.commit()
