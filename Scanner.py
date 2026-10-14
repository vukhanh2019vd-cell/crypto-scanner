import requests

TELEGRAM_TOKEN = "8987523565:AAG8ZFmkqWTBsM0u6V5ibdieXwqTtwbqMM"
TELEGRAM_CHAT_ID = "1353463391"

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": "🚨 Test bot: Ket noi thanh cong!",
    "parse_mode": "Markdown"
}

response = requests.post(url, json=payload)
print("Trang thai gui:", response.status_code, response.text)
