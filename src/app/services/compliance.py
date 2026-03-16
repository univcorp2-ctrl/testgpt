from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.config import AppSettings


@dataclass
class ComplianceResult:
    robots_url: str
    robots_found: bool
    terms_url: str
    api_export_available: str
    allowed: bool
    notes: list[str]


class ComplianceService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    def check(self) -> ComplianceResult:
        robots_url = f"{self.settings.target_base_url.rstrip('/')}/robots.txt"
        notes: list[str] = []
        robots_found = False
        try:
            resp = httpx.get(robots_url, timeout=15)
            robots_found = resp.status_code == 200
            if robots_found and "disallow" in resp.text.lower():
                notes.append("robots.txt contains Disallow directives; manual scope validation required")
        except httpx.HTTPError:
            notes.append("robots.txt fetch failed")
        terms_url = f"{self.settings.target_base_url.rstrip('/')}/terms"
        notes.append("Terms/API/export detection is semi-automated and must be manually reviewed.")
        allowed = self.settings.compliance_approved
        return ComplianceResult(
            robots_url=robots_url,
            robots_found=robots_found,
            terms_url=terms_url,
            api_export_available="manual_review",
            allowed=allowed,
            notes=notes,
        )

    def assert_crawl_allowed(self) -> None:
        if not self.settings.compliance_approved:
            raise RuntimeError("Compliance approval is false. Crawl commands are locked.")
