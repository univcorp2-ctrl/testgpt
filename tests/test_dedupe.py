from app.services.dedupe import dedupe_key
from app.services.parser import ParsedListing


def test_dedupe_prefers_id() -> None:
    k = dedupe_key(ParsedListing("A", "u", None, None, None))
    assert k == "id:A"
