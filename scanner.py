import pandas as pd
import requests
import json
from tvDatafeed import TvDatafeed, Interval

# ==============================
# TELEGRAM AYARLARI
# ==============================

BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
CHAT_ID = "TELEGRAM_CHAT_ID"

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)

# ==============================
# BIST100 LISTESI
# ==============================

BIST100_SYMBOLS = [
"AEFES","AGHOL","AKBNK","AKSA","AKSEN","ALARK","ARCLK","ASELS","ASTOR",
"BIMAS","BRYAT","CANTE","CCOLA","CIMSA","DOAS","DOHOL","ECILC","ECZYT",
"EGEEN","EKGYO","ENJSA","ENKAI","EREGL","FROTO","GARAN","GESAN","GUBRF",
"HALKB","HEKTS","ISCTR","ISMEN","KCHOL","KONTR","KOZAA","KOZAL","KRDMD",
"LOGO","MAVI","MGROS","ODAS","OTKAR","OYAKC","PGSUS","PETKM","QUAGR",
"SAHOL","SASA","SISE","SKBNK","SMRTG","SOKM","TAVHL","TCELL","THYAO",
"TKFEN","TOASO","TSKB","TTKOM","TTRAK","TUPRS","ULKER","VAKBN","VESBE",
"VESTL","YKBNK","ZOREN"
]

# ==============================
# SPAM KONTROL DOSYASI
# ==============================

SIGNAL_FILE = "sent_signals.json"

def load_sent():

    try:
        with open(SIGNAL_FILE,"r") as f:
            return json.load(f)
    except:
        return []

def save_sent(data):

    with open(SIGNAL_FILE,"w") as f:
        json.dump(data,f)

# ==============================
# SCANNER
# ==============================

def run_scanner():

    tv = TvDatafeed()

    sent = load_sent()

    signals = []

    for symbol in BIST100_SYMBOLS:

        try:

            df = tv.get_hist(
                symbol=symbol,
                exchange="BIST",
                interval=Interval.in_daily,
                n_bars=50
            )

            if df is None:
                continue

            close = df["close"].iloc[-1]

            donchian_high = df["high"].iloc[-21:-1].max()

            if close > donchian_high:

                key = f"{symbol}_TURTLE"

                if key not in sent:

                    signals.append(symbol)

                    sent.append(key)

        except Exception as e:

            print(symbol, "hata:", e)

    if len(signals) > 0:

        msg = "🚨 BIST Turtle AL\n\n"

        for s in signals:
            msg += f"{s}\n"

        send_telegram(msg)

        save_sent(sent)

# ==============================
# RUN
# ==============================

if __name__ == "__main__":

    run_scanner()
