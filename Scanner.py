import os
import requests
import pandas as pd
import numpy as np

TELEGRAM_TOKEN = "8987523565:AAG8ZFmkqWTBsM0u6V5ibdieXwqTtwbqMM"
TELEGRAM_CHAT_ID = "1353463391"

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Chưa cấu hình Telegram Token hoặc Chat ID!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print("Trang thai gui:", response.status_code, response.text)
    except Exception as e:
        print("Loi:", e)

def get_binance_klines(symbol="BTCUSDT", interval="4h", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if isinstance(data, list):
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            df['close'] = df['close'].astype(float)
            return df['close']
    except Exception as e:
        print(f"Lỗi lấy dữ liệu Binance {symbol}: {e}")
    return None

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_market():
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
    alert_messages = []
    
    for symbol in symbols:
        closes = get_binance_klines(symbol)
        if closes is not None and len(closes) > 14:
            rsi = calculate_rsi(closes)
            current_rsi = rsi.iloc[-1]
            print(f"{symbol} RSI (H4): {current_rsi:.2f}")
            
            if current_rsi < 30:
                alert_messages.append(f"🚨 *{symbol}* Quá bán (Oversold)! RSI H4 = `{current_rsi:.2f}`")
            elif current_rsi > 70:
                alert_messages.append(f"🚨 *{symbol}* Quá mua (Overbought)! RSI H4 = `{current_rsi:.2f}`")
                
    if alert_messages:
        full_msg = "\n".join(alert_messages)
        send_telegram(full_msg)
    else:
        print("Không có đồng nào chạm ngưỡng RSI.")

if __name__ == "__main__":
    print("Bắt đầu quét thị trường...")
    scan_market()
