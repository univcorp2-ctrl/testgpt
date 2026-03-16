"""init schema"""

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("crawl_run", sa.Column("id", sa.Integer, primary_key=True), sa.Column("started_at", sa.DateTime), sa.Column("finished_at", sa.DateTime), sa.Column("mode", sa.String(32)), sa.Column("status", sa.String(32)))
    op.create_table("query_plan", sa.Column("id", sa.Integer, primary_key=True), sa.Column("crawl_run_id", sa.Integer), sa.Column("shard_key", sa.String(255)), sa.Column("query_params", sa.JSON), sa.Column("status", sa.String(32)))
    op.create_table("listing_raw", sa.Column("id", sa.Integer, primary_key=True), sa.Column("site_name", sa.String(64)), sa.Column("site_listing_id", sa.String(128)), sa.Column("canonical_url", sa.Text), sa.Column("response_format", sa.String(16)), sa.Column("response_body", sa.Text), sa.Column("etag", sa.String(255)), sa.Column("last_modified", sa.String(255)), sa.Column("raw_hash", sa.String(64)), sa.Column("fetched_at", sa.DateTime))
    op.create_table("listing_current", sa.Column("id", sa.Integer, primary_key=True), sa.Column("site_name", sa.String(64)), sa.Column("site_listing_id", sa.String(128)), sa.Column("canonical_url", sa.Text), sa.Column("title", sa.Text), sa.Column("property_type", sa.String(64)), sa.Column("prefecture", sa.String(32)), sa.Column("city", sa.String(64)), sa.Column("town", sa.String(64)), sa.Column("address_text", sa.Text), sa.Column("access_text", sa.Text), sa.Column("lat", sa.Float), sa.Column("lon", sa.Float), sa.Column("structure", sa.String(64)), sa.Column("built_year", sa.Integer), sa.Column("built_month", sa.Integer), sa.Column("age_years", sa.Float), sa.Column("land_area_m2", sa.Float), sa.Column("building_area_m2", sa.Float), sa.Column("rentable_area_m2", sa.Float), sa.Column("floors", sa.String(32)), sa.Column("units", sa.Integer), sa.Column("occupancy_status", sa.String(64)), sa.Column("current_rent_yen", sa.Float), sa.Column("annual_rent_yen", sa.Float), sa.Column("annual_full_rent_yen", sa.Float), sa.Column("price_yen", sa.Float), sa.Column("gross_yield_pct", sa.Float), sa.Column("management_fee_yen", sa.Float), sa.Column("repair_reserve_yen", sa.Float), sa.Column("brokerage_type", sa.String(32)), sa.Column("seller_name", sa.String(128)), sa.Column("remarks", sa.Text), sa.Column("is_member_only", sa.Boolean), sa.Column("raw_hash", sa.String(64)), sa.Column("is_deleted", sa.Boolean), sa.Column("first_seen_at", sa.DateTime), sa.Column("last_seen_at", sa.DateTime), sa.Column("last_changed_at", sa.DateTime))
    for t in ["listing_history","property_master","seller_master","address_geocode","land_valuation","building_valuation","analysis_scenario","analysis_result","manual_review_queue"]:
        if t == "listing_history":
            op.create_table(t, sa.Column("id", sa.Integer, primary_key=True), sa.Column("listing_current_id", sa.Integer), sa.Column("change_type", sa.String(32)), sa.Column("changed_fields", sa.JSON), sa.Column("changed_at", sa.DateTime))
        elif t == "property_master":
            op.create_table(t, sa.Column("id", sa.Integer, primary_key=True), sa.Column("listing_current_id", sa.Integer))
        elif t == "seller_master":
            op.create_table(t, sa.Column("id", sa.Integer, primary_key=True), sa.Column("name", sa.String(128), unique=True))
        elif t == "address_geocode":
            op.create_table(t, sa.Column("id", sa.Integer, primary_key=True), sa.Column("listing_current_id", sa.Integer), sa.Column("source", sa.String(64)), sa.Column("confidence", sa.Float), sa.Column("lat", sa.Float), sa.Column("lon", sa.Float), sa.Column("status", sa.String(32)))
        elif t == "land_valuation":
            op.create_table(t, sa.Column("id", sa.Integer, primary_key=True), sa.Column("listing_current_id", sa.Integer), sa.Column("valuation_method", sa.String(32)), sa.Column("source_year", sa.Integer), sa.Column("source_url", sa.Text), sa.Column("confidence", sa.Float), sa.Column("land_value_yen", sa.Float))
        elif t == "building_valuation":
            op.create_table(t, sa.Column("id", sa.Integer, primary_key=True), sa.Column("listing_current_id", sa.Integer), sa.Column("structure", sa.String(64)), sa.Column("depreciation_factor", sa.Float), sa.Column("building_value_yen", sa.Float), sa.Column("tax_simple_remaining_life", sa.Integer), sa.Column("lender_remaining_term", sa.Integer))
        elif t == "analysis_scenario":
            op.create_table(t, sa.Column("id", sa.Integer, primary_key=True), sa.Column("name", sa.String(32)), sa.Column("params", sa.JSON))
        elif t == "analysis_result":
            op.create_table(t, sa.Column("id", sa.Integer, primary_key=True), sa.Column("listing_current_id", sa.Integer), sa.Column("scenario_name", sa.String(32)), sa.Column("metrics", sa.JSON), sa.Column("pass_fail", sa.String(8)), sa.Column("fail_reason_codes", sa.JSON))
        else:
            op.create_table(t, sa.Column("id", sa.Integer, primary_key=True), sa.Column("queue_type", sa.String(64)), sa.Column("target_id", sa.String(128)), sa.Column("reason_code", sa.String(64)), sa.Column("payload", sa.JSON), sa.Column("status", sa.String(32)), sa.Column("created_at", sa.DateTime))


def downgrade() -> None:
    for t in ["manual_review_queue","analysis_result","analysis_scenario","building_valuation","land_valuation","address_geocode","seller_master","property_master","listing_history","listing_current","listing_raw","query_plan","crawl_run"]:
        op.drop_table(t)
