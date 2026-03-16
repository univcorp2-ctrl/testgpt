from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GeocodeResult:
    lat: float | None
    lon: float | None
    confidence: float
    status: str


class GeocoderAdapter:
    def geocode(self, address: str) -> GeocodeResult:
        raise NotImplementedError


class DummyGeocoder(GeocoderAdapter):
    def geocode(self, address: str) -> GeocodeResult:
        if len(address) < 6:
            return GeocodeResult(None, None, 0.0, "failed")
        return GeocodeResult(35.0, 139.0, 0.5, "low_confidence")
