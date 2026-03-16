from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RouteValueResult:
    method: str
    land_value_yen: float | None
    confidence: float
    source_year: int | None
    source_url: str | None


class RouteValueAdapter:
    source_name: str

    def evaluate(self, *, route_value_per_m2: float | None, land_area_m2: float | None) -> RouteValueResult:
        raise NotImplementedError


class OfficialNTAAdapter(RouteValueAdapter):
    source_name = "official_nta_import"

    def evaluate(self, *, route_value_per_m2: float | None, land_area_m2: float | None) -> RouteValueResult:
        if route_value_per_m2 is None or land_area_m2 is None:
            return RouteValueResult("manual", None, 0.0, None, None)
        return RouteValueResult(
            "simple",
            route_value_per_m2 * land_area_m2,
            0.6,
            2024,
            "https://www.rosenka.nta.go.jp/",
        )
