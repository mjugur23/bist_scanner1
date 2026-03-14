import os
import requests
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from datetime import datetime

# Kendi yazdığımız modülleri içe aktarıyoruz
from scanners.turtle_logic import check_turtle
from scanners.supertrend_logic import check_supertrend

# ======================
# CONFIG & SETTINGS
# ======================
BOT_TOKEN = "8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk"
CHAT_ID = "5886003690"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk/sendMessage"
    payload = {"5886003690": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Hatası: {e}")

# ======================
# ANA ÇALIŞTIRICI
# ======================
def run_scanner():
    tv = TvDatafeed()
    
    # Sonuç kutuları
    turtle_new, turtle_near = [], []
    st_new, st_near = [], []

    # Sembol listesi (Buraya 500'lük tam listeni yapıştırabilirsin)
    symbols = ["PETKM", "TURSG", "AKSEN", "AFYON", "THYAO", "ASELS", "EREGL", "TUPRS"]

    for symbol in symbols:
        try:
            # Veriyi bir kere çekiyoruz, her iki taramaya da gönderiyoruz
            df = tv.get_hist(symbol=symbol, exchange="BIST", interval=Interval.in_daily, n_bars=100)
            if df is None or len(df) < 35:
                continue

            # 1. TURTLE KONTROLÜ
            t_status, t_msg = check_turtle(df, symbol)
            if t_status == "NEW": turtle_new.append(t_msg)
            elif t_status == "NEAR": turtle_near.append(t_msg)

            # 2. SUPERTREND KONTROLÜ
            s_status, s_msg = check_supertrend(df, symbol)
            if s_status == "NEW": st_new.append(s_msg)
            elif s_status == "NEAR": st_near.append(s_msg)

        except Exception as e:
            print(f"{symbol} taranırken hata oluştu: {e}")

    # ======================
    # MESAJLARI GÖNDER (AYRI AYRI)
    # ======================
    
    # Mesaj 1: Turtle Sonuçları
    if turtle_new or turtle_near:
        t_output = ""
        if turtle_new:
            t_output += "🚨 **TURTLE TAZE KIRILIM (AL)**\n\n" + "\n".join(turtle_new) + "\n\n"
        if turtle_near:
            t_output += "🔔 **TURTLE BREAKOUT YAKIN (PUSU)**\n\n" + "\n".join(turtle_near)
        send_telegram(t_output)

    # Mesaj 2: Supertrend Sonuçları
    if st_new or st_near:
        s_output = ""
        if st_new:
            s_output += "✨ **SUPERTREND TAZE AL SİNYALİ**\n\n" + "\n".join(st_new) + "\n\n"
        if st_near:
            s_output += "🕯️ **SUPERTREND DÖNÜŞE YAKIN**\n\n" + "\n".join(st_near)
        send_telegram(s_output)

if __name__ == "__main__":
    run_scanner()
