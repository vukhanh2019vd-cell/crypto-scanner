import os
import requests
import pandas as pd
import numpy as np

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Lỗi gửi tin nhắn: {e}")

def calculate_rsi(prices, period=14):
    deltas = pd.Series(prices).diff()
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi_list = [rsi]
    for delta in deltas[period+1:]:
        up = (up * (period - 1) + max(delta, 0)) / period
        down = (down * (period - 1) + max(-delta, 0)) / period
        rs = up / down if down != 0 else 0
        rsi = 100.0 - (100.0 / (1.0 + rs))
        rsi_list.append(rsi)
    return rsi_list

def check_divergence(prices, rsis):
    p = prices[-30:]
    r = rsis[-30:]
    # Phân kỳ dương (Bullish)
    if p[-1] < p[-15] and r[-1] > r[-15] and r[-1] < 40:
        return "BULLISH", min(p)
    # Phân kỳ âm (Bearish)
    elif p[-1] > p[-15] and r[-1] < r[-15] and r[-1] > 60:
        return "BEARISH", max(p)
    return None, None

# 1. Quét sàn Binance
def scan_binance():
    print("Đang quét Binance...")
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        tickers = requests.get(url).json()
        
        for ticker in tickers:
            symbol = ticker['symbol']
            if symbol.endswith('USDT') and float(ticker['quoteVolume']) > 15000000:
                for tf in ['1h', '4h']:
                    kline_url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=60"
                    kline_res = requests.get(kline_url).json()
                    
                    if isinstance(kline_res, list) and len(kline_res) >= 50:
                        closes = [float(c[4]) for c in kline_res]
                        rsi_series = calculate_rsi(closes)
                        div_type, pivot_price = check_divergence(closes, rsi_series)
                        
                        if div_type:
                            entry = closes[-1]
                            rsi_val = rsi_series[-1]
                            
                            if div_type == "BULLISH":
                                sl = pivot_price * 0.99
                                risk = entry - sl
                                tp1 = entry + (risk * 1.5)
                                tp2 = entry + (risk * 2.5)
                                signal_text = "🟢 **PHÂN KỲ DƯƠNG (LONG)**"
                            else:
                                sl = pivot_price * 1.01
                                risk = sl - entry
                                tp1 = entry - (risk * 1.5)
                                tp2 = entry - (risk * 2.5)
                                signal_text = "🔴 **PHÂN KỲ ÂM (SHORT)**"
                                
                            msg = (
                                f"⚡ **BINANCE - KHUNG {tf.upper()}** ⚡\n\n"
                                f"🔹 Cặp: `{symbol}`\n"
                                f"📊 Tín hiệu: {signal_text}\n"
                                f"🎯 **Entry:** `${entry:,.4f}`\n"
                                f"🛑 **Stop Loss (SL):** `${sl:,.4f}`\n"
                                f"🎯 **Take Profit 1 (TP1):** `${tp1:,.4f}`\n"
                                f"🎯 **Take Profit 2 (TP2):** `${tp2:,.4f}`\n"
                                f"📈 RSI: `{rsi_val:.2f}`"
                            )
                            send_telegram(msg)
    except Exception as e:
        print(f"Lỗi Binance: {e}")

# 2. Quét sàn MEXC
def scan_mexc():
    print("Đang quét MEXC...")
    try:
        url = "https://api.mexc.com/api/v3/ticker/24hr"
        tickers = requests.get(url).json()
        
        for ticker in tickers:
            symbol = ticker.get('symbol', '')
            if symbol.endswith('USDT') and float(ticker.get('quoteVolume', 0)) > 5000000:
                for tf in ['1h', '4h']:
                    kline_url = f"https://api.mexc.com/api/v3/klines?symbol={symbol}&interval={tf}&limit=60"
                    kline_res = requests.get(kline_url).json()
                    
                    if isinstance(kline_res, list) and len(kline_res) >= 50:
                        closes = [float(c[4]) for c in kline_res]
                        rsi_series = calculate_rsi(closes)
                        div_type, pivot_price = check_divergence(closes, rsi_series)
                        
                        if div_type:
                            entry = closes[-1]
                            rsi_val = rsi_series[-1]
                            
                            if div_type == "BULLISH":
                                sl = pivot_price * 0.99
                                risk = entry - sl
                                tp1 = entry + (risk * 1.5)
                                tp2 = entry + (risk * 2.5)
                                signal_text = "🟢 **PHÂN KỲ DƯƠNG (LONG)**"
                            else:
                                sl = pivot_price * 1.01
                                risk = sl - entry
                                tp1 = entry - (risk * 1.5)
                                tp2 = entry - (risk * 2.5)
                                signal_text = "🔴 **PHÂN KỲ ÂM (SHORT)**"
                                
                            msg = (
                                f"⚡ **MEXC - KHUNG {tf.upper()}** ⚡\n\n"
                                f"🔹 Cặp: `{symbol}`\n"
                                f"📊 Tín hiệu: {signal_text}\n"
                                f"🎯 **Entry:** `${entry:,.4f}`\n"
                                f"🛑 **Stop Loss (SL):** `${sl:,.4f}`\n"
                                f"🎯 **Take Profit 1 (TP1):** `${tp1:,.4f}`\n"
                                f"🎯 **Take Profit 2 (TP2):** `${tp2:,.4f}`\n"
                                f"📈 RSI: `{rsi_val:.2f}`"
                            )
                            send_telegram(msg)
    except Exception as e:
        print(f"Lỗi MEXC: {e}")

if __name__ == "__main__":
    scan_binance()
    scan_mexc()
    print("Đã hoàn tất quét toàn bộ 2 sàn!")ểp
