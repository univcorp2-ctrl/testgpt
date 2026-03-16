from __future__ import annotations

import click

from app.config import get_settings


@click.group()
def app() -> None:
    pass


def _session(settings):
    from app.db.session import get_session_factory

    return get_session_factory(settings)()


@app.command(name="bootstrap-login")
def bootstrap_login_cmd() -> None:
    import os

    from app.services.bootstrap_login import bootstrap_login

    settings = get_settings()
    key = os.getenv("APP_ENCRYPTION_KEY", "temporary_dev_key")
    path = bootstrap_login(settings, key)
    click.echo(f"saved encrypted session state to {path}")


@app.command(name="compliance-check")
def compliance_check_cmd() -> None:
    import json

    from app.services.compliance import ComplianceService

    settings = get_settings()
    result = ComplianceService(settings).check()
    click.echo(json.dumps(result.__dict__, ensure_ascii=False, indent=2))


@app.command(name="crawl-backfill")
def crawl_backfill_cmd() -> None:
    from app.services.compliance import ComplianceService
    from app.services.crawler import CrawlerService

    settings = get_settings()
    ComplianceService(settings).assert_crawl_allowed()
    with _session(settings) as db:
        CrawlerService(settings).run_urls(db, settings.start_urls)


@app.command(name="crawl-delta")
def crawl_delta_cmd() -> None:
    crawl_backfill_cmd()


@app.command(name="enrich-geocode")
def enrich_geocode_cmd() -> None:
    from app.adapters.geocode import DummyGeocoder
    from app.db.models import AddressGeocode, ListingCurrent, ManualReviewQueue

    settings = get_settings()
    geocoder = DummyGeocoder()
    with _session(settings) as db:
        rows = db.query(ListingCurrent).all()
        for row in rows:
            if not row.address_text:
                continue
            res = geocoder.geocode(row.address_text)
            db.add(
                AddressGeocode(
                    listing_current_id=row.id,
                    source="dummy",
                    confidence=res.confidence,
                    lat=res.lat,
                    lon=res.lon,
                    status=res.status,
                )
            )
            if res.status != "ok":
                db.add(
                    ManualReviewQueue(
                        queue_type="geocode",
                        target_id=str(row.id),
                        reason_code="GEOCODE_LOW_CONFIDENCE",
                        payload={"status": res.status, "address": row.address_text},
                    )
                )
        db.commit()


@app.command(name="enrich-route-value")
def enrich_route_value_cmd() -> None:
    from app.adapters.route_value import OfficialNTAAdapter
    from app.db.models import LandValuation, ListingCurrent, ManualReviewQueue

    settings = get_settings()
    adapter = OfficialNTAAdapter()
    with _session(settings) as db:
        for row in db.query(ListingCurrent).all():
            result = adapter.evaluate(route_value_per_m2=None, land_area_m2=row.land_area_m2)
            db.add(
                LandValuation(
                    listing_current_id=row.id,
                    valuation_method=result.method,
                    source_year=result.source_year,
                    source_url=result.source_url,
                    confidence=result.confidence,
                    land_value_yen=result.land_value_yen,
                )
            )
            if result.method == "manual":
                db.add(
                    ManualReviewQueue(
                        queue_type="route_value",
                        target_id=str(row.id),
                        reason_code="INSUFFICIENT_DATA",
                        payload={"priority": settings.route_value_source_priority},
                    )
                )
        db.commit()


@app.command(name="analyze")
def analyze_cmd() -> None:
    import json

    from app.db.models import ListingCurrent
    from app.services.analysis import AnalysisInput, compute_metrics, judge

    settings = get_settings()
    with _session(settings) as db:
        for row in db.query(ListingCurrent).all():
            gpr = row.annual_full_rent_yen or row.annual_rent_yen or 0
            if not row.price_yen or gpr <= 0:
                continue
            metrics = compute_metrics(
                AnalysisInput(
                    gpr=gpr,
                    vacancy_rate=settings.default_assumptions.vacancy_rate_base,
                    opex_ratio=settings.default_assumptions.opex_ratio_base,
                    ads=gpr * 0.5,
                    interest_rate=settings.user_thresholds.interest_rate_min,
                    price_yen=row.price_yen,
                    total_project_cost=row.price_yen * (1 + settings.default_assumptions.acquisition_cost_rate),
                    cash_invested=row.price_yen * 0.2,
                    cumulative_value=row.price_yen * 0.8,
                )
            )
            pf, reasons = judge(
                metrics,
                settings.user_thresholds.dscr_min,
                settings.user_thresholds.debt_ratio_max,
                settings.user_thresholds.hand_nokori_ratio_min_pct,
            )
            db.execute(
                "insert into analysis_result(listing_current_id, scenario_name, metrics, pass_fail, fail_reason_codes) values (:id, :name, :metrics, :pf, :reasons)",
                {
                    "id": row.id,
                    "name": "base",
                    "metrics": json.dumps(metrics),
                    "pf": pf,
                    "reasons": json.dumps(reasons),
                },
            )
        db.commit()


@app.command(name="export-csv")
def export_csv_cmd() -> None:
    from app.services.exporter import export_csvs

    settings = get_settings()
    with _session(settings) as db:
        paths = export_csvs(db, settings.output_dir)
        for p in paths:
            click.echo(str(p))


@app.command(name="doctor")
def doctor_cmd() -> None:
    from app.services.doctor import doctor

    settings = get_settings()
    for line in doctor(settings):
        click.echo(line)


@app.command(name="resume")
def resume_cmd() -> None:
    from app.services.resume import resume_hint

    click.echo(resume_hint())


@app.command(name="init-db")
def init_db_cmd() -> None:
    from app.db.base import Base
    from app.db.session import get_engine

    settings = get_settings()
    engine = get_engine(settings)
    Base.metadata.create_all(engine)
    click.echo("db initialized")


@app.command(name="show-query-plan")
def show_query_plan_cmd() -> None:
    import json

    from app.services.query_partitioner import build_query_shards

    click.echo(json.dumps(build_query_shards(), ensure_ascii=False, indent=2))


@app.command(name="bootstrap-ai-affiliate")
@click.option("--base-dir", default=".", show_default=True, help="Scaffold output base directory")
def bootstrap_ai_affiliate_cmd(base_dir: str) -> None:
    from pathlib import Path

    from app.services.ai_affiliate_scaffold import bootstrap_ai_affiliate_workspace

    result = bootstrap_ai_affiliate_workspace(Path(base_dir))
    click.echo(f"workspace: {result.root}")
    click.echo(f"created directories: {len(result.created_dirs)}")
    click.echo(f"created files: {len(result.created_files)}")


@app.command(name="run-affiliate-deterministic")
@click.option("--input-jsonl", required=True, type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option(
    "--output-dir",
    default="ai_affiliate_automation/runs",
    show_default=True,
    type=click.Path(file_okay=False, path_type=str),
)
def run_affiliate_deterministic_cmd(input_jsonl: str, output_dir: str) -> None:
    import json
    from pathlib import Path

    from app.services.affiliate_ops import run_deterministic_pipeline

    result = run_deterministic_pipeline(Path(input_jsonl), Path(output_dir))
    click.echo(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
