"""
Telegram Notifier — Morning + Evening
"""

import os
import requests
from datetime import datetime


def send_telegram(message: str) -> bool:
    token   = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("⚠️  Telegram credentials not set.")
        return False
    url  = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            print("✅ Telegram sent.")
            return True
        print(f"❌ Telegram error: {resp.status_code}")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def notify_signals(signals: list) -> None:
    """Morning — new BUY signals."""
    today = datetime.now().strftime("%d %b %Y")

    if not signals:
        msg = (
            f"🌅 <b>Morning Scan — {today}</b>\n\n"
            f"🔍 Nifty 50 scanned. No swing setups today.\n\n"
            f"<i>No signal = stay out. Check again tomorrow.</i>"
        )
    else:
        lines = [
            f"🌅 <b>Morning Scan — {today}</b>\n",
            f"✅ <b>{len(signals)} swing setup(s) found</b>\n",
            "─" * 28,
        ]
        for i, s in enumerate(signals, 1):
            lines.append(
                f"\n<b>{i}. {s['ticker']}</b> 📈\n"
                f"   Entry:     ₹{s['entry']}\n"
                f"   Stop-loss: ₹{s['stop_loss']}  (risk ₹{s['risk']}/share)\n"
                f"   Target:    ₹{s['target']}  (reward ₹{s['reward']}/share)\n"
                f"   R:R: 1:{s['rr_ratio']}  |  RSI: {s['rsi']}\n"
            )
        lines.append("\n⚠️ <i>Paper trade only. Log it on your dashboard.</i>")
        msg = "\n".join(lines)

    print("\n── Morning Telegram ──")
    print(msg)
    send_telegram(msg)


def notify_evening_summary(open_trades: list) -> None:
    """Evening — summary of open trades."""
    today = datetime.now().strftime("%d %b %Y")

    if not open_trades:
        msg = (
            f"🌆 <b>Evening Summary — {today}</b>\n\n"
            f"📭 No open paper trades to track.\n\n"
            f"<i>Add signals from tomorrow's morning scan.</i>"
        )
    else:
        lines = [
            f"🌆 <b>Evening Summary — {today}</b>\n",
            f"📂 <b>{len(open_trades)} open trade(s) to watch:</b>\n",
            "─" * 28,
        ]
        for t in open_trades:
            lines.append(
                f"\n<b>{t['ticker']}</b>\n"
                f"   Entry:  ₹{t['entry']}  (since {t['date']})\n"
                f"   Stop:   ₹{t['stop_loss']}  ← exit if hits this\n"
                f"   Target: ₹{t['target']}  ← book profit here\n"
            )
        lines.append(
            "\n💡 <i>GTT order set on Zerodha?\n"
            "If yes — Zerodha handles exit automatically.\n"
            "If no — keep an eye on these tomorrow morning.</i>"
        )
        msg = "\n".join(lines)

    print("\n── Evening Telegram ──")
    print(msg)
    send_telegram(msg)


if __name__ == "__main__":
    # Test
    notify_signals([])
    notify_evening_summary([{
        "ticker": "SWASTIKAIN", "entry": "193",
        "stop_loss": "178", "target": "225", "date": "2026-11-14"
    }])