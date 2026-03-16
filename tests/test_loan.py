from app.services.loan import tax_simple_remaining_life


def test_remaining_life_rule() -> None:
    assert tax_simple_remaining_life(47, 50) >= 2
    assert tax_simple_remaining_life(47, 10) > 2
