from __future__ import annotations

import argparse
import csv

from .backtest import parse_candles, run_backtest
from .client import BitbankClient
from .config import load_settings
from .risk import RiskConfig
from .strategy import MovingAverageRsiStrategy
from .trader import Trader


def _load_csv(path: str) -> list[list[str]]:
    with open(path, newline="") as handle:
        reader = csv.reader(handle)
        return list(reader)


def main() -> None:
    parser = argparse.ArgumentParser(description="Bitbank trading bot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backtest_parser = subparsers.add_parser("backtest", help="Run backtest from CSV")
    backtest_parser.add_argument("csv_path", help="Path to OHLCV CSV from bitbank")

    live_parser = subparsers.add_parser("trade", help="Run live trading loop")
    live_parser.add_argument("--poll-seconds", type=int, default=60 * 15)

    args = parser.parse_args()
    settings = load_settings()

    if args.command == "backtest":
        rows = _load_csv(args.csv_path)
        candles = parse_candles(rows)
        result = run_backtest(candles)
        print(f"Final equity: {result.final_equity:,.0f} JPY")
        print(f"Trades: {result.trades}")
        print(f"Win rate: {result.win_rate:.2%}")
        return

    if args.command == "trade":
        if not settings.api_key or not settings.api_secret:
            raise SystemExit("API keys are required for live trading")
        client = BitbankClient(settings.api_key, settings.api_secret, settings.base_url)
        risk = RiskConfig(settings.max_position_pct, settings.min_order_size)
        strategy = MovingAverageRsiStrategy()
        trader = Trader(
            client=client,
            strategy=strategy,
            risk_config=risk,
            pair=settings.pair,
            timeframe=settings.timeframe,
            fee_rate=settings.fee_rate,
            dry_run=settings.dry_run,
        )
        trader.run(poll_seconds=args.poll_seconds)


if __name__ == "__main__":
    main()
