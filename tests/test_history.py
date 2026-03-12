from dataclasses import dataclass
from datetime import datetime

from app.services.history import detect_changes


@dataclass
class Row:
    title: str
    price_yen: float
    gross_yield_pct: float
    occupancy_status: str
    last_seen_at: datetime
    last_changed_at: datetime


def test_history_detects_price_change() -> None:
    row = Row("a", 100.0, 10.0, "x", datetime.utcnow(), datetime.utcnow())
    ch = detect_changes(row, {"title": "a", "price_yen": 200.0, "gross_yield_pct": 10.0, "occupancy_status": "x"})
    assert "price_yen" in ch
