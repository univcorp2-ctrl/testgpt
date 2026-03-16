from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AnalysisInput:
    gpr: float
    vacancy_rate: float
    opex_ratio: float
    ads: float
    interest_rate: float
    price_yen: float
    total_project_cost: float
    cash_invested: float
    cumulative_value: float


def compute_metrics(x: AnalysisInput) -> dict[str, float]:
    egi = x.gpr * (1 - x.vacancy_rate)
    opex = egi * x.opex_ratio
    noi = egi - opex
    pre_tax_cf = noi - x.ads
    noi_yield = noi / x.price_yen
    dscr = noi / x.ads if x.ads else 0.0
    debt_ratio = x.ads / x.gpr if x.gpr else 0.0
    break_even_occupancy = (opex + x.ads) / x.gpr if x.gpr else 1.0
    return {
        "GPR": x.gpr,
        "EGI": egi,
        "OPEX": opex,
        "NOI": noi,
        "ADS": x.ads,
        "pre_tax_cf": pre_tax_cf,
        "gross_yield": x.gpr / x.price_yen,
        "noi_yield": noi_yield,
        "ccr": pre_tax_cf / x.cash_invested if x.cash_invested else 0.0,
        "dscr": dscr,
        "debt_ratio": debt_ratio,
        "ltv": (x.total_project_cost - x.cash_invested) / x.price_yen,
        "break_even_occupancy": break_even_occupancy,
        "yield_gap": noi_yield - x.interest_rate,
        "cumulative_to_price_ratio": x.cumulative_value / x.price_yen,
        "hand_nokori_ratio_pct": pre_tax_cf / x.total_project_cost * 100,
        "hand_nokori_on_equity_pct": pre_tax_cf / x.cash_invested * 100 if x.cash_invested else 0.0,
    }


def judge(metrics: dict[str, float], dscr_min: float, debt_ratio_max: float, hand_min_pct: float) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if metrics["dscr"] < dscr_min:
        reasons.append("DSCR_LOW")
    if metrics["debt_ratio"] > debt_ratio_max:
        reasons.append("DEBT_RATIO_HIGH")
    if metrics["pre_tax_cf"] <= 0:
        reasons.append("NEGATIVE_CF")
    if metrics["hand_nokori_ratio_pct"] < hand_min_pct:
        reasons.append("HAND_NOKORI_LOW")
    return ("PASS" if not reasons else "FAIL", reasons)
