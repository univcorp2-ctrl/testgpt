from __future__ import annotations

from pathlib import Path

from app.config import AppSettings


def doctor(settings: AppSettings) -> list[str]:
    checks = []
    checks.append(f"output_dir_exists={settings.output_dir.exists()}")
    checks.append(f"session_state_exists={Path(settings.session_state_path).exists()}")
    checks.append(f"compliance_approved={settings.compliance_approved}")
    return checks
