import requests

BOT_TOKEN = "8710125777:AAEJocampyLtDyIL95jM_mXRVWeV655X2zY"
CHAT_ID = "5886003690"

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)

send_telegram("🚀 GitHub scanner çalıştı")
