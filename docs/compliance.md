# Compliance Gate

- 対象: 健美家（`TARGET_BASE_URL` は設定ファイルで指定）
- 最初に確認する項目
  - 利用規約 URL / robots.txt / 公開API / CSVエクスポート可否
  - 会員限定データ取得の可否
- 許可: 公開ページ、規約で明示的に許可される会員データ
- 禁止: CAPTCHA/MFA回避、アクセス制御回避、proxy rotation、stealth/fingerprint spoofing
- 要確認: robotsのDisallow範囲、利用規約における自動収集文言、会員コンテンツの二次利用

## Enforcement
- `COMPLIANCE_APPROVED=false` の間は `crawl-backfill` / `crawl-delta` を実行禁止。
- compliance-check は収集結果を表示し、最終承認は人手で `.env` を更新。
- グレーな機能は実装済みでも `disabled by default`。

## API / Export
- 自動判定は未確定。`manual_review_queue` で監査し、承認後に config 更新。
