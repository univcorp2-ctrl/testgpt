# LINE 物件情報 日次配信 API

LINEグループ向けに、毎日指定時刻で物件情報を自動投稿するAPIです。安定運用のために以下を実装しています。

- LINE Webhook署名検証
- groupId自動収集 + DB保存
- 日次ジョブの冪等制御 (`lastSentDate`)
- LINE Push APIの `X-Line-Retry-Key` 付与
- AI失敗時のテンプレート送信フォールバック
- 構造化ログ（LINE request-id, status, retry回数）

## ディレクトリ構成

```txt
apps/api
  ├─ src/
  │  ├─ index.ts
  │  ├─ routes/webhook.ts
  │  ├─ routes/jobs.ts
  │  ├─ routes/settings.ts
  │  ├─ line/client.ts
  │  ├─ line/signature.ts
  │  ├─ content/propertySource.ts
  │  ├─ content/googleSheetsSource.ts
  │  ├─ generate/messageGenerator.ts
  │  ├─ store/store.ts
  │  ├─ store/firestoreStore.ts
  │  └─ util/validation.ts
  ├─ tests/
  ├─ data/properties.json
  ├─ public/index.html
  ├─ README_SETUP.md
  └─ Dockerfile
```

## 環境変数

```bash
PORT=8080
LOG_LEVEL=info
SERVICE_TIMEZONE=Asia/Tokyo

LINE_CHANNEL_ACCESS_TOKEN=LINE_ACCESS_TOKEN_DUMMY
LINE_CHANNEL_SECRET=LINE_SECRET_DUMMY

OPENAI_API_KEY=OPENAI_API_KEY_DUMMY
OPENAI_MODEL=gpt-4o-mini

USE_FIRESTORE=true
GOOGLE_CLOUD_PROJECT=my-project

PROPERTY_SOURCE=sheets # or json
PROPERTY_JSON_PATH=./data/properties.json

GOOGLE_SHEETS_SPREADSHEET_ID=spreadsheet_id
GOOGLE_SHEETS_RANGE=properties!A:F
GOOGLE_SERVICE_ACCOUNT_EMAIL=svc-account@my-project.iam.gserviceaccount.com
GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

## セットアップ

詳細な初期設定は `README_SETUP.md` を参照してください。

```bash
cd apps/api
npm install
npm run dev
```

### テスト

```bash
npm test
```


## 操作設定Web UI

- URL: `GET /ui`
- 設定API: `GET/PUT /api/settings`
- 変更可能項目: `timezone`, `dailyTime`, `propertySource`
- 登録済みのLINE groupId一覧と `lastSentDate` を確認可能

## LINE Developers側で必要な設定

1. **Messaging APIチャネルを作成**
2. **チャネルアクセストークン（長期）を発行**し `LINE_CHANNEL_ACCESS_TOKEN` に設定
3. **チャネルシークレット**を `LINE_CHANNEL_SECRET` に設定
4. **Webhook URL** を設定
   - 例: `https://<your-domain>/webhook/line`
   - 検証時は ngrok を利用: `https://xxxx.ngrok-free.app/webhook/line`
5. **Webhookを有効化**
6. **Botを対象グループへ招待**
   - joinイベントまたはmessageイベントで `groupId` がDB保存される

## ngrokでWebhook検証（ローカル）

```bash
# 1) API起動
cd apps/api
npm run dev

# 2) 別ターミナルでngrok
ngrok http 8080

# 3) 発行されたURLをLINE DevelopersのWebhook URLに設定
# 例: https://xxxx.ngrok-free.app/webhook/line
```

## 日次スケジューラ設定

### Cloud Run + Cloud Scheduler の例

1. Cloud Runへデプロイ（`/jobs/daily` が到達可能なURL）
2. Cloud SchedulerでHTTPジョブ作成
   - URL: `https://<cloud-run-url>/jobs/daily`
   - Method: `POST`
   - Cron例: `0 9 * * *` (JST 09:00)
   - 認証: OIDCまたは適切な認証ヘッダ

### AWS Lambda / EventBridgeの場合

- EventBridgeのcronから API Gateway 経由で `/jobs/daily` を POST

## Google Sheetsフォーマット

1行目ヘッダ、2行目以降データ:

| A(title) | B(price) | C(area) | D(stationMinutes) | E(url) | F(notes) |
|---|---|---|---|---|---|

## API仕様

### POST `/webhook/line`

- `x-line-signature` を HMAC-SHA256 + Base64 で検証
- join/messageイベントから `source.groupId` を抽出してupsert
- レスポンスは即時 `200`
- DB更新は `setImmediate` で非同期処理

### POST `/jobs/daily`

- 各groupについて `lastSentDate` で冪等チェック
- 物件ソース（Sheets/JSON）を取得
- AIで文面生成（JSON）
- 生成失敗またはバリデーション失敗時はテンプレートで送信
- LINE push送信 (`X-Line-Retry-Key`付き)
- 送信履歴保存

