# GeminiDailyAggregator (Windows / API追加課金ゼロ構成)

Gemini CLI（Googleログイン方式）と、手動保存したファイル（md/txt/html/json/csv）を集約して、
**Markdown / Excel / SQLite** に保存するローカル運用ツールです。

> 重要: この構成は **Gemini APIキー・Google APIキー・Vertex AI・OpenAI API・外部有料APIを使いません**。

---

## 1. 前提

- OS: Windows 10/11
- 作業フォルダ: `C:\AI_Agents\GeminiDailyAggregator`
- 実行場所はローカル（Cドライブ）
- 必要なら成果物のみ後でGoogle Driveへコピー

---

## 2. フォルダ構成

```text
C:\AI_Agents\GeminiDailyAggregator
├─ inbox
│  ├─ manual_paste
│  ├─ gemini_chat_exports
│  └─ raw
├─ reports
├─ data
├─ scripts
└─ prompts
```

---

## 3. 初回セットアップ

PowerShell:

```powershell
cd C:\AI_Agents\GeminiDailyAggregator
.\scripts\setup.ps1
```

`setup.ps1` で実施する内容:
- 必要フォルダ作成
- Pythonライブラリ導入（pandas / openpyxl / beautifulsoup4 / pyyaml）
- Gemini CLI存在確認
- `GEMINI_API_KEY` / `GOOGLE_API_KEY` が設定済みなら警告

---

## 4. Gemini CLIログイン（APIキー方式は使わない）

初回のみ:

```powershell
gemini
```

ブラウザで **Sign in with Google** を選択してログインしてください。

環境変数を消したい場合（任意）:

```powershell
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $null, "User")
[Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", $null, "User")
```

---

## 5. 入力データの置き場所

- 手動コピー: `inbox\manual_paste`
- Geminiチャットのエクスポート/Takeout: `inbox\gemini_chat_exports`
- その他の生データ: `inbox\raw`

対応拡張子: `.md .txt .html .json .csv`

HTMLは自動でテキスト化します。

---

## 6. 実行方法

```powershell
cd C:\AI_Agents\GeminiDailyAggregator
.\scripts\run_daily.ps1
```

実行内容:
1. `inbox` 配下のファイルを収集
2. SHA256で重複判定
3. Gemini CLI（`gemini -p`）に投入してJSON配列化
4. SQLiteに保存（`raw_documents`, `insights`）
5. 日次レポート出力

出力:
- `reports\daily_summary_YYYY-MM-DD.md`
- `reports\daily_summary_YYYY-MM-DD.xlsx`
- `reports\important_actions.md`
- 失敗時: `reports\error_YYYY-MM-DD.log`
- DB: `data\aggregator.sqlite`

---

## 7. スケジューラ登録（例: 毎日8時）

```powershell
schtasks /Create /TN "GeminiDailyAggregator_0800" /TR "powershell.exe -ExecutionPolicy Bypass -File C:\AI_Agents\GeminiDailyAggregator\scripts\run_daily.ps1" /SC DAILY /ST 08:00 /F
```

必要なら12:00/18:00も追加してください。

---

## 8. トラブルシュート

- `gemini` コマンドがない
  - `npm install -g @google/gemini-cli` を実行
- JSONパースエラーが出る
  - `reports\error_YYYY-MM-DD.log` に生出力が保存されるので確認
- Excelが空
  - 当日データがない可能性あり。`insights` テーブルを確認
- Google Driveに同期したい
  - `config.yaml` の `sync.enabled: true` と `google_drive_reports_dir` を設定

---

## 9. 今回あえて入れていないもの

- Playwrightなどのブラウザ自動操作
- Composio/Gmail/Driveの外部連携

まずは **Gemini CLI + 手動保存ファイル + ローカル集約** の安定運用を優先しています。
