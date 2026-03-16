# Codexデスクトップ向け最短スタート（API未使用）

## 目的
最初は外部APIを叩かず、機械的に処理できるところだけ先に固めます。

## 手順
1. 入力データを作る（`data/sample_sources.jsonl` をコピーして編集）
2. 以下コマンドを実行する

```bash
PYTHONPATH=src python -m app.cli run-affiliate-deterministic \
  --input-jsonl ai_affiliate_automation/data/sample_sources.jsonl \
  --output-dir ai_affiliate_automation/runs
```

3. 出力される2ファイルを確認
- `normalized_*.jsonl`（URL正規化・重複排除・商材タグ付け済み）
- `content_specs_*.jsonl`（記事/LP生成前の機械的ブリーフ）

## この段階でできること
- URL正規化
- 重複排除
- 商材タグ判定（辞書ベース）
- リスクフラグ検出（誇張語など）
- CTA初期割当

## まだやらないこと
- LLM生成
- CMS投稿
- 配信API連携
