from __future__ import annotations


def build_query_shards() -> list[dict[str, str]]:
    prefectures = ["東京都", "神奈川県"]
    ptypes = ["一棟アパート", "区分マンション"]
    shards: list[dict[str, str]] = []
    for pref in prefectures:
        for ptype in ptypes:
            shards.append({"prefecture": pref, "property_type": ptype, "price_band": "0-5000"})
    return shards
