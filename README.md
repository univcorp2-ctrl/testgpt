# Bitbank Auto Trader

> **注意**: ここで提供するロジックは教育用途のサンプルです。勝ちを保証するものではありません。
> 実運用時は十分な検証とリスク管理を行ってください。

## 目的
BitbankのAPIを使った自動売買の最小構成を用意し、
戦略・リスク管理・実運用の骨組みを提供します。

## 事前準備 (API)
1. BitbankでAPIキーとシークレットを発行
2. 権限は「残高参照」「注文」「取消」を有効化
3. 環境変数を設定

```bash
export BITBANK_API_KEY="your_key"
export BITBANK_API_SECRET="your_secret"
export BITBANK_PAIR="btc_jpy"
export BITBANK_TIMEFRAME="15min"
export MAX_POSITION_PCT="0.2"
export MIN_ORDER_SIZE="0.0001"
export FEE_RATE="0.0012"
export DRY_RUN="true"
```

> **API署名**: 本実装は `nonce + path + body` をHMAC-SHA256で署名します。必ずBitbankの最新仕様で確認してください。

## アーキテクチャ

```
bitbank_bot/
  cli.py            # CLI (backtest/trade)
  client.py         # Bitbank REST client (public/private)
  indicators.py     # SMA, RSI
  strategy.py       # 売買シグナル生成
  risk.py           # ポジションサイズ
  trader.py         # ライブ売買ループ
  backtest.py       # バックテスト
```

### データフロー
1. `client.py` がローソク足/資産/注文APIを呼び出し
2. `strategy.py` がMAクロス + RSIフィルタでシグナル生成
3. `risk.py` が最大ポジション比率でサイズ計算
4. `trader.py` が注文を発行 (DRY_RUN なら疑似)

### ロジック概要
- **トレンド判定**: 短期SMAと長期SMA
- **エントリー**: 上昇トレンド + RSI過熱感の解消で買い
- **イグジット**: 下降トレンド + RSI過熱感で売り
- **リスク管理**: 資産の一定割合のみ投入

## 使い方

### バックテスト
BitbankのOHLCV CSVを用意して実行:

```bash
PYTHONPATH=src python -m bitbank_bot.cli backtest path/to/ohlcv.csv
```

### ライブ売買

```bash
PYTHONPATH=src python -m bitbank_bot.cli trade --poll-seconds 900
```

## TODO
- 手数料/スリッページの精密化
- テイクプロフィット/ストップロスの追加
- 複数通貨ペアへの対応
- 指標パラメータの最適化
