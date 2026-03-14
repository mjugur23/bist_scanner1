import sys
import os
import requests
import time
import pandas as pd
from tvDatafeed import TvDatafeed, Interval

# Modül yolları (scanners klasöründeki dosyaları çekmek için)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scanners.turtle_logic import check_turtle
from scanners.supertrend_logic import check_supertrend

# ======================
# AYARLAR (CONFIG)
# ======================
BOT_TOKEN = "8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk"
CHAT_ID = "5886003690"

# Global sonuç listeleri
turtle_new = []
turtle_near = []
st_new = []
st_near = []
failed_symbols = [] # Veri alınamayan hisseler burada toplanacak

def send_telegram(msg):
    url = f"https://api.telegram.org/bot8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk/sendMessage"
    payload = {"chat_id": 5886003690, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e: 
        print(f"Telegram Hatası: {e}")

def scan_single_symbol(tv, symbol):
    """Sırayla tek bir hisseyi tarayan fonksiyon"""
    global turtle_new, turtle_near, st_new, st_near, failed_symbols
    try:
        # Hissenin başına BIST: ekle
        full_symbol = f"BIST:{symbol}" if ":" not in symbol else symbol
        df = tv.get_hist(symbol=full_symbol, exchange="", interval=Interval.in_daily, n_bars=100)
        
        # Eğer veri gelmediyse veya yeni halka arz ise listeye ekle ve çık
        if df is None or df.empty or len(df) < 35: 
            failed_symbols.append(symbol)
            return

        clean_name = symbol.split(':')[-1]

        # 1. TURTLE TARAMASI
        t_status, t_msg = check_turtle(df, clean_name)
        if t_status == "NEW": turtle_new.append(t_msg)
        elif t_status == "NEAR": turtle_near.append(t_msg)

        # 2. SUPERTREND TARAMASI
        s_status, s_msg = check_supertrend(df, clean_name)
        if s_status == "NEW": st_new.append(s_msg)
        elif s_status == "NEAR": st_near.append(s_msg)

    except Exception as e: 
        failed_symbols.append(symbol)
        print(f"{symbol} taranırken hata oluştu: {e}")

def run_scanner():
    global turtle_new, turtle_near, st_new, st_near, failed_symbols
    
    # Her tarama başında eski listeleri tertemiz yap
    turtle_new.clear()
    turtle_near.clear()
    st_new.clear()
    st_near.clear()
    failed_symbols.clear()
    
    start_time = time.time()
    tv = TvDatafeed()
    
    # 500'lük tam hisse listeni buraya koyabilirsin
    symbols = BIST100_SYMBOLS = [
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

    print(f"Tarama {len(symbols)} hisse için SIRALI (tek tek) başladı...\n")
    
    # SIRALI TARAMA DÖNGÜSÜ
    for index, symbol in enumerate(symbols, 1):
        print(f"[{index}/{len(symbols)}] Kontrol ediliyor: {symbol}...")
        scan_single_symbol(tv, symbol)
        time.sleep(0.5) # TradingView'ı yormamak için yarım saniye mola

    # ======================
    # MESAJLARI GÖNDER
    # ======================
    t_output = ""
    if turtle_new: t_output += "🚨 **TURTLE YENİ AL**\n\n" + "\n".join(turtle_new) + "\n\n"
    if turtle_near: t_output += "🔔 **TURTLE PUSU**\n\n" + "\n".join(turtle_near)
    if t_output: send_telegram(t_output)

    s_output = ""
    if st_new: s_output += "✨ **SUPERTREND AL**\n\n" + "\n".join(st_new) + "\n\n"
    if st_near: s_output += "🕯️ **SUPERTREND PUSU**\n\n" + "\n".join(st_near)
    if s_output: send_telegram(s_output)

    # ======================
    # TARAMA RAPORU
    # ======================
    end_time = time.time()
    print(f"\n✅ Tarama tamamlandı. Toplam Süre: {int(end_time - start_time)} saniye.")
    
    # Eğer hatalı/eksik hisse varsa ekrana yazdır (Telegram'a atmaz, sadece logda görünür)
    if failed_symbols:
        print(f"⚠️ DİKKAT: {len(failed_symbols)} hisseden veri alınamadı veya bar sayısı yetersiz:")
        print(", ".join(failed_symbols))

if __name__ == "__main__":
    run_scanner()
