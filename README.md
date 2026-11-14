# NSE Swing Trader 🇮🇳📈

Automated Nifty 50 swing trade scanner.  
Runs every weekday at **9:15 AM IST** via GitHub Actions.  
Sends signals to **Telegram**. Logs to **paper_trades.csv**.  
No real orders. Paper trading only until you're ready.

---

## What it does

1. Fetches all 50 Nifty 50 stocks via yfinance
2. Calculates RSI, EMA-50, EMA-200, ATR
3. Finds stocks in a **bullish swing setup** (dip in uptrend, RSI recovering)
4. Calculates Entry / Stop-Loss / Target in ₹
5. Sends a **Telegram message** to your phone
6. Saves signals to `paper_trades.csv` for tracking

---

## Setup (one time, 15 minutes)

### Step 1 — Fork / clone this repo
```bash
git clone https://github.com/navchin/nse-swing-trader.git
cd nse-swing-trader
```

### Step 2 — Create a Telegram Bot (5 minutes)
1. Open Telegram → search **@BotFather**
2. Send `/newbot`
3. Give it a name: `Naveen Swing Trader`
4. Give it a username: `naveenswing_bot`
5. BotFather gives you a **token** — copy it
6. Open this URL in browser (replace YOUR_TOKEN):
   `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
7. Send any message to your bot first, then refresh the URL
8. You'll see `"chat":{"id":XXXXXXXXX}` — that number is your **Chat ID**

### Step 3 — Add GitHub Secrets
In your GitHub repo → **Settings → Secrets and variables → Actions → New secret**

| Secret name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | The token from BotFather |
| `TELEGRAM_CHAT_ID` | Your chat ID number |

### Step 4 — Push to GitHub
```bash
git add .
git commit -m "feat: NSE swing scanner v1"
git push origin main
```

### Step 5 — Test it manually
GitHub repo → **Actions tab** → **NSE Swing Scanner** → **Run workflow**  
Check your Telegram in 2–3 minutes.

---

## Signal logic (Bullish Swing Setup)

| Condition | Value | Why |
|---|---|---|
| Price > EMA-200 | ✅ Required | Uptrend intact |
| Price ≤ EMA-50 × 1.03 | ✅ Required | Pulled back, cheap entry |
| RSI between 30–45 | ✅ Required | Oversold, ready to bounce |
| RSI today > RSI yesterday | ✅ Required | Momentum turning up |
| Volume > 1 lakh shares | ✅ Required | Real liquidity |
| Risk:Reward ≥ 1:2 | ✅ Required | Only good setups pass |

---

## Paper Trade Journal

Every signal is saved to `paper_trades.csv`.  
After each trade resolves, manually update:
- `outcome` → `TARGET HIT` or `STOPPED OUT`
- `exit_price` → what price you exited at
- `pnl_per_share` → exit - entry

After 2–3 weeks, review the CSV to see win rate and accuracy.

---

## Project structure

```
nse-swing-trader/
├── main.py              # Entry point
├── scanner.py           # Nifty 50 scanner + signal logic
├── paper_trade.py       # CSV logger
├── notify.py            # Telegram alerts
├── requirements.txt     # Python dependencies
├── paper_trades.csv     # Auto-created on first run
└── .github/
    └── workflows/
        └── swing_scanner.yml  # Runs at 9:15 AM IST weekdays
```

---

## Next steps (after 2–3 weeks of paper trading)

- [ ] Review paper_trades.csv — is win rate > 60%?
- [ ] Add Zerodha Kite Connect for real order placement
- [ ] Expand from Nifty 50 to Nifty 500
- [ ] Add Bearish agent (short selling / exit signals)
- [ ] Add FII/DII flow as additional filter

---

*Built by Naveen (navchin) | Paper trading only | Not SEBI registered advice*
