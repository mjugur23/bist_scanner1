import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import json  # Hafıza dosyası için eklendi
from scipy.signal import argrelextrema
import warnings

warnings.filterwarnings('ignore')

# --- TELEGRAM VE HAFIZA AYARLARI ---
# Token ve ID'yi kodun içinde doğrudan bıraktım (senin kodunda olduğu gibi)
TOKEN = "8625940807:AAE_bsrBsj7lojRv6Dhbq0uJjY_kaz7RwMo"
CHAT_ID = "5886003690"
MEMORY_FILE = "dusen_hafiza.json"

def load_memory():
    """Hafıza dosyasını okur."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_memory(new_stocks, current_memory):
    """Yeni bulunan hisseleri hafızaya ekler."""
    updated_memory = list(set(current_memory + new_stocks))
    with open(MEMORY_FILE, "w") as f:
        json.dump(updated_memory, f)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram hatası: {e}")

# --- YENİ VE AKILLI DÜŞEN KIRILIM MOTORU ---
def find_downtrend_breakout(df, window=5, min_distance=10):
    if df is None or len(df) < 30:
        return False, {}
        
    high_col = 'High' if 'High' in df.columns else 'high'
    close_col = 'Close' if 'Close' in df.columns else 'close'
    
    highs = df[high_col].values
    closes = df[close_col].values
    dates = df.index
    
    pivot_indices = []
    for i in range(window, len(highs) - window):
        if highs[i] == max(highs[i - window : i + window + 1]):
            if not pivot_indices or i - pivot_indices[-1] >= 3:
                pivot_indices.append(i)

    if len(pivot_indices) < 2:
        return False, {}

    current_idx = len(highs) - 1
    current_close = closes[current_idx]
    prev_close = closes[current_idx - 1]

    for i in range(len(pivot_indices) - 2, -1, -1):
        for j in range(len(pivot_indices) - 1, i, -1):
            p1_idx = pivot_indices[i]
            p2_idx = pivot_indices[j]

            if p2_idx - p1_idx < min_distance:
                continue

            p1_high = highs[p1_idx]
            p2_high = highs[p2_idx]

            if p1_high <= p2_high:
                continue

            m = (p2_high - p1_high) / (p2_idx - p1_idx)
            b = p1_high - m * p1_idx

            ihlal_var = False
            for k in range(p1_idx + 1, current_idx): 
                cizgi_degeri = m * k + b
                if highs[k] > cizgi_degeri: 
                    ihlal_var = True
                    break

            if ihlal_var:
                continue

            cizgi_dun = m * (current_idx - 1) + b
            cizgi_bugun = m * current_idx + b

            if prev_close <= cizgi_dun and current_close > cizgi_bugun:
                if current_close > (p1_high * 1.05):
                     continue

                details = {
                    "1. Tepe Tarihi": dates[p1_idx].strftime('%Y-%m-%d'),
                    "1. Tepe Fiyatı": round(p1_high, 2),
                    "2. Tepe Tarihi": dates[p2_idx].strftime('%Y-%m-%d'),
                    "2. Tepe Fiyatı": round(p2_high, 2),
                    "Kırılım Fiyatı": round(current_close, 2),
                    "Direnç Sınırı": round(cizgi_bugun, 2)
                }
                return True, details

    return False, {}

def main():
    TICKERS = [
       "THYAO","ASELS","ISCTR","AKBNK","YKBNK","KCHOL","TUPRS","TRALT","SASA","ASTOR", 
       "GARAN","PGSUS","EREGL","BIMAS","SAHOL","EKGYO","TCELL","SISE","HALKB","PEKGY",
       "KTLEV","ATATR","TERA","TEHOL","MGROS","FROTO","NETCD","DSTKF","KRDMD","VAKBN",
       "TTKOM","CVKMD","PETKM","GUBRF","DOFRB","TOASO","AEFES","PAHOL","BRSAN","PASEU",
       "MEYSU","KLRHO","ENKAI","CANTE","SARKY","CWENE","IEYHO","ALARK","MANAS","TRMET",
       "TAVHL","KONTR","ULKER","AKHAN","UCAYM","MEGMT","MARMR","EMPAE","MIATK","BTCIM",
       "KUYAS","ADESE","ALVES","ZERGY","ARFYE","BESTE","FRMPL","FENER","CIMSA","TURSG",
       "OYAKC","ALTNY","EUREN","SMRVA","AKSEN","HEDEF","OTKAR","ECILC","DOAS","CCOLA",
       "TSKB","TUKAS","PSGYO","HEKTS","HDFGS","BINHO","OBAMS","SDTTR","ARCLK","EUPWR",
       "SKBNK","BULGS","VAKFA","KATMR","PATEK","QUAGR","ODAS","GSRAY","ZGYO","ISMEN",
       "BERA","ECOGR","TKFEN","ESEN","SURGY","BSOKE","BMSTL","GENKM","SVGYO","PAPIL",
       "TRENJ","GENIL","DAPGM","MAVI","GZNMI","YEOTK","MAGEN","SOKM","GLRMK","GIPTA",
       "ODINE","IZENR","BRYAT","EFOR","ALKLC","MPARK","IHLAS","GESAN","MOPAS","VAKFN",
       "FONET","SEGMN","A1CAP","ISGSY","GUNDG","EDATA","ISKPL","HLGYO","FORMT","RALYH",
       "DOHOL","VSNMD","PRKAB","AKFIS","KBORU","TCKRC","ENJSA","AKCNS","EMKEL","ESCOM",
       "TSPOR","ANSGR","ALBRK","AKSA","ZOREN","ATATP","CEMAS","LYDHO","KLGYO","TRHOL",
       "TABGD","TATEN","LILAK","CEMZY","FORTE","IZFAS","LINK","GEREL","ONCSM","ARDYZ",
       "YYAPI","AYGAZ","RGYAS","USAK","BAHKM","ENERY","ESCAR","BURCE","DERHL","RYSAS",
       "MEKAG","KCAER","IMASM","AGHOL","KAYSE","KZBGY","GRSEL","ARSAN","LMKDC","TTRAK",
       "ECZYT","AHGAZ","KARSN","ALGYO","TUREX","CGCAM","POLTK","TMPOL","VESTL","MRGYO",
       "GRTHO","BALSU","ENTRA","KLYPV","RUBNS","GWIND","INFO","AKFYE","SAFKR","TEKTU",
       "SNGYO","ANHYT","SELVA","FZLGY","REEDR","YYLGD","ALKA","FRIGO","ERCB","OZATD",
       "ISDMR","ENSRI","SMART","LOGO","BMSCH","GOKNR","CLEBI","DITAS","YAPRK","MERCN",
       "KRDMA","BORLS","TRGYO","GENTS","RTALB","SEGYO","TARKM","ADGYO","SRVGY","MERKO",
       "DURKN","SMRTG","BINBN","AYDEM","BLUME","MOGAN","EGEEN","AGROT","DMRGD","VKGYO",
       "TNZTP","ARMGD","NTGAZ","GMTAS","BRKVY","AKGRT","TUCLK","LIDER","RUZYE","IHAAS",
       "AVOD","DCTTR","EKOS","OTTO","TMSN","RYGYO","GLYHO","ADEL","LYDYE","TKNSA",
       "BVSAN","BAGFS","KLKIM","KAPLM","MAKTK","MOBTL","BARMA","SELEC","AGESA","ONRYT",
       "BORSK","PRKME","DOFER","PNLSN","EGGUB","EGEGY","YUNSA","PKENT","ICUGS","NATEN",
       "LRSHO"
    ]
    
    hafiza = load_memory()
    yeni_bulunanlar_hisse_kodlari = []
    mesajlar_listesi = []
    
    print("Düşen Kırılım Taraması Başlıyor...")
    
    for ticker in TICKERS:
        # Eğer hisse hafızada varsa tarama yapmadan geç
        if ticker in hafiza:
            continue
            
        try:
            df = yf.download(f"{ticker}.IS", period="6mo", progress=False)
            if df.empty: continue
            
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            is_breakout, details = find_downtrend_breakout(df)
            if is_breakout:
                mesaj = f"📉 *DÜŞEN KIRILIMI YAKALANDI!*\n"
                mesaj += f"📌 Hisse: *{ticker}*\n"
                mesaj += f"💵 Kırılım Fiyatı: {details['Kırılım Fiyatı']} TL\n"
                mesaj += f"🚧 Direnç: {details['Direnç Sınırı']} TL\n"
                
                mesajlar_listesi.append(mesaj)
                yeni_bulunanlar_hisse_kodlari.append(ticker)
                
        except Exception as e:
            continue

    if mesajlar_listesi:
        # Mesajları gönder
        for msg in mesajlar_listesi:
            send_telegram_message(msg)
        
        # Hafızayı güncelle ve kaydet
        save_memory(yeni_bulunanlar_hisse_kodlari, hafiza)
        print(f"Tarama bitti, {len(mesajlar_listesi)} yeni hisse gönderildi ve hafızaya alındı.")
    else:
        print("Yeni bir kırılım bulunamadı veya bulunanlar zaten hafızada.")

if __name__ == "__main__":
    main()
