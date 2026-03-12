from app.adapters.route_value import OfficialNTAAdapter


def test_simple_route_value() -> None:
    res = OfficialNTAAdapter().evaluate(route_value_per_m2=1000, land_area_m2=50)
    assert res.method == "simple"
    assert res.land_value_yen == 50000
