import requests

BOT_TOKEN = "8665295187:AAEVNZQgFBmnECr4Oi18mtA8-KrvM0SFUN8"
CHAT_ID = "5886003690"

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


def run_scanner():

    # örnek sinyal
    symbol = "MAVI"
    price = 43.70

    msg = f"""
🚨 BIST Turtle Alert

Hisse: {symbol}
Fiyat: {price}
"""

    send_telegram(msg)


run_scanner()
