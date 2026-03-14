import sys
import os
import requests
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from concurrent.futures import ThreadPoolExecutor
import time

# Klasör yolu ayarı
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scanners.turtle_logic import check_turtle
from scanners.supertrend_logic import check_supertrend

# ======================
# CONFIG & CREDENTIALS
# ======================
BOT_TOKEN = "8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk"
CHAT_ID = "5886003690"
MAX_WORKERS = 2 

# Sonuçları toplamak için global listeler
turtle_new = []
turtle_near = []
st_new = []
st_near = []

def send_telegram(msg):
    url = f"https://api.telegram.org/bot8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk/sendMessage"
    payload = {"chat_id": 5886003690, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Hatası: {e}")

def scan_single_symbol(tv, symbol):
    """Her bir hisse için paralel çalışacak fonksiyon"""
    try:
        # BIST ön eki kontrolü
        full_symbol = f"BIST:{symbol}" if ":" not in symbol else symbol
        df = tv.get_hist(symbol=full_symbol, exchange="", interval=Interval.in_daily, n_bars=100)
        
        if df is None or df.empty or len(df) < 35:
            return

        clean_name = symbol.split(':')[-1]

        # 1. TURTLE KONTROLÜ
        t_status, t_msg = check_turtle(df, clean_name)
        if t_status == "NEW":
            turtle_new.append(t_msg)
        elif t_status == "NEAR":
            turtle_near.append(t_msg)

        # 2. SUPERTREND KONTROLÜ
        s_status, s_msg = check_supertrend(df, clean_name)
        if s_status == "NEW":
            st_new.append(s_msg)
        elif s_status == "NEAR":
            st_near.append(s_msg)

    except Exception as e:
        print(f"{symbol} taranırken hata: {e}")

def run_scanner():
    # --- KRİTİK: LİSTELERİ SIFIRLA ---
    global turtle_new, turtle_near, st_new, st_near
    turtle_new, turtle_near, st_new, st_near = [], [], [], []
    
    start_time = time.time()
    tv = TvDatafeed()
    
    # Buraya 500'lük tam listenizi ekleyebilirsiniz
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

    print(f"Tarama {len(symbols)} hisse için başladı...")

    # Paralel İşleme
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(lambda s: scan_single_symbol(tv, s), symbols)

    # --- MESAJ GÖNDERİMİ ---
    # Turtle Mesajı
    if turtle_new or turtle_near:
        t_msg = ""
        if turtle_new:
            t_msg += "🚨 **TURTLE TAZE KIRILIM**\n\n" + "\n".join(turtle_new) + "\n\n"
        if turtle_near:
            t_msg += "🔔 **TURTLE PUSU (YAKIN)**\n\n" + "\n".join(turtle_near)
        send_telegram(t_msg)

    # Supertrend Mesajı
    if st_new or st_near:
        s_msg = ""
        if st_new:
            s_msg += "✨ **SUPERTREND TAZE AL**\n\n" + "\n".join(st_new) + "\n\n"
        if st_near:
            s_msg += "🕯️ **SUPERTREND PUSU**\n\n" + "\n".join(st_near)
        send_telegram(s_msg)

    print(f"Tarama bitti. Süre: {int(time.time() - start_time)} saniye.")

if __name__ == "__main__":
    run_scanner()
