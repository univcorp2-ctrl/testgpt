from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

from optimizer import run_optimization


def load_config(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Config not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in config: {exc}") from exc


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python cli.py <config.json>")
    config_path = Path(sys.argv[1])
    config = load_config(config_path)
    result = run_optimization(config)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
