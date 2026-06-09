# LINEチャンネル情報取得の設計メモ

## 目的
LINE上の特定チャンネル（グループ/ルーム/ユーザー）に投稿される情報を受け取り、
テキスト本文とハイパーリンクを抽出して保存・検索できるようにする。

## 前提と制約
- LINEは**既存の会話履歴をAPIで取得**できないため、Bot（Messaging API）を対象のチャンネルに参加させ、
  **Webhookで新規メッセージを受信**する方式が現実的。
- 公式の取得対象は、
  - グループ/ルーム/ユーザー（Botに届くイベント）
  - テキストメッセージ（画像やファイルは今回は除外）
- Botが参加していないチャンネルの情報は取得できない。

## 全体構成
1. **LINE公式アカウント + Messaging API** を作成
2. Webhook受信サーバー（`line_webhook_server.py`）を公開
3. 受信したテキストをSQLiteに保存（`line_storage.py`）
4. 保存データをCLIで検索・抽出（`line_cli.py`）

```
LINE (Group/Room/User)
  -> Webhook (POST /callback)
     -> line_webhook_server.py
        -> line_storage.py (SQLite)
           -> line_cli.py (検索/抽出)
```

## データ設計
`messages` テーブルで保存する情報
- `source_type`: group / room / user
- `source_id`: groupId / roomId / userId
- `message_id`: LINEのmessageId
- `text`: テキスト本文
- `links`: 正規表現で抽出したURL配列（JSON）
- `timestamp_ms`: イベントのtimestamp
- `received_at`: サーバー受信時刻
- `raw_event`: 受信したイベント全体のJSON

## セキュリティ
- LINEから送信される`X-Line-Signature`を`channel_secret`で検証。
- `LINE_CHANNEL_SECRET`が無い場合は検証できないため、
  サンプル運用として警告ログを出しつつ受信する。

## 運用の流れ
1. LINE Developer Consoleでチャネル作成・Webhook URL設定。
2. `LINE_CHANNEL_SECRET` を環境変数に設定。
3. `python line_webhook_server.py`でWebhook受信を開始。
4. Botを対象グループ/ルームに招待。
5. `python line_cli.py list-sources` や `fetch` で保存済みデータを取得。

## 事前設定ガイダンス（どのように準備するか）
### 1. LINE Developer Consoleの準備
- Providersを作成し、Messaging APIチャネルを新規作成する。
- 「Messaging API設定」から**Webhook送信**を有効化する。
- チャネルシークレット（`LINE_CHANNEL_SECRET`）を控える。

### 2. Webhook受信先の準備
- 外部からHTTPSで到達可能なURLを用意する（例: `https://example.com/callback`）。
- 本リポジトリの`line_webhook_server.py`を動作させるサーバーを準備する。
- ローカル検証ではngrok等でトンネルを張り、URLをWebhookに設定する。

### 3. 環境変数の設定
```bash
export LINE_CHANNEL_SECRET="your-channel-secret"
export LINE_DB_PATH="line_messages.sqlite3"  # 任意
```

### 4. Webhookサーバー起動
```bash
python line_webhook_server.py
```

### 5. チャンネル（グループ/ルーム）への参加
- 対象のグループ/ルームにBotを招待する。
- Botが参加したチャンネルで送信されたテキストがWebhookに届く。

### 6. 取得データの確認（CLI）
```bash
python line_cli.py list-sources
python line_cli.py fetch --source-type group --source-id <groupId> --limit 20
```

## 拡張案
- 画像/ファイルのメタ情報取得
- 受信メッセージのタグ付け
- PostgreSQLやクラウドストレージへの移行
