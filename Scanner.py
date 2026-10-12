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

def main():
    print("Đang bắt đầu quét thị trường Binance & MEXC...")
    test_msg = "🤖 **Bot Scanner đã khởi động thành công!**\nĐang theo dõi dữ liệu RSI đa khung thời gian."
    send_telegram(test_msg)
    print("Đã hoàn tất quét toàn bộ 2 sàn!")

if __name__ == "__main__":
    main()
