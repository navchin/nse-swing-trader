"""
Paper Trade Logger
-------------------
Logs signals to paper_trades.csv and reads open trades for evening scan.
"""

import csv
import os
from datetime import datetime

PAPER_TRADE_FILE = "paper_trades.csv"

HEADERS = [
    "date", "ticker", "entry", "stop_loss", "target",
    "risk_per_share", "reward_per_share", "rr_ratio",
    "rsi", "ema50", "ema200", "atr",
    "outcome", "exit_price", "pnl_per_share", "notes",
]


def log_signals(signals: list) -> None:
    if not signals:
        print("📋 No signals to log today.")
        return

    file_exists = os.path.exists(PAPER_TRADE_FILE)
    with open(PAPER_TRADE_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for s in signals:
            row = {
                "date":             datetime.now().strftime("%Y-%m-%d"),
                "ticker":           s["ticker"],
                "entry":            s["entry"],
                "stop_loss":        s["stop_loss"],
                "target":           s["target"],
                "risk_per_share":   s["risk"],
                "reward_per_share": s["reward"],
                "rr_ratio":         s["rr_ratio"],
                "rsi":              s["rsi"],
                "ema50":            s["ema50"],
                "ema200":           s["ema200"],
                "atr":              s["atr"],
                "outcome":          "OPEN",
                "exit_price":       "",
                "pnl_per_share":    "",
                "notes":            "",
            }
            writer.writerow(row)
            print(f"  📝 Logged: {s['ticker']} | Entry ₹{s['entry']} | Stop ₹{s['stop_loss']} | Target ₹{s['target']}")

    print(f"\n✅ {len(signals)} trade(s) logged.")


def get_open_trades() -> list:
    """Return all open trades from CSV."""
    if not os.path.exists(PAPER_TRADE_FILE):
        return []
    trades = []
    with open(PAPER_TRADE_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["outcome"] == "OPEN":
                trades.append(row)
    return trades


def print_open_trades() -> None:
    trades = get_open_trades()
    if not trades:
        print("No open paper trades.")
        return
    print(f"\n📂 Open trades ({len(trades)}):")
    print("-" * 60)
    for t in trades:
        print(f"  {t['date']} | {t['ticker']:<12} | Entry ₹{t['entry']:<8} | Stop ₹{t['stop_loss']:<8} | Target ₹{t['target']}")
    print("-" * 60)


if __name__ == "__main__":
    print_open_trades()