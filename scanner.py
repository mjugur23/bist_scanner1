import os
import json
import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
from tvDatafeed import TvDatafeed, Interval

# ================= AYARLAR =================
BOT_TOKEN = "8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk"
CHAT_ID = "5886003690"
MAX_WORKERS = 2 
MEMORY_FILE = "hafiza.json"

# Kendi taradığın hisse listesini (symbols) buraya eklemeyi unutma
symbols = [
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
# ===========================================

tv = TvDatafeed()

def load_memory():
    """Bugünün hafızasını yükler. Gün değişmişse hafızayı sıfırlar."""
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
                if data.get("date") == today:
                    return data.get("alerts", {})
        except:
            pass
    return {}

def save_memory(alerts_dict):
    """Hafızayı dosyaya kaydeder."""
    today = datetime.now().strftime("%Y-%m-%d")
    with open(MEMORY_FILE, "w") as f:
        json.dump({"date": today, "alerts": alerts_dict}, f)

def check_turtle(df, symbol):
    """Sadece Turtle stratejisini hesaplar."""
    if df is None or len(df) < 21:
        return "NONE", ""
    
    # Bugün hariç son 20 günün en yükseği
    recent_high = df['high'].iloc[-21:-1].max()
    last_close = df['close'].iloc[-1]
    
    # 1. Durum: Kırılım Gerçekleşti (AL)
    if last_close > recent_high:
        return "NEW", f"🚀 **{symbol}** - Fiyat: {last_close:.2f} (Zirve: {recent_high:.2f})"
    
    # 2. Durum: Dirence Yakın (YAKIN)
    distance = ((recent_high - last_close) / last_close) * 100
    if 0 < distance <= 1.5:
        return "NEAR", f"👀 **{symbol}** - Mesafe: %{distance:.2f} (Direnç: {recent_high:.2f})"
        
    return "NONE", ""

def scan_symbol(symbol):
    try:
        df = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_daily, n_bars=30)
        status, msg = check_turtle(df, symbol)
        return symbol, status, msg
    except Exception as e:
        return symbol, "NONE", ""

def send_telegram(message):
    url = f"https://api.telegram.org/bot8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk/sendMessage"
    payload = {"chat_id": 5886003690, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

def main():
    memory = load_memory()
    updated = False
    
    turtle_al = []
    turtle_yakin = []
    
    # 2 Worker ile hızlı tarama
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = executor.map(scan_symbol, symbols)
        
    for symbol, status, msg in results:
        if status == "NONE":
            continue
            
        prev_status = memory.get(symbol)
        
        # Eğer bugün zaten "AL" verdiysek, bir daha asla rahatsız etme
        if prev_status == "NEW":
            continue
            
        # Eğer bugün "YAKIN" verdiysek ve hala "YAKIN" durumundaysa, tekrar atma
        if status == "NEAR" and prev_status == "NEAR":
            continue
            
        # Yeni bir gelişme varsa listeye ekle ve hafızaya yaz
        if status == "NEW":
            turtle_al.append(msg)
            memory[symbol] = "NEW"
            updated = True
        elif status == "NEAR":
            turtle_yakin.append(msg)
            memory[symbol] = "NEAR"
            updated = True

    # Mesajları derle ve gönder
    if turtle_al or turtle_yakin:
        final_msg = ""
        if turtle_al:
            final_msg += "🚨 **TURTLE AL**\n\n" + "\n".join(turtle_al) + "\n\n"
        if turtle_yakin:
            final_msg += "🔔 **TURTLE (YAKIN)**\n\n" + "\n".join(turtle_yakin) + "\n\n"
        
        send_telegram(final_msg)
        
    # Hafızada yeni bir kayıt oluştuysa defteri kaydet
    if updated:
        save_memory(memory)

if __name__ == "__main__":
    main()
