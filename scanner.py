import os
import json
import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
from tvDatafeed import TvDatafeed, Interval

# --- TELEGRAM AYARLARI ---
# Token ve Chat ID'yi GitHub Secrets'tan (veya bilgisayarındaki ortam değişkenlerinden) güvenle çeker.
TOKEN = os.environ.get("8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk")
CHAT_ID = os.environ.get("5886003690")

def send_telegram_message(message):
    # url kısmında senin token'ın açıkça yazıyordu, onu sildik ve değişkene bağladık:
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram hatasi: {e}")


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
    """Hafızayı kalıcı olarak yükler (Günlük sıfırlama İPTAL edildi)."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
                # Eğer eski versiyondan kalma "alerts" key'i varsa sadece onu al
                return data.get("alerts", data) if isinstance(data, dict) else {}
        except:
            pass
    return {}

def save_memory(memory_dict):
    """Hafızayı kalıcı olarak dosyaya kaydeder."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_dict, f)

def check_turtle(df, symbol):
    """Kıvanç Özbilgiç - TuTCI (Turtle Trade Channels) Birebir Python Çevirisi"""
    if df is None or len(df) < 30:
        return "FLAT", ""

    # TradingView'daki highest(high, 20) ve lowest(low, 10) hesaplamaları
    df['Donchian_High'] = df['high'].rolling(window=20).max()
    df['Donchian_Low'] = df['low'].rolling(window=10).min()

    # Pine Script'teki upper[1] ve sdown[1] (Bir önceki barın değerleri)
    df['upper_1'] = df['Donchian_High'].shift(1)
    df['sdown_1'] = df['Donchian_Low'].shift(1)

    # Sinyalleri belirle (buySignal = high >= upper[1] | buyExit = low <= sdown[1])
    df['buySignal'] = df['high'] >= df['upper_1']
    df['buyExit'] = df['low'] <= df['sdown_1']

    state = "FLAT" # Hissenin anlık durumu (LONG=Alımda, FLAT=Nötr)
    fresh_signal = False
    
    # Geçmişten bugüne doğru TradingView gibi bar bar simülasyon yapıyoruz
    for i in range(20, len(df)): 
        # Eğer AL koşulu sağlandıysa ve hisse zaten alımda değilse
        if df['buySignal'].iloc[i] and state != "LONG":
            state = "LONG"
            if i == len(df) - 1: # Eğer bu LONG'a geçiş TAM OLARAK BUGÜN (son barda) olduysa!
                fresh_signal = True
        
        # Eğer ÇIKIŞ (Stop) koşulu sağlandıysa ve hisse alımdaydıysa
        elif df['buyExit'].iloc[i] and state == "LONG":
            state = "FLAT"

    # Bugünün (Son barın) verileri
    last_close = df['close'].iloc[-1]
    last_upper = df['upper_1'].iloc[-1]

    # 1. DURUM: Taptaze AL sinyali (Grafikte ilk yeşil okun yandığı an)
    if fresh_signal:
        return "NEW", f"🚀 **{symbol}** - Fiyat: {last_close:.2f} (Zirve: {last_upper:.2f})"
    
    # YENİ DURUM: Zaten AL sinyali vermiş ve trendine devam ediyor (Sessiz kalması için)
    if state == "LONG":
        return "LONG", ""
    
    # 2. DURUM: YAKIN sinyali (Hisse henüz AL'a geçmediyse ve dirence çok yakınsa)
    if state == "FLAT" and pd.notna(last_upper) and last_close < last_upper:
        distance = ((last_upper - last_close) / last_close) * 100
        if 0 < distance <= 1.5:
            return "NEAR", f"👀 **{symbol}** - Mesafe: %{distance:.2f} (Direnç: {last_upper:.2f})"
            
    return "FLAT", ""

def scan_symbol(symbol):
    try:
        # Geçmişi doğru okuyabilmesi için n_bars=100 olarak güncellendi!
        df = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_daily, n_bars=100)
        status, msg = check_turtle(df, symbol)
        return symbol, status, msg
    except Exception as e:
        return symbol, "FLAT", ""

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
        prev_status = memory.get(symbol, "FLAT")
        
        # Eğer YENİ sinyal varsa ve hafızada zaten LONG (alımda) DEĞİLSE
        if status == "NEW" and prev_status != "LONG":
            turtle_al.append(msg)
            memory[symbol] = "LONG"
            updated = True
            
        # Eğer hisse ALIMDAYSA ama bugün 'fresh_signal' vermediyse bile hafızayı LONG tut
        elif status == "LONG" and prev_status != "LONG":
            memory[symbol] = "LONG"
            updated = True
            
        # Eğer YAKIN durumu varsa
        elif status == "NEAR":
            if prev_status != "NEAR" and prev_status != "LONG":
                turtle_yakin.append(msg)
                memory[symbol] = "NEAR"
                updated = True
                
        # Eğer trend bozulduysa / stop olduysa (FLAT), hafızayı sıfırla ki ileride tekrar AL verebilsin
        elif status == "FLAT" and prev_status != "FLAT":
            memory[symbol] = "FLAT"
            updated = True

    # Mesajları derle ve gönder
    if turtle_al or turtle_yakin:
        final_msg = ""
        if turtle_al:
            final_msg += "🚨 **TURTLE AL**\n\n" + "\n".join(turtle_al) + "\n\n"
        if turtle_yakin:
            final_msg += "🔔 **TURTLE (YAKIN)**\n\n" + "\n".join(turtle_yakin) + "\n\n"
        
        send_telegram(final_msg)
        
    # Hafızada yeni bir kayıt/değişiklik oluştuysa defteri kaydet
    if updated:
        save_memory(memory)

if __name__ == "__main__":
    main()
