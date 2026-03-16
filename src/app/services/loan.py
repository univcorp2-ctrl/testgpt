from __future__ import annotations

from math import floor


def tax_simple_remaining_life(statutory_life: int, elapsed_years: int) -> int:
    if elapsed_years >= statutory_life:
        return max(floor(statutory_life * 0.2), 2)
    return max(floor((statutory_life - elapsed_years) + elapsed_years * 0.2), 2)
