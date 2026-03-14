import os
import requests
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
from datetime import datetime

# ======================
# CONFIG & SETTINGS
# ======================
BOT_TOKEN = "8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk"
CHAT_ID = "6348148813"
BREAKOUT_NEAR_THRESHOLD = 0.02

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200: print(f"Telegram Hatası: {response.text}")
    except Exception as e: print(f"Bağlantı hatası: {e}")

# ======================
# TURTLE ENGINE (SENİN KODUN)
# ======================
def _prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["entry_high_20"] = df["high"].rolling(20).max().shift(1)
    df["entry_low_20"] = df["low"].rolling(20).min().shift(1)
    df["exit_low_10"] = df["low"].rolling(10).min().shift(1)
    return df

def _simulate_state(df: pd.DataFrame):
    position = 0
    position_history = []
    for idx, row in df.iterrows():
        eh = row.get("entry_high_20")
        exl = row.get("exit_low_10")
        close = row.get("close")
        if pd.isna(eh) or pd.isna(exl):
            position_history.append(position)
            continue
        if position == 1 and close < exl:
            position = 0
        if position == 0 and close > eh:
            position = 1
        position_history.append(position)
    df["position"] = position_history
    return df

# ======================
# TARAMA (SCANNER)
# ======================
def run_scanner():
    tv = TvDatafeed()
    new_al = []
    breakout_near = []

    # Not: BIST_SYMBOLS listesi burada tanımlı olmalı (Daha önce paylaştığın liste)
    for symbol in BIST_SYMBOLS:
        try:
            df = tv.get_hist(symbol=symbol, exchange="BIST", interval=Interval.in_daily, n_bars=100)
            if df is None or len(df) < 30: continue

            df = _prepare_df(df)
            df = _simulate_state(df)
            
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            curr_pos = last["position"]
            prev_pos = prev["position"]
            close = last["close"]
            entry_high = last["entry_high_20"]

            # 🟢 YENİ AL (AFYON burada elenecek)
            if curr_pos == 1 and prev_pos != 1:
                new_al.append(f"🚀 *{symbol}* - Fiyat: {close:.2f} (Zirve: {entry_high:.2f})")
            
            # 🟡 BREAKOUT YAKIN
            elif curr_pos == 0 and close < entry_high:
                dist = (entry_high - close) / entry_high
                if dist <= BREAKOUT_NEAR_THRESHOLD:
                    new_al_val = entry_high
                    breakout_near.append(f"👀 *{symbol}* - %{dist*100:.2f} (Direnç: {entry_high:.2f})")

        except Exception as e:
            print(f"{symbol} hata: {e}")

    # Mesaj Gönderimi
    msg = ""
    if new_al:
        msg += "🚨 **TURTLE YENİ AL SİNYALİ**\n\n" + "\n".join(new_al) + "\n\n"
    if breakout_near:
        msg += "🔔 **BREAKOUT YAKIN (PUSU)**\n\n" + "\n".join(breakout_near)

    if msg:
        send_telegram(msg)

# SEMBOLLERİ BURAYA EKLEYEBİLİRSİN
BIST_SYMBOLS = ["AKSEN", "AFYON", "AKBNK", "THYAO", "EREGL", "TUPRS"] # Test için, sonra listeyi büyüt

if __name__ == "__main__":
    run_scanner()
