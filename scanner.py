import requests

BOT_TOKEN = "BOT_TOKEN_BURAYA"
CHAT_ID = "CHAT_ID_BURAYA"

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)

send_telegram("🚀 GitHub scanner çalıştı")
