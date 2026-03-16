# Architecture

```text
[CLI/Typer]
  -> Compliance Gate
  -> Crawl (backfill/delta, checkpoint)
  -> Raw Store (listing_raw)
  -> Normalize (listing_current/history)
  -> Enrich (geocode, route value)
  -> Analyze (scenario KPI)
  -> Export CSV
```

- データフロー: `raw -> normalized -> enriched -> analyzed`
- Backfill: query partitioner で shard を作って一括収集
- Delta: 既存URL再取得 + ETag/Last-Modified + content hash で差分取得
- Manual review queue:
  - geocode 低精度
  - route value の情報不足
  - 価格/利回り/タイトル等の重要変更
- Query partitioner:
  - prefecture/city/property_type/price帯/築年/利回り帯を基準に shard 化
  - shard単位で再開可能
