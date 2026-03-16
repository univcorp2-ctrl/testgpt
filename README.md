# 健美家 収集・分析プラットフォーム (Python)

## セットアップ
1. `cp .env.example .env`
2. `.env` を更新（DB_DSN, TARGET_BASE_URL, LOGIN_URL, START_URLS, APP_ENCRYPTION_KEY）
3. `docker compose up -d postgres`
4. `pip install -e .[dev]`
5. `alembic upgrade head` または `python -m app.cli init-db`

## 実行方法
- `python -m app.cli compliance-check`
- `python -m app.cli bootstrap-login`（headfulで人手ログイン）
- `python -m app.cli crawl-backfill`
- `python -m app.cli crawl-delta`
- `python -m app.cli enrich-geocode`
- `python -m app.cli enrich-route-value`
- `python -m app.cli analyze`
- `python -m app.cli export-csv`
- `python -m app.cli doctor`
- `python -m app.cli resume`
- `PYTHONPATH=src python -m app.cli bootstrap-ai-affiliate`（AIアフィリエイト自動化の雛形生成）
- `PYTHONPATH=src python -m app.cli run-affiliate-deterministic --input-jsonl <path> --output-dir <dir>`（API未使用の機械処理パイプライン）

## 実運用注意
- `COMPLIANCE_APPROVED=true` まで crawl はロックされます。
- 平文資格情報保存なし。セッションは暗号化ファイル保存。
- 低負荷: host concurrency 1, jitter wait 5-10秒, retry/backoff。
- 不明点は `docs/assumptions.md` に明記。

## ローカル開発
- Lint: `ruff check .`
- Type check: `mypy src`
- Test: `pytest`

## .env 説明
- `DB_DSN`: PostgreSQL接続
- `APP_ENCRYPTION_KEY`: セッション暗号化キー
- `COMPLIANCE_APPROVED`: 規約レビュー後に true
