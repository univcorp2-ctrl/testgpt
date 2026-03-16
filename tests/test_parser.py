from app.services.parser import parse_listing


def test_parse_listing_extracts_id() -> None:
    p = parse_listing("abc", "https://x.test/detail?listing_id=123")
    assert p.site_listing_id == "123"
