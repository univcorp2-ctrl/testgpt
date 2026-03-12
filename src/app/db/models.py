from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CrawlRun(Base):
    __tablename__ = "crawl_run"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    mode: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="running")


class QueryPlan(Base):
    __tablename__ = "query_plan"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    crawl_run_id: Mapped[int] = mapped_column(Integer)
    shard_key: Mapped[str] = mapped_column(String(255))
    query_params: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default="pending")


class ListingRaw(Base):
    __tablename__ = "listing_raw"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_name: Mapped[str] = mapped_column(String(64))
    site_listing_id: Mapped[str | None] = mapped_column(String(128))
    canonical_url: Mapped[str] = mapped_column(Text)
    response_format: Mapped[str] = mapped_column(String(16), default="html")
    response_body: Mapped[str] = mapped_column(Text)
    etag: Mapped[str | None] = mapped_column(String(255))
    last_modified: Mapped[str | None] = mapped_column(String(255))
    raw_hash: Mapped[str] = mapped_column(String(64), index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ListingCurrent(Base):
    __tablename__ = "listing_current"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_name: Mapped[str] = mapped_column(String(64))
    site_listing_id: Mapped[str | None] = mapped_column(String(128), index=True)
    canonical_url: Mapped[str] = mapped_column(Text, index=True)
    title: Mapped[str | None] = mapped_column(Text)
    property_type: Mapped[str | None] = mapped_column(String(64))
    prefecture: Mapped[str | None] = mapped_column(String(32))
    city: Mapped[str | None] = mapped_column(String(64))
    town: Mapped[str | None] = mapped_column(String(64))
    address_text: Mapped[str | None] = mapped_column(Text)
    access_text: Mapped[str | None] = mapped_column(Text)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    structure: Mapped[str | None] = mapped_column(String(64))
    built_year: Mapped[int | None] = mapped_column(Integer)
    built_month: Mapped[int | None] = mapped_column(Integer)
    age_years: Mapped[float | None] = mapped_column(Float)
    land_area_m2: Mapped[float | None] = mapped_column(Float)
    building_area_m2: Mapped[float | None] = mapped_column(Float)
    rentable_area_m2: Mapped[float | None] = mapped_column(Float)
    floors: Mapped[str | None] = mapped_column(String(32))
    units: Mapped[int | None] = mapped_column(Integer)
    occupancy_status: Mapped[str | None] = mapped_column(String(64))
    current_rent_yen: Mapped[float | None] = mapped_column(Float)
    annual_rent_yen: Mapped[float | None] = mapped_column(Float)
    annual_full_rent_yen: Mapped[float | None] = mapped_column(Float)
    price_yen: Mapped[float | None] = mapped_column(Float)
    gross_yield_pct: Mapped[float | None] = mapped_column(Float)
    management_fee_yen: Mapped[float | None] = mapped_column(Float)
    repair_reserve_yen: Mapped[float | None] = mapped_column(Float)
    brokerage_type: Mapped[str | None] = mapped_column(String(32))
    seller_name: Mapped[str | None] = mapped_column(String(128))
    remarks: Mapped[str | None] = mapped_column(Text)
    is_member_only: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_hash: Mapped[str] = mapped_column(String(64))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ListingHistory(Base):
    __tablename__ = "listing_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_current_id: Mapped[int] = mapped_column(Integer)
    change_type: Mapped[str] = mapped_column(String(32))
    changed_fields: Mapped[dict[str, Any]] = mapped_column(JSON)
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PropertyMaster(Base):
    __tablename__ = "property_master"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_current_id: Mapped[int] = mapped_column(Integer)


class SellerMaster(Base):
    __tablename__ = "seller_master"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)


class AddressGeocode(Base):
    __tablename__ = "address_geocode"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_current_id: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(64))
    confidence: Mapped[float] = mapped_column(Float)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="ok")


class LandValuation(Base):
    __tablename__ = "land_valuation"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_current_id: Mapped[int] = mapped_column(Integer)
    valuation_method: Mapped[str] = mapped_column(String(32))
    source_year: Mapped[int | None] = mapped_column(Integer)
    source_url: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    land_value_yen: Mapped[float | None] = mapped_column(Float)


class BuildingValuation(Base):
    __tablename__ = "building_valuation"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_current_id: Mapped[int] = mapped_column(Integer)
    structure: Mapped[str | None] = mapped_column(String(64))
    depreciation_factor: Mapped[float] = mapped_column(Float, default=0.0)
    building_value_yen: Mapped[float | None] = mapped_column(Float)
    tax_simple_remaining_life: Mapped[int | None] = mapped_column(Integer)
    lender_remaining_term: Mapped[int | None] = mapped_column(Integer)


class AnalysisScenario(Base):
    __tablename__ = "analysis_scenario"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
    params: Mapped[dict[str, Any]] = mapped_column(JSON)


class AnalysisResult(Base):
    __tablename__ = "analysis_result"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_current_id: Mapped[int] = mapped_column(Integer)
    scenario_name: Mapped[str] = mapped_column(String(32))
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON)
    pass_fail: Mapped[str] = mapped_column(String(8))
    fail_reason_codes: Mapped[list[str]] = mapped_column(JSON)


class ManualReviewQueue(Base):
    __tablename__ = "manual_review_queue"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    queue_type: Mapped[str] = mapped_column(String(64))
    target_id: Mapped[str] = mapped_column(String(128))
    reason_code: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
