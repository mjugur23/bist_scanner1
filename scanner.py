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
"A1CAP","A1YEN","ACSEL","ADEL","ADESE","ADGYO","AEFES","AFYON",
"AGESA","AGHOL","AGROT","AGYO","AHGAZ","AHSGY","AKBNK","AKCNS",
"AKENR","AKFGY","AKFIS","AKFYE","AKGRT","AKHAN","AKMGY","AKSA",
"AKSEN","AKSGY","AKSUE","AKYHO","ALARK","ALBRK","ALCAR","ALCTL",
"ALFAS","ALGYO","ALKA","ALKIM","ALKLC","ALMAD","ALTNY","ALVES",
"ANELE","ANGEN","ANHYT","ANSGR","ARASE","ARCLK","ARDYZ","ARENA",
"ARFYE","ARMGD","ARSAN","ARTMS","ARZUM","ASELS","ASGYO","ASTOR",
"ASUZU","ATAGY","ATAKP","ATATP","ATATR","ATEKS","ATLAS","ATSYH",
"AVGYO","AVHOL","AVOD","AVPGY","AVTUR","AYCES","AYDEM","AYEN",
"AYES","AYGAZ","AZTEK","BAGFS","BAHKM","BAKAB","BALAT","BALSU",
"BANVT","BARMA","BASCM","BASGZ","BAYRK","BEGYO","BERA","BESLR",
"BESTE","BEYAZ","BFREN","BIENY","BIGCH","BIGEN","BIGTK","BIMAS",
"BINBN","BINHO","BIOEN","BIZIM","BJKAS","BLCYT","BLUME","BMSCH",
"BMSTL","BNTAS","BOBET","BORLS","BORSK","BOSSA","BRISA","BRKO",
"BRKSN","BRKVY","BRLSM","BRMEN","BRSAN","BRYAT","BSOKE","BTCIM",
"BUCIM","BULGS","BURCE","BURVA","BVSAN","BYDNR","CANTE","CASA",
"CATES","CCOLA","CELHA","CEMAS","CEMTS","CEMZY","CEOEM","CGCAM",
"CIMSA","CLEBI","CMBTN","CMENT","CONSE","COSMO","CRDFA","CRFSA",
"CUSAN","CVKMD","CWENE","DAGHL","DAGI","DAPGM","DARDL","DCTTR",
"DENGE","DERHL","DERIM","DESA","DESPC","DEVA","DGATE","DGGYO",
"DGNMO","DIRIT","DITAS","DMRGD","DMSAS","DNISI","DOAS","DOBUR",
"DOCO","DOFER","DOFRB","DOGUB","DOHOL","DOKTA","DSTKF","DUNYH",
"DURDO","DURKN","DYOBY","DZGYO","EBEBK","ECILC","ECOGR","ECZYT",
"EDATA","EDIP","EFOR","EFORC","EGEEN","EGEGY","EGEPO","EGGUB",
"EGPRO","EGSER","EKGYO","EKIZ","EKOS","EKSUN","ELITE","EMKEL",
"EMNIS","EMPAE","ENDAE","ENERY","ENJSA","ENKAI","ENSRI","ENTRA",
"EPLAS","ERBOS","ERCB","EREGL","ERSU","ESCAR","ESCOM","ESEN",
"ETILR","ETYAT","EUHOL","EUKYO","EUPWR","EUREN","EUYO","EYGYO",
"FADE","FENER","FLAP","FMIZP","FONET","FORMT","FORTE","FRIGO",
"FRMPL","FROTO","FZLGY","GARAN","GARFA","GATEG","GEDIK","GEDZA",
"GENIL","GENKM","GENTS","GEREL","GESAN","GIPTA","GLBMD","GLCVY",
"GLRMK","GLRYH","GLYHO","GMTAS","GOKNR","GOLTS","GOODY","GOZDE",
"GRNYO","GRSEL","GRTHO","GRTRK","GSDDE","GSDHO","GSRAY","GUBRF",
"GUNDG","GWIND","GZNMI","HALKB","HATEK","HATSN","HDFGS","HEDEF",
"HEKTS","HKTM","HLGYO","HOROZ","HRKET","HTTBT","HUBVC","HUNER",
"HURGZ","ICBCT","ICUGS","IDEAS","IDGYO","IEYHO","IHAAS","IHEVA",
"IHGZT","IHLAS","IHLGM","IHYAY","IMASM","INDES","INFO","INGRM",
"INTEK","INTEM","INVEO","INVES","IPEKE","ISATR","ISBIR","ISBTR",
"ISCTR","ISDMR","ISFIN","ISGSY","ISGYO","ISKPL","ISKUR","ISMEN",
"ISSEN","ISYAT","ITTFH","IZENR","IZFAS","IZINV","IZMDC","JANTS",
"KAPLM","KAREL","KARSN","KARTN","KARYE","KATMR","KAYSE","KBORU",
"KCAER","KCHOL","KENT","KERVN","KERVT","KFEIN","KGYO","KIMMR",
"KLGYO","KLKIM","KLMSN","KLNMA","KLRHO","KLSER","KLSYN","KLYPV",
"KMPUR","KNFRT","KOCMT","KONKA","KONTR","KONYA","KOPOL","KORDS",
"KOTON","KOZAA","KOZAL","KRDMA","KRDMB","KRDMD","KRGYO","KRONT",
"KRPLS","KRSTL","KRTEK","KRVGD","KSTUR","KTLEV","KTSKR","KUTPO",
"KUVVA","KUYAS","KZBGY","KZGYO","LIDER","LIDFA","LILAK","LINK",
"LKMNH","LMKDC","LOGO","LRSHO","LUKSK","LXGYO","LYDHO","LYDYE",
"MAALT","MACKO","MAGEN","MAKIM","MAKTK","MANAS","MARBL","MARKA",
"MARMR","MARTI","MAVI","MCARD","MEDTR","MEGAP","MEGMT","MEKAG",
"MEPET","MERCN","MERIT","MERKO","METRO","METUR","MEYSU","MGROS",
"MHRGY","MIATK","MIPAZ","MMCAS","MNDRS","MNDTR","MOBTL","MOGAN",
"MOPAS","MPARK","MRGYO","MRSHL","MSGYO","MTRKS","MTRYO","MZHLD",
"NATEN","NETAS","NETCD","NIBAS","NTGAZ","NTHOL","NUGYO","NUHCM",
"OBAMS","OBASE","ODAS","ODINE","OFSYM","ONCSM","ONRYT","ORCAY",
"ORGE","ORMA","OSMEN","OSTIM","OTKAR","OTTO","OYAKC","OYAYO",
"OYLUM","OYYAT","OZATD","OZGYO","OZKGY","OZRDN","OZSUB","OZYSR",
"PAGYO","PAHOL","PAMEL","PAPIL","PARSN","PASEU","PATEK","PCILT",
"PEHOL","PEKGY","PENGD","PENTA","PETKM","PETUN","PGSUS","PINSU",
"PKART","PKENT","PLTUR","PNLSN","PNSUT","POLHO","POLTK","PRDGS",
"PRKAB","PRKME","PRZMA","PSDTC","PSGYO","QNBFB","QNBFK","QNBFL",
"QNBTR","QUAGR","RALYH","RAYSG","REEDR","RGYAS","RNPOL","RODRG",
"ROYAL","RTALB","RUBNS","RUZYE","RYGYO","RYSAS","SAFKR","SAHOL",
"SAMAT","SANEL","SANFM","SANKO","SARKY","SASA","SAYAS","SDTTR",
"SEGMN","SEGYO","SEKFK","SEKUR","SELEC","SELGD","SELVA","SERNT",
"SEYKM","SILVR","SISE","SKBNK","SKTAS","SKYLP","SKYMD","SMART",
"SMRTG","SMRVA","SNGYO","SNICA","SNKRN","SNPAM","SODSN","SOKE",
"SOKM","SONME","SRVGY","SUMAS","SUNTK","SURGY","SUWEN","SVGYO",
"TABGD","TARKM","TATEN","TATGD","TAVHL","TBORG","TCELL","TCKRC",
"TDGYO","TEHOL","TEKTU","TERA","TETMT","TEZOL","TGSAS","THYAO",
"TKFEN","TKNSA","TLMAN","TMPOL","TMSN","TNZTP","TOASO","TRALT",
"TRCAS","TRENJ","TRGYO","TRHOL","TRILC","TRMET","TSGYO","TSKB",
"TSPOR","TTKOM","TTRAK","TUCLK","TUKAS","TUPRS","TUREX","TURGG",
"TURSG","UCAYM","UFUK","ULAS","ULKER","ULUFA","ULUSE","ULUUN",
"UMPAS","UNLU","USAK","UZERB","VAKBN","VAKFA","VAKFN","VAKKO",
"VANGD","VBTYZ","VERTU","VERUS","VESBE","VESTL","VKFYO","VKGYO",
"VKING","VRGYO","VSNMD","YAPRK","YATAS","YAYLA","YBTAS","YEOTK",
"YESIL","YGGYO","YGYO","YIGIT","YKBNK","YKSLN","YONGA","YUNSA",
"YYAPI","YYLGD","ZEDUR","ZERGY","ZGYO","ZOREN","ZRGYO"
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
    if st_new: s_output += "✨ **SUPERTREND TAZE AL**\n\n" + "\n".join(st_new) + "\n\n"
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
