import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import json
import warnings

warnings.filterwarnings('ignore')

# --- TELEGRAM VE HAFIZA AYARLARI ---
TOKEN = "8625940807:AAE_bsrBsj7lojRv6Dhbq0uJjY_kaz7RwMo"
CHAT_ID = "5886003690"
MEMORY_FILE = "dusen_hafiza.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except:
            return {}
    return {}

def save_memory(memory_dict):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory_dict, f)
    except Exception as e:
        print(f"Hafiza yazma hatasi: {e}")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram hatasi: {e}")

# --- ANALIZ MOTORU ---
def find_downtrend_status(df, window=10, min_distance=20): # Ayarlar bilgisayardaki gibi güncellendi
    if df is None or len(df) < 50:
        return None, {}
        
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    high_col = 'High' if 'High' in df.columns else 'high'
    close_col = 'Close' if 'Close' in df.columns else 'close'
    
    highs = df[high_col].values
    closes = df[close_col].values
    
    pivot_indices = []
    for i in range(window, len(highs) - window):
        if highs[i] == max(highs[i - window : i + window + 1]):
            if not pivot_indices or i - pivot_indices[-1] >= 5:
                pivot_indices.append(i)

    if len(pivot_indices) < 2:
        return None, {}

    current_idx = len(highs) - 1
    current_close = closes[current_idx]
    prev_close = closes[current_idx - 1]

    for i in range(len(pivot_indices) - 2, -1, -1):
        for j in range(len(pivot_indices) - 1, i, -1):
            p1_idx = pivot_indices[i]
            p2_idx = pivot_indices[j]
            if p2_idx - p1_idx < min_distance: continue

            p1_high = highs[p1_idx]
            p2_high = highs[p2_idx]
            if p1_high <= p2_high: continue

            m = (p2_high - p1_high) / (p2_idx - p1_idx)
            b = p1_high - m * p1_idx

            ihlal_var = False
            for k in range(p1_idx + 1, current_idx): 
                if highs[k] > (m * k + b): 
                    ihlal_var = True
                    break
            if ihlal_var: continue

            cizgi_dun = m * (current_idx - 1) + b
            cizgi_bugun = m * current_idx + b

            if prev_close <= cizgi_dun and current_close > cizgi_bugun:
                if current_close <= (p1_high * 1.10): # Marjı biraz esnettik
                    return "KIRDI", {"Fiyat": round(current_close, 2), "Direnç": round(cizgi_bugun, 2)}
            elif current_close <= cizgi_bugun and current_close >= (cizgi_bugun * 0.98):
                return "YAKIN", {"Fiyat": round(current_close, 2), "Direnç": round(cizgi_bugun, 2)}
    return None, {}

def main():
    # ... (TICKERS Listesi aynı kalacak, buraya yapıştırmıyorum kalabalık olmasın diye) ...
    
    memory = load_memory()
    kiranlar = []
    yaklasanlar = []
    
    print("Geniş Açı Analiz Basliyor (2 Yıllık Veri)...")
    
    for ticker in TICKERS:
        try:
            # 2 Yıllık veri çekiyoruz
            df = yf.download(f"{ticker}.IS", period="2y", progress=False)
            if df is None or df.empty: continue
            
            status, details = find_downtrend_status(df)
            
            if status == "KIRDI":
                if memory.get(ticker) != "KIRDI":
                    kiranlar.append(f"✅ *{ticker}* (Fiyat: {details['Fiyat']} / Direnc: {details['Direnc']})")
                    memory[ticker] = "KIRDI"
            elif status == "YAKIN":
                if ticker not in memory:
                    yaklasanlar.append(f"⏳ *{ticker}* (Fiyat: {details['Fiyat']} / Direnc: {details['Direnc']})")
                    memory[ticker] = "YAKIN"
        except:
            continue

    if kiranlar or yaklasanlar:
        rapor = "🔔 *GENİŞ AÇI DÜŞEN TREND ANALİZİ* 🔔\n\n"
        if kiranlar:
            rapor += "🚀 *KIRILIM GERÇEKLEŞENLER*\n" + "\n".join(kiranlar) + "\n\n"
        if yaklasanlar:
            rapor += "👀 *KIRILIMA ÇOK YAKINLAR (%2)*\n" + "\n".join(yaklasanlar)
        
        send_telegram_message(rapor)
        save_memory(memory)
        print("Rapor gonderildi.")
    else:
        print("Yeni sinyal yok.")

if __name__ == "__main__":
    main()
