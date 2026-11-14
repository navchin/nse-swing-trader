"""
NSE Nifty 50 Swing Trade Scanner
---------------------------------
Fetches Nifty 50 stocks via yfinance (.NS suffix)
Calculates RSI, EMA-50, EMA-200, ATR
Finds swing trade setups — bullish reversal after a dip
Outputs: list of signals with entry, stop-loss, target in ₹
"""

import yfinance as yf
import pandas as pd
import ta
from datetime import datetime, timedelta
import json

# ── Nifty 50 tickers (NSE suffix) ──────────────────────────────────────────
NIFTY50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "BAJFINANCE.NS", "NESTLEIND.NS", "ULTRACEMCO.NS", "WIPRO.NS",
    "HCLTECH.NS", "POWERGRID.NS", "NTPC.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
    "JSWSTEEL.NS", "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS", "ONGC.NS",
    "BPCL.NS", "HEROMOTOCO.NS", "BAJAJFINSV.NS", "DRREDDY.NS", "CIPLA.NS",
    "DIVISLAB.NS", "EICHERMOT.NS", "GRASIM.NS", "INDUSINDBK.NS", "M&M.NS",
    "APOLLOHOSP.NS", "TATACONSUM.NS", "HINDALCO.NS", "SBILIFE.NS", "HDFCLIFE.NS",
    "TECHM.NS", "BRITANNIA.NS", "BAJAJ-AUTO.NS", "UPL.NS", "SHRIRAMFIN.NS"
]

# ── Parameters ──────────────────────────────────────────────────────────────
RSI_LOWER       = 30
RSI_UPPER       = 45
EMA_SHORT       = 50
EMA_LONG        = 200
ATR_PERIOD      = 14
MIN_RR_RATIO    = 2.0
LOOKBACK_DAYS   = 100


def fetch_data(ticker: str):
    """Download OHLCV data for a ticker."""
    try:
        end   = datetime.today()
        start = end - timedelta(days=LOOKBACK_DAYS)
        df = yf.download(ticker, start=start, end=end,
                         progress=False, auto_adjust=True)
        if df is None or len(df) < 60:
            return None
        # Flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except Exception as e:
        print(f"  ⚠️  Fetch error {ticker}: {e}")
        return None


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add RSI, EMA-50, EMA-200, ATR using ta library."""
    close = df["Close"]
    high  = df["High"]
    low   = df["Low"]

    df["RSI"]    = ta.momentum.RSIIndicator(close, window=14).rsi()
    df["EMA50"]  = ta.trend.EMAIndicator(close, window=EMA_SHORT).ema_indicator()
    df["EMA200"] = ta.trend.EMAIndicator(close, window=EMA_LONG).ema_indicator()
    df["ATR"]    = ta.volatility.AverageTrueRange(
                       high, low, close, window=ATR_PERIOD).average_true_range()
    return df


def is_swing_setup(df: pd.DataFrame, ticker: str):
    """
    Bullish swing setup:
    1. Price > EMA-200  →  uptrend intact
    2. Price <= EMA-50 * 1.03  →  pulled back, cheap entry
    3. RSI between 30–45  →  oversold bounce zone
    4. RSI today > yesterday  →  momentum turning up
    5. Risk:Reward >= 1:2
    """
    if df is None or len(df) < 3:
        return None

    latest = df.iloc[-1]
    prev   = df.iloc[-2]

    try:
        cmp      = round(float(latest["Close"]), 2)
        rsi      = round(float(latest["RSI"]),   2)
        rsi_prev = round(float(prev["RSI"]),     2)
        ema50    = round(float(latest["EMA50"]),  2)
        ema200   = round(float(latest["EMA200"]), 2)
        atr      = round(float(latest["ATR"]),   2)
        volume   = float(latest["Volume"])
    except Exception:
        return None

    # Skip NaN values
    import math
    if any(math.isnan(v) for v in [cmp, rsi, ema50, ema200, atr]):
        return None

    # Conditions
    above_ema200 = cmp > ema200
    near_ema50   = cmp <= ema50 * 1.03
    rsi_zone     = RSI_LOWER < rsi < RSI_UPPER
    rsi_turning  = rsi > rsi_prev
    volume_ok    = volume > 100000

    if not all([above_ema200, near_ema50, rsi_zone, rsi_turning, volume_ok]):
        return None

    # Price levels
    entry     = cmp
    stop_loss = round(entry - (1.5 * atr), 2)
    target    = round(entry + (3.0 * atr), 2)
    risk      = round(entry - stop_loss,   2)
    reward    = round(target - entry,      2)
    rr_ratio  = round(reward / risk, 2) if risk > 0 else 0

    if rr_ratio < MIN_RR_RATIO:
        return None

    return {
        "ticker":     ticker.replace(".NS", ""),
        "cmp":        entry,
        "ema50":      ema50,
        "ema200":     ema200,
        "rsi":        rsi,
        "atr":        atr,
        "entry":      entry,
        "stop_loss":  stop_loss,
        "target":     target,
        "risk":       risk,
        "reward":     reward,
        "rr_ratio":   rr_ratio,
        "verdict":    "BUY",
        "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M IST"),
    }


def run_scanner() -> list:
    """Scan all Nifty 50 stocks and return signals."""
    signals = []
    print(f"🔍 Scanning {len(NIFTY50)} Nifty 50 stocks...\n")

    for ticker in NIFTY50:
        df = fetch_data(ticker)
        if df is None:
            print(f"  ⚠️  Skipped: {ticker} (no data)")
            continue
        df = calculate_indicators(df)
        signal = is_swing_setup(df, ticker)
        if signal:
            signals.append(signal)
            print(f"  ✅ SIGNAL: {signal['ticker']:<14} CMP ₹{signal['cmp']:<10} RSI {signal['rsi']}")
        else:
            print(f"  ⏭  No setup: {ticker.replace('.NS','')}")

    print(f"\n📊 Scan complete — {len(signals)} signal(s) found.")
    return signals


if __name__ == "__main__":
    signals = run_scanner()
    if signals:
        print("\n── Signals ──")
        print(json.dumps(signals, indent=2))