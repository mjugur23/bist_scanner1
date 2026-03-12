import pandas as pd
import yfinance as yf
import requests

BOT_TOKEN="8665295187:AAEVNZQgFBmnECr4Oi18mtA8-KrvM0SFUN8"
CHAT_ID="5886003690"

symbols=[
"THYAO.IS",
"ASELS.IS",
"GARAN.IS",
"KCHOL.IS",
"EREGL.IS"
]

def send(msg):

    url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        data={
        "chat_id":CHAT_ID,
        "text":msg
        }
    )

for s in symbols:

    df=yf.download(s,period="3mo",interval="1d")

    if df.empty:
        continue

    close=df["Close"]
    high=df["High"]

    # Turtle breakout
    donchian20=high.rolling(20).max()

    if close.iloc[-1] > donchian20.iloc[-2]:

        send(f"🚀 Turtle Breakout: {s}")

    # High close
    if close.iloc[-1] >= high.iloc[-1]*0.999:

        send(f"📈 High Close: {s}")
