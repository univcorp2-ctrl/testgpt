from __future__ import annotations

from dataclasses import dataclass
from math import floor
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class LandConfig:
    area_m2: float
    bcr_percent: float
    far_percent: float
    zoning: str
    road_width_m: Optional[float] = None
    far_road_coefficient: Optional[float] = None


@dataclass(frozen=True)
class BuildConfig:
    name: str
    structure: str
    floor_to_floor_m: float
    base_common_ratio: float
    common_ratio_add_per_floor: float
    min_floor_plate_m2: Optional[float] = None
    max_height_m: Optional[float] = None
    height_district_limit_m: Optional[float] = None
    max_floors_override: Optional[int] = None
    elevator_threshold_floors: int = 0
    elevator_cost_yen: float = 0.0


@dataclass(frozen=True)
class EconomicsConfig:
    land_price_yen: float
    construction_cost_yen_per_m2: float
    soft_cost_ratio: float
    contingency_ratio: float
    vacancy_ratio: float
    opex_ratio: float
    property_tax_yen_per_year: float
    cost_uplift_per_floor_after: int
    cost_uplift_rate_per_extra_floor: float


@dataclass(frozen=True)
class UnitOptions:
    min_m2: float
    max_m2: float
    step_m2: float
    rent_bands: List[Dict[str, float]]
    extra_cost_per_unit_yen: float = 0.0
    extra_opex_per_unit_year_yen: float = 0.0
    labels_by_area_m2: Optional[Dict[str, str]] = None


@dataclass(frozen=True)
class OneRoomOrdinance:
    enabled: bool
    apply_if_units_ge: Optional[int] = None
    min_unit_area_m2: Optional[float] = None
    small_unit_threshold_m2: Optional[float] = None
    max_small_unit_ratio: Optional[float] = None
    max_small_unit_count: Optional[int] = None
    family_unit_threshold_m2: Optional[float] = None
    min_family_unit_ratio: Optional[float] = None
    min_family_unit_count: Optional[int] = None
    max_units_total: Optional[int] = None


@dataclass(frozen=True)
class ObjectiveConfig:
    metric: str
    waste_penalty_rate: float


@dataclass(frozen=True)
class IRRConfig:
    enabled: bool
    hold_years: int
    rent_growth_rate: float
    fixed_opex_growth_rate: float
    exit_cap_rate: float
    selling_cost_ratio: float
    use_noi_next_year_for_exit: bool


@dataclass(frozen=True)
class SearchConfig:
    search_max_types: int
    waste_allowance_ratio: float


@dataclass
class PlanResult:
    floors: int
    footprint_m2: float
    total_floor_area_m2: float
    rentable_area_m2: float
    common_ratio: float
    unit_mix: List[Dict[str, Any]]
    units_total: int
    annual_gross_rent_yen: float
    egi_yen: float
    noi_yen: float
    total_investment_yen: float
    construction_cost_yen: float
    soft_cost_yen: float
    contingency_yen: float
    gross_yield: float
    noi_yield: float
    irr: Optional[float]
    waste_ratio: float
    notes: List[str]


LOW_RISE_KEYWORD = "低層"


def zoning_absolute_height_limit(zoning: str) -> Optional[float]:
    if LOW_RISE_KEYWORD in zoning:
        return 10.0
    return None


def effective_far_percent(land: LandConfig) -> Tuple[float, List[str]]:
    notes: List[str] = []
    if land.road_width_m is None or land.far_road_coefficient is None:
        notes.append("道路による容積制限は未反映")
        return land.far_percent, notes
    road_limit = land.road_width_m * land.far_road_coefficient * 100
    return min(land.far_percent, road_limit), notes


