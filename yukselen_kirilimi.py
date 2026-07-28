import os
import requests
import yfinance as yf
import pandas as pd
import numpy as np
import json
import warnings

warnings.filterwarnings('ignore')

# --- TELEGRAM VE HAFIZA AYARLARI ---
# GITHUB'A YÜKLERKEN BURAYI BOŞ BIRAK VE GITHUB SECRETS KULLAN!
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8839652305:AAE7x_DriVyFis-ceROoxJGuwdX9EwhFYCc")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "5886003690")
MEMORY_FILE = "yukselen_hafiza.json" # Hafıza dosyası çakışmasın diye adını değiştirdik

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

# --- ANALİZ MOTORU (1 YILLIK YÜKSELEN TREND/DESTEK KIRILIMI) ---
def find_uptrend_status(df, window=7, min_distance=15):
    if df is None or len(df) < 40:
        return None, {}
        
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    low_col = 'Low' if 'Low' in df.columns else 'low'
    close_col = 'Close' if 'Close' in df.columns else 'close'
    
    lows = df[low_col].values
    closes = df[close_col].values
    
    # 1. Dip (Pivot) noktalarını bul (Zirveler yerine diplere bakıyoruz)
    pivot_indices = []
    for i in range(window, len(lows) - window):
        if lows[i] == min(lows[i - window : i + window + 1]):
            if not pivot_indices or i - pivot_indices[-1] >= 4:
                pivot_indices.append(i)

    if len(pivot_indices) < 2:
        return None, {}

    current_idx = len(lows) - 1
    current_close = closes[current_idx]
    prev_close = closes[current_idx - 1]

    for i in range(len(pivot_indices) - 2, -1, -1):
        for j in range(len(pivot_indices) - 1, i, -1):
            p1_idx = pivot_indices[i]
            p2_idx = pivot_indices[j]
            if p2_idx - p1_idx < min_distance: continue

            p1_low = lows[p1_idx]
            p2_low = lows[p2_idx]
            
            # Yükselen trend olması için ikinci dip, birinci dipten YUKARIDA olmalı
            if p1_low >= p2_low: continue

            m = (p2_low - p1_low) / (p2_idx - p1_idx)
            b = p1_low - m * p1_idx

            # Aradaki barlarda bu destek çizgisinin belirgin şekilde ihlal edilip edilmediğini kontrol et
            ihlal_var = False
            for k in range(p1_idx + 1, current_idx): 
                if lows[k] < (m * k + b) * 0.99: # %1'lik ufak sarkmaları tolere edebiliriz
                    ihlal_var = True
                    break
            if ihlal_var: continue

            cizgi_dun = m * (current_idx - 1) + b
            cizgi_bugun = m * current_idx + b

            # KIRILIM KOŞULU: Dün çizginin (desteğin) üstündeyken, bugün altına sarktıysa
            if prev_close >= cizgi_dun and current_close < cizgi_bugun:
                if current_close >= (p1_low * 0.92): # Dibe göre %8'den fazla çakılmamışsa (Marj)
                    return "KIRDI", {"Fiyat": round(current_close, 2), "Destek": round(cizgi_bugun, 2)}
            
            # YAKIN KOŞULU: Fiyat desteğe %2 kadar yaklaştıysa ve hala üstündeyse
            elif current_close >= cizgi_bugun and current_close <= (cizgi_bugun * 1.02):
                return "YAKIN", {"Fiyat": round(current_close, 2), "Destek": round(cizgi_bugun, 2)}
                
    return None, {}

def main():
    # Senin belirlediğin geniş hisse havuzu
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
        "BORSK","PRKME","DOFER","PNLSN","EGGUB","EGEGY","YUNSA","PKENT","ICUGS","NATEN","LRSHO"
    ]
    
    memory = load_memory()
    kiranlar = []
    yaklasanlar = []
    
    print("1 Yıllık Yükselen Trend (Short) Analizi Başlıyor...")
    
    for ticker in TICKERS:
        try:
            df = yf.download(f"{ticker}.IS", period="1y", progress=False)
            if df is None or df.empty: continue
            
            status, details = find_uptrend_status(df)
            
            if status == "KIRDI":
                if memory.get(ticker) != "KIRDI":
                    kiranlar.append(f"🔻 *{ticker}* (Fiyat: {details['Fiyat']} / Destek: {details['Destek']})")
                    memory[ticker] = "KIRDI"
            elif status == "YAKIN":
                if ticker not in memory:
                    yaklasanlar.append(f"⚠️ *{ticker}* (Fiyat: {details['Fiyat']} / Destek: {details['Destek']})")
                    memory[ticker] = "YAKIN"
        except:
            continue

    if kiranlar or yaklasanlar:
        rapor = "🚨 *YÜKSELEN TREND (SHORT) SİNYALLERİ* 🚨\n\n"
        if kiranlar:
            rapor += "📉 *DESTEĞİ AŞAĞI KIRANLAR*\n" + "\n".join(kiranlar) + "\n\n"
        if yaklasanlar:
            rapor += "👀 *DESTEĞE ÇOK YAKLAŞANLAR (%2)*\n" + "\n".join(yaklasanlar)
        
        send_telegram_message(rapor)
        save_memory(memory)
        print("Sinyaller gönderildi.")
    else:
        print("Yeni sinyal bulunamadı.")

if __name__ == "__main__":
    main()
