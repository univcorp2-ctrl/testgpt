from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from line_storage import fetch_messages, list_sources


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query stored LINE messages")
    parser.add_argument(
        "--db",
        default="line_messages.sqlite3",
        help="SQLite DB path (default: line_messages.sqlite3)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-sources", help="List source channels with message counts")

    fetch_parser = subparsers.add_parser("fetch", help="Fetch messages")
    fetch_parser.add_argument("--source-type", help="group|room|user")
    fetch_parser.add_argument("--source-id", help="groupId/roomId/userId")
    fetch_parser.add_argument("--limit", type=int, default=50)

    return parser


def print_json(payload: Dict[str, Any] | list[Dict[str, Any]]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    db_path = Path(args.db)

    if args.command == "list-sources":
        print_json(list_sources(db_path))
        return
    if args.command == "fetch":
        messages = fetch_messages(
            db_path,
            source_type=args.source_type,
            source_id=args.source_id,
            limit=args.limit,
        )
        print_json(messages)
        return


if __name__ == "__main__":
    main()