def effective_height_limit_m(land: LandConfig, build: BuildConfig) -> Tuple[float, List[str]]:
    notes: List[str] = []
    limits = []
    if build.max_height_m is not None:
        limits.append(build.max_height_m)
    if build.height_district_limit_m is not None:
        limits.append(build.height_district_limit_m)
    zoning_limit = zoning_absolute_height_limit(land.zoning)
    if zoning_limit is not None:
        limits.append(zoning_limit)
    if not limits:
        notes.append("高さ上限は設定されていません")
        return float("inf"), notes
    return min(limits), notes


def max_floors(land: LandConfig, build: BuildConfig, max_total_floor_area: float) -> int:
    structure_limit = 3 if build.structure == "wood" else 6
    height_limit_m, _ = effective_height_limit_m(land, build)
    if height_limit_m == float("inf"):
        height_limit = structure_limit
    else:
        height_limit = max(1, floor(height_limit_m / build.floor_to_floor_m))
    floor_plate_limit = height_limit
    if build.min_floor_plate_m2:
        floor_plate_limit = max(1, floor(max_total_floor_area / build.min_floor_plate_m2))
    limit = min(structure_limit, height_limit, floor_plate_limit)
    if build.max_floors_override is not None:
        limit = min(limit, build.max_floors_override)
    return max(1, limit)


def common_ratio_for_floors(build: BuildConfig, floors: int) -> float:
    ratio = build.base_common_ratio + (floors - 1) * build.common_ratio_add_per_floor
    return min(ratio, 0.35)


def unit_sizes(options: UnitOptions) -> List[float]:
    size = options.min_m2
    sizes: List[float] = []
    while size <= options.max_m2 + 1e-6:
        sizes.append(round(size, 2))
        size += options.step_m2
    return sizes


def rent_per_m2(size: float, bands: List[Dict[str, float]]) -> float:
    for band in bands:
        if band["min_m2"] <= size <= band["max_m2"]:
            return band["rent_yen_per_m2_month"]
    raise ValueError(f"Rent band not found for unit size {size}")


def label_for_unit(size: float, options: UnitOptions) -> str:
    if options.labels_by_area_m2 is None:
        return f"{size:.1f}m2"
    return options.labels_by_area_m2.get(str(size), f"{size:.1f}m2")


def ordinance_ok(
    ordinance: OneRoomOrdinance, units: List[Tuple[float, int]]
) -> bool:
    if not ordinance.enabled:
        return True
    total_units = sum(count for _, count in units)
    if ordinance.apply_if_units_ge is not None and total_units < ordinance.apply_if_units_ge:
        return True
    if ordinance.max_units_total is not None and total_units > ordinance.max_units_total:
        return False
    if ordinance.min_unit_area_m2 is not None:
        for size, count in units:
            if count > 0 and size < ordinance.min_unit_area_m2:
                return False
    if total_units == 0:
        return False
    small_units = 0
    family_units = 0
    if ordinance.small_unit_threshold_m2 is not None:
        small_units = sum(count for size, count in units if size < ordinance.small_unit_threshold_m2)
    if ordinance.family_unit_threshold_m2 is not None:
        family_units = sum(count for size, count in units if size >= ordinance.family_unit_threshold_m2)
    if ordinance.max_small_unit_ratio is not None:
        if small_units / total_units > ordinance.max_small_unit_ratio:
            return False
    if ordinance.max_small_unit_count is not None:
        if small_units > ordinance.max_small_unit_count:
            return False
    if ordinance.min_family_unit_ratio is not None:
        if family_units / total_units < ordinance.min_family_unit_ratio:
            return False
    if ordinance.min_family_unit_count is not None:
        if family_units < ordinance.min_family_unit_count:
            return False
    return True


