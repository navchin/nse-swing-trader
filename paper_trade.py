"""
Paper Trade Logger
-------------------
Logs every BUY signal to paper_trades.csv
Tracks: entry, stop-loss, target, outcome (open/hit target/stopped out)
You update the 'outcome' column manually in the CSV after each trade resolves.
"""

import csv
import os
from datetime import datetime

PAPER_TRADE_FILE = "paper_trades.csv"

HEADERS = [
    "date",
    "ticker",
    "cmp",
    "entry",
    "stop_loss",
    "target",
    "risk_per_share",
    "reward_per_share",
    "rr_ratio",
    "rsi",
    "ema50",
    "ema200",
    "atr",
    "outcome",        # You fill this: OPEN / TARGET HIT / STOPPED OUT
    "exit_price",     # You fill this when trade closes
    "pnl_per_share",  # You fill this: exit_price - entry
    "notes",
]


def log_signals(signals: list[dict]) -> None:
    """Append new signals to the paper trades CSV."""
    if not signals:
        print("📋 No signals to log today.")
        return

    file_exists = os.path.exists(PAPER_TRADE_FILE)

    with open(PAPER_TRADE_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, extrasaction="ignore")

        if not file_exists:
            writer.writeheader()
            print(f"📋 Created new paper trade journal: {PAPER_TRADE_FILE}")

        for s in signals:
            row = {
                "date":            datetime.now().strftime("%Y-%m-%d"),
                "ticker":          s["ticker"],
                "cmp":             s["cmp"],
                "entry":           s["entry"],
                "stop_loss":       s["stop_loss"],
                "target":          s["target"],
                "risk_per_share":  s["risk"],
                "reward_per_share": s["reward"],
                "rr_ratio":        s["rr_ratio"],
                "rsi":             s["rsi"],
                "ema50":           s["ema50"],
                "ema200":          s["ema200"],
                "atr":             s["atr"],
                "outcome":         "OPEN",
                "exit_price":      "",
                "pnl_per_share":   "",
                "notes":           "",
            }
            writer.writerow(row)
            print(f"  📝 Logged: {s['ticker']} | Entry ₹{s['entry']} | Stop ₹{s['stop_loss']} | Target ₹{s['target']}")

    print(f"\n✅ {len(signals)} trade(s) logged to {PAPER_TRADE_FILE}")


def print_open_trades() -> None:
    """Print all currently open paper trades."""
    if not os.path.exists(PAPER_TRADE_FILE):
        print("No paper trades file found.")
        return

    open_trades = []
    with open(PAPER_TRADE_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["outcome"] == "OPEN":
                open_trades.append(row)

    if not open_trades:
        print("No open paper trades.")
        return

    print(f"\n📂 Open paper trades ({len(open_trades)}):")
    print("-" * 70)
    for t in open_trades:
        print(
            f"  {t['date']} | {t['ticker']:<12} | "
            f"Entry ₹{t['entry']:<8} | "
            f"Stop ₹{t['stop_loss']:<8} | "
            f"Target ₹{t['target']:<8} | "
            f"R:R {t['rr_ratio']}"
        )
    print("-" * 70)


if __name__ == "__main__":
    print_open_trades()
