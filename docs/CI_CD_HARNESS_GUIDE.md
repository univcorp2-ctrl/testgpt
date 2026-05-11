# CI/CDハーネス設計ガイド

このリポジトリに入れたハーネスは、開発後に毎回同じ品質チェックを自動で通すための最小構成です。

## 目的

ChatGPTやCodex/Claude/Geminiで作ったコードをGitHubにアップロードした後、以下を自動化します。

1. GitHubにpushまたはPull Request作成
2. GitHub Actionsが自動起動
3. Python/Node.jsの有無を自動判定
4. Lint、型チェック、セキュリティチェック、テスト、ビルドを実行
5. 成果物があればArtifactsに保存
6. 結果をActionsのSummaryで確認
7. 必要ならVercel/Netlify/Cloudflare Pages/Renderへデプロイ

## 入れたファイル

- `.github/workflows/ci.yml`
  - 自動テスト・品質チェック用
- `.github/workflows/deploy-cloudflare-pages.yml`
  - Cloudflare Pagesへ手動またはmain pushでデプロイする雛形
- `.github/workflows/dependency-review.yml`
  - PRで依存関係の脆弱性・ライセンス問題を確認する雛形
- `.github/dependabot.yml`
  - GitHub Actions / npm / pip の依存更新を自動提案する雛形

## まず見る場所

GitHubのリポジトリ画面で以下を確認します。

1. Actionsタブ
2. CI - test, quality, artifact
3. 最新のWorkflow Run
4. Summary
5. 失敗した場合は該当Jobのログ

## CIで行うチェック

### Pythonがある場合

- `ruff check .`
- `mypy .`
- `bandit -r .`
- `pip-audit`
- `pytest -q --maxfail=1`

`mypy`、`bandit`、`pip-audit`は最初は止まりすぎないように一部 `|| true` にしています。運用が安定したら厳格化してください。

### Node.jsがある場合

`package.json`内にスクリプトがあれば以下を実行します。

- `npm run lint --if-present`
- `npm run typecheck --if-present`
- `npm test --if-present`
- `npm run build --if-present`

## デプロイまで完全自動化する考え方

一番簡単なのは、GitHub Actionsでテストを通してからデプロイする流れです。

```text
ChatGPTで仕様整理
  ↓
コード生成
  ↓
GitHubへpush / PR作成
  ↓
GitHub Actions CI
  ↓
テスト成功
  ↓
デプロイJob
  ↓
本番/プレビューURL発行
  ↓
Actions Summary / PRコメントで結果確認
```

## おすすめの無料・低コスト構成

### 静的サイト・軽いWebアプリ

優先順位は以下です。

1. Cloudflare Pages
2. Netlify
3. Vercel
4. GitHub Pages

### APIサーバーや常駐処理

1. Render
2. Railway
3. Fly.io
4. Google Cloud Run

完全無料に近い運用を狙うなら、まずは静的サイト化してCloudflare PagesかNetlifyに寄せるのが安定です。

## Cloudflare Pagesへデプロイする場合

GitHubのSecretsに以下を登録します。

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_PAGES_PROJECT`

GitHub画面での設定場所:

```text
Repository → Settings → Secrets and variables → Actions → New repository secret
```

ビルド成果物の場所はプロジェクトに合わせて変えます。

- Vite/React/Astro: `dist`
- Next.js static export: `out`
- Docusaurus: `build`
- MkDocs: `site`

`deploy-cloudflare-pages.yml` の `DEPLOY_DIR` を変更してください。

## Vercelへデプロイする場合

VercelはGitHub連携だけでPreview/Productionを自動生成できます。GitHub Actionsで制御したい場合は以下のSecretsを使います。

- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

基本コマンド例:

```bash
npm i -g vercel@latest
vercel pull --yes --environment=preview --token=$VERCEL_TOKEN
vercel build --token=$VERCEL_TOKEN
vercel deploy --prebuilt --token=$VERCEL_TOKEN
```

## Netlifyへデプロイする場合

NetlifyもGitHub連携だけで自動デプロイできます。GitHub Actionsで制御する場合は以下のSecretsを使います。

- `NETLIFY_AUTH_TOKEN`
- `NETLIFY_SITE_ID`

基本コマンド例:

```bash
npm install -g netlify-cli
netlify deploy --dir=dist --site=$NETLIFY_SITE_ID --auth=$NETLIFY_AUTH_TOKEN
netlify deploy --prod --dir=dist --site=$NETLIFY_SITE_ID --auth=$NETLIFY_AUTH_TOKEN
```

## Renderへデプロイする場合

RenderはGitHubリポジトリとブランチを連携すると、mainへmerge/pushされたタイミングで自動デプロイできます。`render.yaml`を置くと、サービス構成をコード管理できます。

## ChatGPTへ結果を戻す方法

ChatGPTアプリの通常チャットに外部CI結果を直接自動投稿する標準機能はありません。現実的には次のどれかです。

1. GitHub ActionsのSummaryを見る
2. PRコメントにCI結果を自動投稿する
3. ArtifactをダウンロードしてChatGPTに貼る/アップロードする
4. Codex/Claude Code/Gemini CLIなどの外部CLIからGitHub APIを読ませる
5. OpenAI APIやWebhookを使って別チャット/通知先へ送る

最初は `Actions Summary + PRコメント + Artifacts` で十分です。

## 初心者向けの運用ルール

- mainに直pushしない
- 必ずPRを作る
- PRでCIが全部通ってからmerge
- デプロイはmain merge後だけにする
- APIキーやパスワードはGitHub Secretsに入れる
- `.env` は絶対にcommitしない
- 失敗したらActionsログの赤いステップだけを見る
- エラー全文をChatGPTに貼って修正案を出させる

## 失敗時の見る順番

1. Actionsタブで失敗Workflowを開く
2. 赤いJobを開く
3. 赤いStepを開く
4. エラーメッセージをコピー
5. ChatGPTに以下の形で投げる

```text
このGitHub Actionsエラーを直して。
リポジトリ構成:
- Python/Node.jsなど
- 実行したworkflow名

エラー:
ここにログを貼る

期待すること:
CIを通して、必要ならテストも修正してほしい。
```

## 次に厳格化するポイント

最初は通すことを優先し、徐々に厳しくします。

1. `mypy . || true` を `mypy .` に変える
2. `bandit` を必須化する
3. `pip-audit` / `npm audit` を必須化する
4. Playwright/CypressでE2Eテストを追加する
5. branch protectionでCI成功をmerge条件にする
6. deployment environmentに承認ステップを入れる

## 最終形

```text
要件定義
  ↓
コード作成
  ↓
GitHub PR
  ↓
CI: lint / typecheck / unit test / security / build
  ↓
Preview deploy
  ↓
E2E test
  ↓
PR Summary / Artifact確認
  ↓
merge
  ↓
Production deploy
  ↓
本番URL・ログ・結果を確認
```