def unit_mix_candidates(
    rentable_area: float,
    options: UnitOptions,
    ordinance: OneRoomOrdinance,
    search: SearchConfig,
) -> Iterable[Tuple[List[Tuple[float, int]], float]]:
    sizes = unit_sizes(options)
    max_units = max(1, floor(rentable_area / options.min_m2))
    for idx, size in enumerate(sizes):
        for count in range(1, max_units + 1):
            total_area = size * count
            waste = rentable_area - total_area
            if waste < -1e-6:
                continue
            waste_ratio = waste / rentable_area
            if waste_ratio > search.waste_allowance_ratio:
                continue
            units = [(size, count)]
            if ordinance_ok(ordinance, units):
                yield units, waste_ratio
        if search.search_max_types == 1:
            continue
        for size2 in sizes[idx + 1 :]:
            for count1 in range(1, max_units + 1):
                for count2 in range(1, max_units + 1):
                    total_area = size * count1 + size2 * count2
                    waste = rentable_area - total_area
                    if waste < -1e-6:
                        continue
                    waste_ratio = waste / rentable_area
                    if waste_ratio > search.waste_allowance_ratio:
                        continue
                    units = [(size, count1), (size2, count2)]
                    if ordinance_ok(ordinance, units):
                        yield units, waste_ratio


def annual_rent_for_units(units: List[Tuple[float, int]], options: UnitOptions) -> Tuple[float, List[Dict[str, Any]]]:
    total = 0.0
    mix: List[Dict[str, Any]] = []
    for size, count in units:
        monthly = size * rent_per_m2(size, options.rent_bands)
        annual = monthly * 12 * count
        total += annual
        mix.append(
            {
                "size_m2": size,
                "count": count,
                "label": label_for_unit(size, options),
                "rent_yen_per_m2_month": rent_per_m2(size, options.rent_bands),
            }
        )
    return total, mix


def construction_cost(
    total_floor_area: float,
    floors: int,
    econ: EconomicsConfig,
    units_total: int,
    options: UnitOptions,
    build: BuildConfig,
) -> float:
    uplift_floors = max(0, floors - econ.cost_uplift_per_floor_after)
    uplift_multiplier = 1 + econ.cost_uplift_rate_per_extra_floor * uplift_floors
    base_cost = total_floor_area * econ.construction_cost_yen_per_m2 * uplift_multiplier
    elevator_cost = build.elevator_cost_yen if floors >= build.elevator_threshold_floors else 0.0
    unit_extra = options.extra_cost_per_unit_yen * units_total
    return base_cost + elevator_cost + unit_extra


def compute_irr(cash_flows: List[float]) -> Optional[float]:
    def npv(rate: float) -> float:
        return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))

    low = -0.9
    high = 1.0
    npv_low = npv(low)
    npv_high = npv(high)
    attempts = 0
    while npv_low * npv_high > 0 and attempts < 50:
        high += 0.5
        npv_high = npv(high)
        attempts += 1
    if npv_low * npv_high > 0:
        return None
    for _ in range(100):
        mid = (low + high) / 2
        npv_mid = npv(mid)
        if abs(npv_mid) < 1e-6:
            return mid
        if npv_low * npv_mid <= 0:
            high = mid
            npv_high = npv_mid
        else:
            low = mid
            npv_low = npv_mid
    return (low + high) / 2


def irr_for_plan(
    econ: EconomicsConfig,
    options: UnitOptions,
    irr_cfg: IRRConfig,
    vacancy_ratio: float,
    opex_ratio: float,
    annual_gross_rent: float,
    units_total: int,
    total_investment: float,
) -> Optional[float]:
    if not irr_cfg.enabled:
        return None
    base_opex_fixed = econ.property_tax_yen_per_year + options.extra_opex_per_unit_year_yen * units_total
    cash_flows = [-total_investment]
    gross_rent = annual_gross_rent
    for year in range(1, irr_cfg.hold_years + 1):
        if year > 1:
            gross_rent *= 1 + irr_cfg.rent_growth_rate
        egi = gross_rent * (1 - vacancy_ratio)
        fixed_opex = base_opex_fixed * ((1 + irr_cfg.fixed_opex_growth_rate) ** (year - 1))
        opex = egi * opex_ratio + fixed_opex
        cash_flows.append(egi - opex)
    exit_year = irr_cfg.hold_years + 1 if irr_cfg.use_noi_next_year_for_exit else irr_cfg.hold_years
    gross_rent_exit = annual_gross_rent * ((1 + irr_cfg.rent_growth_rate) ** (exit_year - 1))
    egi_exit = gross_rent_exit * (1 - vacancy_ratio)
    fixed_opex_exit = base_opex_fixed * ((1 + irr_cfg.fixed_opex_growth_rate) ** (exit_year - 1))
    noi_exit = egi_exit - (egi_exit * opex_ratio + fixed_opex_exit)
    exit_price = noi_exit / irr_cfg.exit_cap_rate
    selling_cost = exit_price * irr_cfg.selling_cost_ratio
    cash_flows[-1] += exit_price - selling_cost
    return compute_irr(cash_flows)


