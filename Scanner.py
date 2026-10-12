import os
import requests
import pandas as pd
import numpy as np

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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
        print(f"Trạng thái gửi Telegram: {response.status_code}")
    except Exception as e:
        print(f"Lỗi gửi tin nhắn: {e}")

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

def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi

def main():
    print("Đang quét dữ liệu thị trường...")
    # Thử nghiệm quét BTC trên Binance khung 4h
    symbol = "BTCUSDT"
    prices = get_binance_klines(symbol, "4h", 100)
    
    if prices is not None and len(prices) > 0:
        rsi_values = calculate_rsi(prices.values, 14)
        current_price = prices.iloc[-1]
        current_rsi = rsi_values[-1]
        
        msg = (
            f"📊 **QUÉT THỊ TRƯỜNG RSI (BINANCE)**\n\n"
            f"🔹 **Cặp:** `{symbol}`\n"
            f"💰 **Giá hiện tại:** `${current_price:,.2f}`\n"
            f"📈 **RSI (14):** `{current_rsi:.2f}`\n"
            f"⚡ **Trạng thái:** Hệ thống đang chạy ổn định."
        )
        send_telegram(msg)
    else:
        send_telegram("⚠️ Không thể tải dữ liệu nến từ sàn!")

if __name__ == "__main__":
    main()
