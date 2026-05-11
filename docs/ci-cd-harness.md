# CI/CDハーネス設計メモ

このリポジトリに入れるハーネスの目的は、ChatGPTやCodex/Claude Code/Gemini CLIなどで作ったコードを、GitHubに上げた瞬間に自動チェックし、壊れていないことを確認し、必要ならデプロイまで進めることです。

## 全体像

```text
ChatGPTで要件定義/サンプル作成
  ↓
GitHubへpush / PR作成
  ↓
GitHub Actionsが自動起動
  ↓
Lint / 型チェック / セキュリティ / テスト / ビルド
  ↓
ArtifactsとJob Summaryに結果を保存
  ↓
PR上で合否確認
  ↓
mainへmerge
  ↓
必要ならVercel/Netlify/Cloudflare Pages/Render等へデプロイ
  ↓
URL・ログ・成果物を確認
```

## 最初に使うべき構成

初心者が最初に使うなら、まずはGitHub Actions中心でよいです。

理由:

- GitHubに標準で入っている
- YAMLを置くだけで動く
- Actionsログ、Job Summary、Artifactsで結果確認できる
- PR単位でテスト失敗を見られる
- 追加ツールにログインしなくても最初の品質チェックが回る

## 入れているチェック

### Pythonがある場合

- `ruff check .`
- `mypy .` は最初は警告扱い
- `bandit` は最初は警告扱い
- `pip-audit` は最初は警告扱い
- `pytest -q --maxfail=1`

### Node.jsがある場合

- `npm ci` または `npm install`
- `npm run lint --if-present`
- `npm run typecheck --if-present`
- `npm test --if-present`
- `npm run build --if-present`
- `dist` / `build` / `.next` があればArtifact保存

## 自動デプロイの考え方

デプロイは最初から無理に全サービス対応にしない方が安全です。

おすすめ順:

1. 静的サイト/フロント: Vercel, Netlify, Cloudflare Pages
2. Python/API/常駐アプリ: Render, Fly.io, Railway
3. 本格運用: AWS/GCP/Azure + OIDC

## 結果の戻し方

ChatGPT通常アプリのこのチャットへ、外部CI/CDから直接自動返信する標準機能はありません。

現実的な戻し先は次の順番です。

1. GitHub ActionsのJob Summary
2. PRコメント
3. ArtifactとしてMarkdown/Excel/HTMLログ保存
4. Slack/Discord/メール通知
5. OpenAI APIや別エージェントを使って要約し、GitHub Issue/PRに投稿

## 重要な運用ルール

- mainへ直pushしない
- 必ずPRでCIを走らせる
- 最初はセキュリティ系チェックを警告扱いにする
- 安定してから必須チェックに昇格する
- 秘密情報はGitHub Secretsへ入れる
- クラウドへのデプロイは長期キーよりOIDCを優先する
- 同時実行で無駄課金しないように`concurrency`を入れる