def objective_score(
    objective: ObjectiveConfig,
    gross_yield: float,
    noi_yield: float,
    waste_ratio: float,
) -> float:
    metric_value = gross_yield if objective.metric == "gross_yield" else noi_yield
    penalty = 1 - objective.waste_penalty_rate * waste_ratio
    return metric_value * penalty


def evaluate_floors(
    land: LandConfig,
    build: BuildConfig,
    econ: EconomicsConfig,
    options: UnitOptions,
    ordinance: OneRoomOrdinance,
    objective: ObjectiveConfig,
    irr_cfg: IRRConfig,
    search: SearchConfig,
    floors: int,
    max_footprint: float,
    max_total_floor_area: float,
    notes_base: List[str],
) -> Optional[PlanResult]:
    footprint = min(max_footprint, max_total_floor_area / floors)
    if build.min_floor_plate_m2 and footprint < build.min_floor_plate_m2:
        return None
    total_floor_area = footprint * floors
    common_ratio = common_ratio_for_floors(build, floors)
    rentable_area = total_floor_area * (1 - common_ratio)
    best_result: Optional[PlanResult] = None
    best_score: Optional[float] = None
    for units, waste_ratio in unit_mix_candidates(rentable_area, options, ordinance, search):
        annual_rent, mix = annual_rent_for_units(units, options)
        total_units = sum(count for _, count in units)
        construction = construction_cost(total_floor_area, floors, econ, total_units, options, build)
        soft = construction * econ.soft_cost_ratio
        contingency = construction * econ.contingency_ratio
        total_invest = econ.land_price_yen + construction + soft + contingency
        egi = annual_rent * (1 - econ.vacancy_ratio)
        opex = egi * econ.opex_ratio + econ.property_tax_yen_per_year + options.extra_opex_per_unit_year_yen * total_units
        noi = egi - opex
        gross_yield = annual_rent / total_invest if total_invest > 0 else 0
        noi_yield = noi / total_invest if total_invest > 0 else 0
        irr = irr_for_plan(
            econ,
            options,
            irr_cfg,
            econ.vacancy_ratio,
            econ.opex_ratio,
            annual_rent,
            total_units,
            total_invest,
        )
        score = objective_score(objective, gross_yield, noi_yield, waste_ratio)
        candidate = PlanResult(
            floors=floors,
            footprint_m2=round(footprint, 2),
            total_floor_area_m2=round(total_floor_area, 2),
            rentable_area_m2=round(rentable_area, 2),
            common_ratio=round(common_ratio, 4),
            unit_mix=mix,
            units_total=total_units,
            annual_gross_rent_yen=round(annual_rent, 2),
            egi_yen=round(egi, 2),
            noi_yen=round(noi, 2),
            total_investment_yen=round(total_invest, 2),
            construction_cost_yen=round(construction, 2),
            soft_cost_yen=round(soft, 2),
            contingency_yen=round(contingency, 2),
            gross_yield=round(gross_yield, 6),
            noi_yield=round(noi_yield, 6),
            irr=None if irr is None else round(irr, 6),
            waste_ratio=round(waste_ratio, 4),
            notes=list(notes_base),
        )
        if best_score is None or score > best_score:
            best_result = candidate
            best_score = score
    return best_result


