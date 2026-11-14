"""
NSE Swing Trader — Main Entry Point
-------------------------------------
Runs every morning at 9:15 AM IST via GitHub Actions.
1. Scans Nifty 50 for swing setups
2. Logs signals to paper_trades.csv
3. Sends Telegram alert to Naveen
"""

from scanner     import run_scanner
from paper_trade import log_signals, print_open_trades
from notify      import notify_signals


def main():
    print("=" * 50)
    print("  NSE Nifty 50 Swing Scanner")
    print("  Paper Trading Mode 🗒️")
    print("=" * 50)

    # Step 1 — Scan
    signals = run_scanner()

    # Step 2 — Log to CSV
    log_signals(signals)

    # Step 3 — Send Telegram alert
    notify_signals(signals)

    # Step 4 — Print open trades summary
    print("\n── Open Paper Trades ──")
    print_open_trades()

    print("\n✅ Done. Check Telegram for today's signals.")


if __name__ == "__main__":
    main()
