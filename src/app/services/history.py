from __future__ import annotations

from datetime import datetime
from typing import Any

TRACK_FIELDS = ["title", "price_yen", "gross_yield_pct", "occupancy_status"]


def detect_changes(current: Any, incoming: dict[str, object]) -> dict[str, dict[str, object]]:
    changes: dict[str, dict[str, object]] = {}
    for field in TRACK_FIELDS:
        before = getattr(current, field, None)
        after = incoming.get(field)
        if before != after:
            changes[field] = {"before": before, "after": after}
    if changes:
        current.last_changed_at = datetime.utcnow()
    current.last_seen_at = datetime.utcnow()
    return changes
