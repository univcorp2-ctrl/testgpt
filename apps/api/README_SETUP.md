# 初期設定ガイド（運用開始まで）

このドキュメントは「最初の1回だけ」必要な設定をまとめたものです。

## 1. LINE Developers設定

1. Messaging APIチャネルを作成
2. チャネルアクセストークン（長期）を発行し `LINE_CHANNEL_ACCESS_TOKEN` に設定
3. チャネルシークレットを `LINE_CHANNEL_SECRET` に設定
4. Webhook URLを `https://<domain>/webhook/line` へ設定し有効化
5. Botを対象グループへ招待（join/messageイベントで `groupId` が保存される）

## 2. GCP / Firestore 設定（推奨）

1. Firestore有効化
2. Cloud Run実行サービスアカウントへ Firestore 権限付与
3. `USE_FIRESTORE=true` を設定

## 3. 物件データ連携

- Google Sheets利用時
  - `PROPERTY_SOURCE=sheets`
  - `GOOGLE_SHEETS_SPREADSHEET_ID`, `GOOGLE_SHEETS_RANGE`
  - `GOOGLE_SERVICE_ACCOUNT_EMAIL`, `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY`
- JSON代替時
  - `PROPERTY_SOURCE=json`
  - `PROPERTY_JSON_PATH=./data/properties.json`

## 4. AI設定（任意だが推奨）

- `OPENAI_API_KEY` を設定
- 未設定時や生成失敗時はテンプレート文に自動フォールバック

## 5. Web UIで運用設定

起動後 `GET /ui` へアクセスし、以下を更新可能です。
- timezone
- dailyTime
- propertySource
- 登録済みgroupId一覧の確認

## 6. スケジューラ設定

Cloud Scheduler / EventBridge から `POST /jobs/daily` を1日1回呼び出してください。
