"""
NSE Swing Trader — Main Entry Point
-------------------------------------
Morning scan (9:15 AM IST): finds new BUY signals in Nifty 50
Evening scan (3:15 PM IST): checks open trades, reports if target/stop hit
"""

import os
from scanner     import run_scanner
from paper_trade import log_signals, print_open_trades, get_open_trades
from notify      import notify_signals, notify_evening_summary


def morning_scan():
    print("=" * 50)
    print("  🌅 MORNING SCAN — 9:15 AM IST")
    print("  Scanning Nifty 50 for swing setups...")
    print("=" * 50)

    signals = run_scanner()
    log_signals(signals)
    notify_signals(signals)
    print_open_trades()
    print("\n✅ Morning scan done. Check Telegram.")


def evening_scan():
    print("=" * 50)
    print("  🌆 EVENING SCAN — 3:15 PM IST")
    print("  Checking open trades...")
    print("=" * 50)

    open_trades = get_open_trades()
    notify_evening_summary(open_trades)
    print("\n✅ Evening scan done. Check Telegram.")


def main():
    scan_type = os.environ.get("SCAN_TYPE", "morning").lower()

    if scan_type == "evening":
        evening_scan()
    else:
        morning_scan()


if __name__ == "__main__":
    main()