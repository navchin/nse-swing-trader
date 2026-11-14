"""
Telegram Notifier
------------------
Sends swing trade signals to your Telegram chat.
Requires two GitHub Secrets:
  TELEGRAM_BOT_TOKEN  — from @BotFather
  TELEGRAM_CHAT_ID    — your personal chat ID
"""

import os
import requests
from datetime import datetime


def send_telegram(message: str) -> bool:
    """Send a message via Telegram Bot API."""
    token   = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("⚠️  Telegram credentials not set. Skipping notification.")
        print("    Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as GitHub Secrets.")
        return False

    url  = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id":    chat_id,
        "text":       message,
        "parse_mode": "HTML",
    }

    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200:
            print("✅ Telegram alert sent successfully.")
            return True
        else:
            print(f"❌ Telegram error: {resp.status_code} — {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Telegram exception: {e}")
        return False


def format_signal_message(signals: list[dict]) -> str:
    """Format signals into a clean Telegram message."""
    today = datetime.now().strftime("%d %b %Y")

    if not signals:
        return (
            f"📊 <b>NSE Swing Scanner — {today}</b>\n\n"
            f"🔍 Nifty 50 scanned. No swing setups found today.\n\n"
            f"<i>Market may be trending strongly or in choppy range. "
            f"Best to stay out on days with no signal.</i>"
        )

    lines = [f"📊 <b>NSE Swing Scanner — {today}</b>\n"]
    lines.append(f"✅ <b>{len(signals)} swing setup(s) found in Nifty 50</b>\n")
    lines.append("─" * 30)

    for i, s in enumerate(signals, 1):
        lines.append(
            f"\n<b>{i}. {s['ticker']}</b> 📈\n"
            f"   CMP:        ₹{s['cmp']}\n"
            f"   Entry:      ₹{s['entry']}\n"
            f"   Stop-loss:  ₹{s['stop_loss']}  (risk ₹{s['risk']}/share)\n"
            f"   Target:     ₹{s['target']}  (reward ₹{s['reward']}/share)\n"
            f"   R:R Ratio:  1 : {s['rr_ratio']}\n"
            f"   RSI:        {s['rsi']}  |  ATR: ₹{s['atr']}\n"
            f"   EMA-50:     ₹{s['ema50']}  |  EMA-200: ₹{s['ema200']}\n"
        )

    lines.append("\n─" * 30)
    lines.append(
        "\n⚠️ <i>Paper trade only. Do NOT place real orders yet.\n"
        "Track in paper_trades.csv and review after 2 weeks.</i>"
    )
    lines.append("\n🤖 <i>navchin/nse-swing-trader</i>")

    return "\n".join(lines)


def notify_signals(signals: list[dict]) -> None:
    """Main entry point — format and send signals."""
    message = format_signal_message(signals)
    print("\n── Telegram Message Preview ──")
    print(message)
    print("──────────────────────────────\n")
    send_telegram(message)


if __name__ == "__main__":
    # Test with a dummy signal
    test = [{
        "ticker": "HDFCBANK", "cmp": 1642.0,
        "entry": 1642.0, "stop_loss": 1597.0, "target": 1732.0,
        "risk": 45.0, "reward": 90.0, "rr_ratio": 2.0,
        "rsi": 38.5, "ema50": 1660.0, "ema200": 1580.0, "atr": 30.0,
    }]
    notify_signals(test)
