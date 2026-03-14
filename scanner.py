import sys
import os
import requests
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from concurrent.futures import ThreadPoolExecutor
import time

# Modül yolları
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scanners.supertrend_logic import check_supertrend

# ======================
# CONFIG
# ======================
BOT_TOKEN = "8665295187:AAEVNZQgFBmnECr4Oi18mtA8-KrvM0SFUN8"
CHAT_ID = "5886003690"
MAX_WORKERS = 10 
BREAKOUT_NEAR_THRESHOLD = 0.02

# Global sonuç listeleri
turtle_new = []
turtle_near = []
st_new = []
st_near = []

def send_telegram(msg):
    url = f"https://api.telegram.org/bot8665295187:AAEVNZQgFBmnECr4Oi18mtA8-KrvM0SFUN8/sendMessage"
    payload = {"chat_id": 5886003690, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e: print(f"Telegram Hatası: {e}")

# ======================
# TURTLE ENGINE (GÖNDERDİĞİN DOĞRU MANTIK)
# ======================
def check_turtle_logic(df, symbol):
    # Senin _prepare_df ve _simulate_state mantığının birleşmiş hali
    df = df.copy()
    df["eh20"] = df["high"].rolling(20).max().shift(1)
    df["exl10"] = df["low"].rolling(10).min().shift(1)
    
    position = 0
    pos_history = []
    
    # Geçmişten bugüne pozisyon simülasyonu (Doğru sonuç veren kısım burasıydı)
    for idx, row in df.iterrows():
        eh = row["eh20"]
        exl = row["exl10"]
        close = row["close"]
        
        if pd.isna(eh) or pd.isna(exl):
            pos_history.append(position)
            continue
            
        if position == 1 and close < exl:
            position = 0
        elif position == 0 and close > eh:
            position = 1
        pos_history.append(position)
    
    df["position"] = pos_history
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Sinyal Kararı
    if last["position"] == 1 and prev["position"] == 0:
        return "NEW", f"🚀 *{symbol}* - Fiyat: {last['close']:.2f} (Zirve: {last['eh20']:.2f})"
    
    elif last["position"] == 0 and last["close"] < last["eh20"]:
        dist = (last["eh20"] - last["close"]) / last["eh20"]
        if dist <= BREAKOUT_NEAR_THRESHOLD:
            return "NEAR", f"🔔 *{symbol}* - %{dist*100:.2f} (Direnç: {last['eh20']:.2f})"
            
    return None, None

# ======================
# PARALEL TARAMA FONKSİYONU
# ======================
def scan_single_symbol(tv, symbol):
    global turtle_new, turtle_near, st_new, st_near
    try:
        full_symbol = f"BIST:{symbol}" if ":" not in symbol else symbol
        df = tv.get_hist(symbol=full_symbol, exchange="", interval=Interval.in_daily, n_bars=100)
        
        if df is None or df.empty or len(df) < 35: return

        clean_name = symbol.split(':')[-1]

        # 1. TURTLE (Senin kodunla çalışan motor)
        t_status, t_msg = check_turtle_logic(df, clean_name)
        if t_status == "NEW": turtle_new.append(t_msg)
        elif t_status == "NEAR": turtle_near.append(t_msg)

        # 2. SUPERTREND
        s_status, s_msg = check_supertrend(df, clean_name)
        if s_status == "NEW": st_new.append(s_msg)
        elif s_status == "NEAR": st_near.append(s_msg)

    except Exception as e: print(f"{symbol} hata: {e}")

def run_scanner():
    # Listeleri her tarama başında temizle
    global turtle_new, turtle_near, st_new, st_near
    turtle_new.clear(); turtle_near.clear(); st_new.clear(); st_near.clear()
    
    tv = TvDatafeed()
    
    # 500'lük listenizi buraya koyun
    symbols = ["AKSEN", "AFYON", "AKBNK", "THYAO", "EREGL", "TUPRS", "PETKM", "TURSG"] 

    print(f"Tarama {len(symbols)} hisse için paralel başladı...")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(lambda s: scan_single_symbol(tv, s), symbols)

    # MESAJ GÖNDERİMİ
    t_output = ""
    if turtle_new: t_output += "🚨 **TURTLE YENİ AL**\n\n" + "\n".join(turtle_new) + "\n\n"
    if turtle_near: t_output += "🔔 **TURTLE PUSU**\n\n" + "\n".join(turtle_near)
    if t_output: send_telegram(t_output)

    s_output = ""
    if st_new: s_output += "✨ **SUPERTREND TAZE AL**\n\n" + "\n".join(st_new) + "\n\n"
    if st_near: s_output += "🕯️ **SUPERTREND PUSU**\n\n" + "\n".join(st_near)
    if s_output: send_telegram(s_output)

if __name__ == "__main__":
    run_scanner()
