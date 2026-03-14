import sys
import os
import requests
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from concurrent.futures import ThreadPoolExecutor # Paralel çalışma için
import time

# Ana dizini sistem yoluna ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanners.turtle_logic import check_turtle
from scanners.supertrend_logic import check_supertrend

# ======================
# CONFIG
# ======================
BOT_TOKEN = "8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk"
CHAT_ID = "5886003690""
MAX_WORKERS = 10  # Aynı anda kaç hisse sorgulansın? (10-15 idealdir)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk/sendMessage"
    payload = {"chat_id": 5886003690, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Hatası: {e}")

# Global sonuç listeleri
turtle_new, turtle_near = [], []
st_new, st_near = [], []

def scan_single_symbol(tv, symbol):
    """Her bir hisse için çalışacak olan fonksiyon"""
    try:
        # Başına BIST: ekleyerek çekiyoruz
        full_symbol = f"BIST:{symbol}" if ":" not in symbol else symbol
        df = tv.get_hist(symbol=full_symbol, exchange="", interval=Interval.in_daily, n_bars=100)
        
        if df is None or df.empty or len(df) < 35:
            return

        clean_name = symbol.split(':')[-1]

        # 1. TURTLE
        t_status, t_msg = check_turtle(df, clean_name)
        if t_status == "NEW": turtle_new.append(t_msg)
        elif t_status == "NEAR": turtle_near.append(t_msg)

        # 2. SUPERTREND
        s_status, s_msg = check_supertrend(df, clean_name)
        if s_status == "NEW": st_new.append(s_msg)
        elif s_status == "NEAR": st_near.append(s_msg)

    except Exception as e:
        print(f"{symbol} hatası: {e}")

def run_scanner():
    start_time = time.time()
    tv = TvDatafeed()
    
    # 500'lük tam listenizi buraya ekleyin
    symbols = ["PETKM", "TURSG", "AKSEN", "AFYON", "THYAO", "ASELS", "EREGL", "TUPRS"] 
    
    print(f"Tarama başlatıldı. Toplam {len(symbols)} hisse taranıyor...")

    # PARALEL ÇALIŞTIRMA MERKEZİ
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # tv nesnesini her işleme göndererek paralel çalıştırıyoruz
        executor.map(lambda s: scan_single_symbol(tv, s), symbols)

    # MESAJLARI GÖNDER
    if turtle_new or turtle_near:
        t_output = ""
        if turtle_new: t_output += "🚨 **TURTLE TAZE KIRILIM**\n\n" + "\n".join(turtle_new) + "\n\n"
        if turtle_near: t_output += "🔔 **TURTLE PUSU**\n\n" + "\n".join(turtle_near)
        send_telegram(t_output)

    if st_new or st_near:
        s_output = ""
        if st_new: s_output += "✨ **SUPERTREND TAZE AL**\n\n" + "\n".join(st_new) + "\n\n"
        if st_near: s_output += "🕯️ **SUPERTREND PUSU**\n\n" + "\n".join(st_near)
        send_telegram(s_output)

    end_time = time.time()
    print(f"Tarama bitti. Süre: {int(end_time - start_time)} saniye.")

if __name__ == "__main__":
    run_scanner()
