import pandas as pd
import yfinance as yf
import requests

BOT_TOKEN="8665295187:AAEVNZQgFBmnECr4Oi18mtA8-KrvM0SFUN8"
CHAT_ID="5886003690"

BIST_SYMBOLS = [
"AEFES","AGHOL","AKBNK","AKFGY","AKSA","AKSEN","ALARK","ALBRK","ALFAS",
"ARCLK","ASELS","ASTOR","BIMAS","BRYAT","CCOLA","CIMSA","DOAS","DOHOL",
"ECILC","EGEEN","EKGYO","ENJSA","ENKAI","EREGL","FROTO","GARAN","GESAN",
"GUBRF","HALKB","HEKTS","ISCTR","ISMEN","KARSN","KCHOL","KONTR","KORDS",
"KOZAA","KOZAL","KRDMD","MAVI","MGROS","ODAS","OTKAR","PETKM","PGSUS",
"SAHOL","SASA","SISE","SKBNK","SMRTG","SOKM","TCELL","THYAO","TKFEN",
"TUPRS","ULKER","VAKBN","VESTL","YKBNK"
]

symbols=[s+".IS" for s in BIST_SYMBOLS]

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

    if float(close.iloc[-1]) > float(donchian20.iloc[-2]):

        send(f"🚀 Turtle Breakout: {s}")

  
