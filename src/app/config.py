from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CommercialAPI:
    zenrin_maps_api_key: str = ""
    parea_api_key: str = ""


@dataclass
class UserThresholds:
    interest_rate_min: float = 0.01
    interest_rate_max: float = 0.03
    interest_rate_step: float = 0.0025
    dscr_min: float = 1.30
    debt_ratio_max: float = 0.50
    hand_nokori_ratio_min_pct: float = 1.3


@dataclass
class DefaultAssumptions:
    vacancy_rate_base: float = 0.08
    vacancy_rate_stress_add: float = 0.05
    rent_drop_stress: float = 0.05
    opex_ratio_base: float = 0.15
    opex_stress_add: float = 0.10
    rate_stress_add: float = 0.005
    acquisition_cost_rate: float = 0.07
    capex_reserve_ratio: float = 0.05
    property_tax_ratio_hint: float = 0.01


@dataclass
class AppSettings:
    target_site_name: str = "健美家"
    target_base_url: str = "<ここに対象ドメイン>"
    login_url: str = "<ここにログインURL>"
    start_urls: list[str] = field(default_factory=lambda: ["<ここに開始URL1>", "<ここに開始URL2>"])
    allowed_scope: str = "公開物件 + 契約・利用規約上許容される会員限定物件のみ"
    db_dsn: str = "postgresql+psycopg://app:app@localhost:5432/kenbiya"
    output_dir: Path = Path("exports")
    session_state_path: Path = Path("secrets/session_state.enc")
    route_value_source_priority: list[str] = field(default_factory=lambda: ["official_nta_import", "commercial_api", "manual_review"])
    commercial_api: CommercialAPI = field(default_factory=CommercialAPI)
    user_thresholds: UserThresholds = field(default_factory=UserThresholds)
    default_assumptions: DefaultAssumptions = field(default_factory=DefaultAssumptions)
    compliance_approved: bool = False
    host_concurrency: int = 1
    min_wait_sec: int = 5
    max_wait_sec: int = 10


def get_settings(**overrides: Any) -> AppSettings:
    s = AppSettings()
    if os.getenv("TARGET_BASE_URL"):
        s.target_base_url = os.environ["TARGET_BASE_URL"]
    if os.getenv("LOGIN_URL"):
        s.login_url = os.environ["LOGIN_URL"]
    if os.getenv("DB_DSN"):
        s.db_dsn = os.environ["DB_DSN"]
    if os.getenv("START_URLS"):
        s.start_urls = json.loads(os.environ["START_URLS"])
    if os.getenv("COMPLIANCE_APPROVED"):
        s.compliance_approved = os.environ["COMPLIANCE_APPROVED"].lower() == "true"
    for k, v in overrides.items():
        setattr(s, k, v)
    return s
