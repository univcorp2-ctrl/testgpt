from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session


def export_csvs(db: Session, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.utcnow().strftime("%Y%m%d")
    mapping = {
        "listing_current": output_dir / f"listings_current_{stamp}.csv",
        "listing_history": output_dir / f"listings_history_{stamp}.csv",
        "analysis_result": output_dir / f"analysis_results_{stamp}.csv",
        "manual_review_queue": output_dir / f"manual_review_{stamp}.csv",
    }
    out: list[Path] = []
    for table, path in mapping.items():
        df = pd.read_sql(text(f"select * from {table}"), db.bind)
        df.to_csv(path, index=False)
        out.append(path)
    return out