def pareto_front(plans: List[PlanResult]) -> List[PlanResult]:
    front = []
    for plan in plans:
        dominated = False
        for other in plans:
            if other.gross_yield >= plan.gross_yield and other.noi_yield >= plan.noi_yield:
                if other.gross_yield > plan.gross_yield or other.noi_yield > plan.noi_yield:
                    dominated = True
                    break
        if not dominated:
            front.append(plan)
    return front


def evaluate_build_variant(
    land: LandConfig,
    build: BuildConfig,
    econ: EconomicsConfig,
    options: UnitOptions,
    ordinance: OneRoomOrdinance,
    objective: ObjectiveConfig,
    irr_cfg: IRRConfig,
    search: SearchConfig,
) -> Dict[str, Any]:
    far_percent, far_notes = effective_far_percent(land)
    max_footprint = land.area_m2 * land.bcr_percent / 100
    max_total_floor_area = land.area_m2 * far_percent / 100
    height_limit, height_notes = effective_height_limit_m(land, build)
    notes = far_notes + height_notes
    max_floor_count = max_floors(land, build, max_total_floor_area)
    all_plans: List[PlanResult] = []
    for floors in range(1, max_floor_count + 1):
        plan = evaluate_floors(
            land,
            build,
            econ,
            options,
            ordinance,
            objective,
            irr_cfg,
            search,
            floors,
            max_footprint,
            max_total_floor_area,
            notes,
        )
        if plan:
            all_plans.append(plan)
    if not all_plans:
        return {
            "name": build.name,
            "notes": notes + ["有効なプランが見つかりません"],
            "max_floors": max_floor_count,
            "height_limit_m": None if height_limit == float("inf") else height_limit,
            "plans": [],
        }
    best_gross = max(all_plans, key=lambda plan: plan.gross_yield)
    best_noi = max(all_plans, key=lambda plan: plan.noi_yield)
    best_floors = max(all_plans, key=lambda plan: plan.floors)
    pareto = pareto_front(all_plans)
    return {
        "name": build.name,
        "notes": notes,
        "max_floors": max_floor_count,
        "height_limit_m": None if height_limit == float("inf") else height_limit,
        "best_gross_yield_plan": best_gross.__dict__,
        "best_noi_yield_plan": best_noi.__dict__,
        "best_floors_plan": best_floors.__dict__,
        "pareto_front": [plan.__dict__ for plan in pareto],
    }


def _build_config_from_dict(base: Dict[str, Any], override: Optional[Dict[str, Any]]) -> BuildConfig:
    merged = dict(base)
    if override:
        merged.update(override)
    return BuildConfig(**merged)


def run_optimization(config: Dict[str, Any]) -> Dict[str, Any]:
    land = LandConfig(**config["land"])
    econ = EconomicsConfig(**config["economics"])
    options = UnitOptions(**config["unit_options"])
    ordinance = OneRoomOrdinance(**config["one_room_ordinance"])
    objective = ObjectiveConfig(**config["objective"])
    irr_cfg = IRRConfig(**config["irr"])
    search = SearchConfig(**config["search"])

    build_base = config["build"]
    variants = config.get("build_variants", [])
    build_configs = [
        _build_config_from_dict(build_base, None)
    ]
    for variant in variants:
        build_configs.append(_build_config_from_dict(build_base, variant))

    variant_results = []
    for build in build_configs:
        variant_results.append(
            evaluate_build_variant(
                land,
                build,
                econ,
                options,
                ordinance,
                objective,
                irr_cfg,
                search,
            )
        )

    overall_best = None
    for result in variant_results:
        best_plan = result.get("best_gross_yield_plan")
        if not best_plan:
            continue
        if overall_best is None or best_plan["gross_yield"] > overall_best["gross_yield"]:
            overall_best = {"variant": result["name"], **best_plan}

    return {
        "land": land.__dict__,
        "variants": variant_results,
        "overall_best_gross_yield_plan": overall_best,
    }
