# Assumptions / TODO

- TARGET_BASE_URL / LOGIN_URL / START_URLS は未確定のため config placeholder を採用。
- 利用規約とrobotsの最終判断は法務/運用担当がレビューして `COMPLIANCE_APPROVED=true` を設定。
- TODO: 健美家専用HTML parserの精度向上。
  - 理由: 実ドメイン非指定のため汎用パーサーで実装。
  - Unblock条件: 実HTMLサンプルと許可範囲の確定。
- TODO: official_nta_import のETL本体（路線価図/倍率表/補正率）
  - 理由: データソース仕様確定が必要。
  - Unblock条件: 参照元ファイル仕様・更新頻度確定。
