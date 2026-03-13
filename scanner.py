import pandas as pd
import requests
import json
from tvDatafeed import TvDatafeed, Interval

# ======================
# TELEGRAM
# ======================

BOT_TOKEN = "8665295187:AAEVNZQgFBmnECr4Oi18mtA8-KrvM0SFUN8"
CHAT_ID = "5886003690"

def send_telegram(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)

# ======================
# BIST100 LISTE
# ======================

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

# ======================
# SPAM KONTROL
# ======================

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

# ======================
# SCANNER
# ======================

def run_scanner():

    tv = TvDatafeed()

    sent = load_sent()

    new_al = []
    breakout_near = []

    for symbol in BIST100_SYMBOLS:

        try:

            df = tv.get_hist(
                symbol=symbol,
                exchange="BIST",
                interval=Interval.in_daily,
                n_bars=60
            )

            if df is None:
                continue

            close = df["close"].iloc[-1]

            donchian_high = df["high"].iloc[-21:-1].max()

            breakout_distance = (donchian_high - close) / close * 100

            # ======================
            # YENİ AL
            # ======================

            if close > donchian_high:

                key = f"{symbol}_AL"

                if key not in sent:

                    new_al.append(symbol)
                    sent.append(key)

            # ======================
            # BREAKOUT YAKIN
            # ======================

            elif breakout_distance <= 3:

                breakout_near.append(symbol)

        except Exception as e:

            print(symbol, "hata:", e)

    # ======================
    # TELEGRAM MESAJ
    # ======================

    msg = ""

    if len(new_al) > 0:

        msg += "🚨 YENİ AL\n\n"

        for s in new_al:
            msg += f"{s}\n"

        msg += "\n"

    if len(breakout_near) > 0:

        msg += "👀 BREAKOUT YAKIN\n\n"

        for s in breakout_near:
            msg += f"{s}\n"

    if msg != "":

        send_telegram(msg)

        save_sent(sent)

# ======================
# RUN
# ======================

if __name__ == "__main__":

    run_scanner()
