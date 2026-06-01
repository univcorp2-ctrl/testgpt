# 画像生成プロンプト集

このリポジトリの初期設定ガイダンス画像を作る場合は、利用環境で使える最新の GPT Image / ChatGPT Images モデルを使います。APIで `gpt-image-2` が利用可能な環境では `gpt-image-2` を優先してください。

## README冒頭用まとめ画像

```text
日本語UI風のGitHubリポジトリ初期設定ガイド画像。横長16:9。タイトルは「README 画像付き初期設定ガイド」。5つの番号付きパネルを入れる: 1 READMEを見る、2 Secrets設定、3 GitHub Actions実行、4 Artifact/成果物ダウンロード、5 エラー時のログ確認。初心者向けに赤枠、矢印、短い説明ラベルを使う。Secret値は絶対に表示せず、******** または YOUR_SECRET_HERE と表示する。クリーンで見やすいフラットデザイン。
```

## GitHub Secrets設定画面

```text
GitHubのSettings → Secrets and variables → ActionsでNew repository secretを追加する初心者向け手順画像。日本語ラベル、赤枠、番号付き。Secret名は EXAMPLE_SECRET、値は ******** として実値を見せない。
```

## GitHub Actions手動実行画面

```text
GitHub Actionsタブでworkflowを選び、Run workflowを押す手順の画像。日本語UI風。赤枠と番号付き。初心者でも迷わないように3ステップで表示する。
```

## Artifactダウンロード画面

```text
GitHub Actionsの実行結果画面でArtifacts欄からCSV、Excel、TXTなどの成果物をダウンロードする手順画像。日本語ラベル、赤枠、番号付き。ファイル名例は property-ocr-outputs.zip。
```

## エラーログ確認画面

```text
GitHub Actionsで失敗したジョブを開き、赤い失敗ステップとログを確認する初心者向け画像。認証エラー、Secret名ミス、権限不足の確認ポイントを短く表示。Secret値は表示しない。
```
