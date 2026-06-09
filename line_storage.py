from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class StoredMessage:
    source_type: str
    source_id: str
    message_id: str
    text: str
    links: List[str]
    timestamp_ms: int
    raw_event: Dict[str, Any]


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,
                source_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                text TEXT NOT NULL,
                links TEXT NOT NULL,
                timestamp_ms INTEGER NOT NULL,
                received_at TEXT NOT NULL,
                raw_event TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_messages_source
            ON messages (source_type, source_id)
            """
        )


def store_messages(db_path: Path, messages: Iterable[StoredMessage]) -> int:
    init_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    records = [
        (
            msg.source_type,
            msg.source_id,
            msg.message_id,
            msg.text,
            json.dumps(msg.links, ensure_ascii=False),
            msg.timestamp_ms,
            now,
            json.dumps(msg.raw_event, ensure_ascii=False),
        )
        for msg in messages
    ]
    if not records:
        return 0
    with sqlite3.connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO messages (
                source_type,
                source_id,
                message_id,
                text,
                links,
                timestamp_ms,
                received_at,
                raw_event
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            ,
            records,
        )
    return len(records)


def list_sources(db_path: Path) -> List[Dict[str, Any]]:
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT source_type, source_id, COUNT(*) as count
            FROM messages
            GROUP BY source_type, source_id
            ORDER BY count DESC
            """
        ).fetchall()
    return [
        {"source_type": row[0], "source_id": row[1], "count": row[2]}
        for row in rows
    ]


def fetch_messages(
    db_path: Path,
    source_type: Optional[str] = None,
    source_id: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    init_db(db_path)
    query = "SELECT source_type, source_id, message_id, text, links, timestamp_ms, received_at FROM messages"
    conditions = []
    params: List[Any] = []
    if source_type:
        conditions.append("source_type = ?")
        params.append(source_type)
    if source_id:
        conditions.append("source_id = ?")
        params.append(source_id)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY timestamp_ms DESC LIMIT ?"
    params.append(limit)
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [
        {
            "source_type": row[0],
            "source_id": row[1],
            "message_id": row[2],
            "text": row[3],
            "links": json.loads(row[4]),
            "timestamp_ms": row[5],
            "received_at": row[6],
        }
        for row in rows
    ]
