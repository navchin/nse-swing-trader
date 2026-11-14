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
import pandas_ta as ta
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

# ── Parameters (swing trading) ──────────────────────────────────────────────
RSI_OVERSOLD      = 45   # RSI below this = potential bounce
RSI_UPPER_LIMIT   = 60   # RSI should not be too high already
EMA_SHORT         = 50
EMA_LONG          = 200
ATR_PERIOD        = 14
MIN_RR_RATIO      = 2.0  # Minimum risk:reward = 1:2
LOOKBACK_DAYS     = 90   # Enough for EMA-200


def fetch_data(ticker: str) -> pd.DataFrame | None:
    """Download OHLCV data for a ticker."""
    try:
        end   = datetime.today()
        start = end - timedelta(days=LOOKBACK_DAYS)
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        if df is None or len(df) < 50:
            return None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df
    except Exception:
        return None


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add RSI, EMA-50, EMA-200, ATR to dataframe."""
    df["RSI"]     = ta.rsi(df["Close"], length=14)
    df["EMA50"]   = ta.ema(df["Close"], length=EMA_SHORT)
    df["EMA200"]  = ta.ema(df["Close"], length=EMA_LONG)
    atr           = ta.atr(df["High"], df["Low"], df["Close"], length=ATR_PERIOD)
    df["ATR"]     = atr
    return df


def is_swing_setup(df: pd.DataFrame) -> dict | None:
    """
    Bullish swing setup conditions:
    1. Price is ABOVE EMA-200  →  uptrend intact
    2. Price pulled back to near EMA-50  →  dip opportunity
    3. RSI is between 30–45  →  oversold but not broken
    4. Today's RSI > yesterday's RSI  →  momentum turning up
    5. Risk:Reward >= 1:2 using ATR
    """
    if df is None or len(df) < 3:
        return None

    latest   = df.iloc[-1]
    prev     = df.iloc[-2]

    cmp      = round(float(latest["Close"]), 2)
    rsi      = round(float(latest["RSI"]),   2)
    rsi_prev = round(float(prev["RSI"]),     2)
    ema50    = round(float(latest["EMA50"]),  2)
    ema200   = round(float(latest["EMA200"]), 2)
    atr      = round(float(latest["ATR"]),   2)

    # Skip if any indicator is NaN
    if any(v != v for v in [cmp, rsi, ema50, ema200, atr]):
        return None

    # Condition checks
    above_ema200   = cmp > ema200                      # uptrend
    near_ema50     = cmp <= ema50 * 1.03               # within 3% of EMA-50
    rsi_oversold   = RSI_OVERSOLD > rsi > 30           # dip zone
    rsi_turning    = rsi > rsi_prev                    # momentum up
    volume_ok      = float(latest["Volume"]) > 100000  # min liquidity

    if not all([above_ema200, near_ema50, rsi_oversold, rsi_turning, volume_ok]):
        return None

    # Price levels
    entry      = cmp
    stop_loss  = round(entry - (1.5 * atr), 2)
    target     = round(entry + (3.0 * atr), 2)
    risk       = round(entry - stop_loss,   2)
    reward     = round(target - entry,      2)
    rr_ratio   = round(reward / risk,       2) if risk > 0 else 0

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


def run_scanner() -> list[dict]:
    """Scan all Nifty 50 stocks and return signals."""
    signals = []
    print(f"🔍 Scanning {len(NIFTY50)} Nifty 50 stocks...")

    for ticker in NIFTY50:
        df = fetch_data(ticker)
        if df is None:
            continue
        df = calculate_indicators(df)
        signal = is_swing_setup(df)
        if signal:
            signals.append(signal)
            print(f"  ✅ Signal found: {signal['ticker']} | CMP ₹{signal['cmp']} | RSI {signal['rsi']}")
        else:
            print(f"  ⏭  No setup:    {ticker.replace('.NS','')}")

    print(f"\n📊 Scan complete. {len(signals)} signal(s) found.")
    return signals


if __name__ == "__main__":
    signals = run_scanner()
    print(json.dumps(signals, indent=2))
