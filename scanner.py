import os
import json
import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
from tvDatafeed import TvDatafeed, Interval

# --- TELEGRAM AYARLARI ---
TOKEN = "8839652305:AAE7x_DriVyFis-ceROoxJGuwdX9EwhFYCc"
CHAT_ID = "5886003690"
MEMORY_FILE = "hafiza.json"
STATS_FILE = "turtle_istatistik.json" # 🔥 YENİ: BİLGİSAYARDAN YÜKLEYECEĞİMİZ VERİ TABANI

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code != 200:
            print(f"Telegram HATA {r.status_code}: {r.text}")
        else:
            print("Mesaj gönderildi.")
    except Exception as e:
        print(f"Telegram exception: {e}")

# --- HİSSE LİSTESİ ---
symbols = [
    "THYAO","ASELS","ISCTR","AKBNK","YKBNK","KCHOL","TUPRS","TRALT","SASA","ASTOR",
    # ... (Listenin tamamı burada olacak, yer kaplamaması için kısalttım) ...
    "LRSHO"
]

tv = TvDatafeed()

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
                return data.get("alerts", data) if isinstance(data, dict) else {}
        except:
            pass
    return {}

def save_memory(memory_dict):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_dict, f)

# 🔥 YENİ: İSTATİSTİK VERİ TABANINI YÜKLEYEN FONKSİYON
def load_stats_db():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"İstatistik dosyası okunamadı: {e}")
    return {}

def check_turtle(df, symbol, stats_db):
    if df is None or len(df) < 30:
        return "FLAT", ""

    df['Donchian_High'] = df['high'].rolling(window=20).max()
    df['Donchian_Low'] = df['low'].rolling(window=10).min()
    df['upper_1'] = df['Donchian_High'].shift(1)
    df['sdown_1'] = df['Donchian_Low'].shift(1)
    df['buySignal'] = df['high'] >= df['upper_1']
    df['buyExit'] = df['low'] <= df['sdown_1']

    state = "FLAT"
    fresh_signal = False

    for i in range(20, len(df)):
        if df['buySignal'].iloc[i] and state != "LONG":
            state = "LONG"
            if i == len(df) - 1:
                fresh_signal = True
        elif df['buyExit'].iloc[i] and state == "LONG":
            state = "FLAT"

    last_close = df['close'].iloc[-1]
    last_upper = df['upper_1'].iloc[-1]

    # 🔥 İSTATİSTİKLERİ JSON'DAN ÇEK VE MESAJA EKLE
    hisse_istatistik = stats_db.get(symbol, {})
    stat_msg = ""
    if hisse_istatistik:
        stat_msg = (
            f"\n🎯 *Başarı:* %{hisse_istatistik.get('Başarı Oranı %', 0)}"
            f"\n💰 *Beklenti:* %{hisse_istatistik.get('Beklenen Getiri %', 0)}"
            f"\n📈 *Max Yükseliş:* %{hisse_istatistik.get('Ort. MFE %', 0)}"
        )

    if fresh_signal:
        msg = f"🚀 *{symbol}* - Fiyat: {last_close:.2f} (Zirve: {last_upper:.2f}){stat_msg}"
        return "NEW", msg

    if state == "LONG":
        return "LONG", ""

    if state == "FLAT" and pd.notna(last_upper) and last_close < last_upper:
        distance = ((last_upper - last_close) / last_close) * 100
        if 0 < distance <= 1.5:
            msg = f"👀 *{symbol}* - Mesafe: %{distance:.2f} (Direnç: {last_upper:.2f}){stat_msg}"
            return "NEAR", msg

    return "FLAT", ""

def scan_symbol(args):
    symbol, stats_db = args
    try:
        df = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_daily, n_bars=100)
        status, msg = check_turtle(df, symbol, stats_db)
        return symbol, status, msg
    except Exception as e:
        return symbol, "FLAT", ""

def main():
    memory = load_memory()
    stats_db = load_stats_db() # İstatistikleri başlangıçta bir kere hafızaya al
    updated = False

    turtle_al = []
    turtle_yakin = []

    # stats_db'yi fonksiyon içine argüman olarak gönderiyoruz
    scan_args = [(sym, stats_db) for sym in symbols]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = executor.map(scan_symbol, scan_args)

    for symbol, status, msg in results:
        prev_status = memory.get(symbol, "FLAT")

        if status == "NEW" and prev_status != "LONG":
            turtle_al.append(msg)
            memory[symbol] = "LONG"
            updated = True
        elif status == "LONG" and prev_status != "LONG":
            memory[symbol] = "LONG"
            updated = True
        elif status == "NEAR":
            if prev_status != "NEAR" and prev_status != "LONG":
                turtle_yakin.append(msg)
                memory[symbol] = "NEAR"
                updated = True
        elif status == "FLAT" and prev_status != "FLAT":
            memory[symbol] = "FLAT"
            updated = True

    if turtle_al or turtle_yakin:
        final_msg = ""
        if turtle_al:
            final_msg += "🚨 *TURTLE AL*\n\n" + "\n\n".join(turtle_al) + "\n\n"
        if turtle_yakin:
            final_msg += "🔔 *TURTLE (YAKIN)*\n\n" + "\n\n".join(turtle_yakin) + "\n\n"

        send_telegram(final_msg)
    else:
        print("Yeni sinyal bulunamadı.")

    if updated:
        save_memory(memory)

if __name__ == "__main__":
    main()
