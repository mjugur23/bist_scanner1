import os
import requests
import pandas as pd
from tvDatafeed import TvDatafeed, Interval

# ======================
# TELEGRAM YAPILANDIRMASI
# ======================
# Bilgileri GitHub Secrets üzerinden güvenli bir şekilde alıyoruz
BOT_TOKEN = os.getenv("8665295187")
CHAT_ID = os.getenv("AAEVNZQgFBmnECr4Oi18mtA8-KrvM0SFUN8")

def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("Hata: Telegram Token veya Chat ID bulunamadı!")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown" # Mesajların daha şık görünmesi için
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")

# ======================
# BIST SEMBOLLERİ
# ======================
# Liste uzun olduğu için kodun başında aynı şekilde kalsın (BIST100_SYMBOLS)
# Buraya senin paylaştığın listeyi olduğu gibi ekle veya mevcut haliyle kalsın.

BIST100_SYMBOLS = [
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

# ======================
# SCANNER (TURTLE STRATEJİSİ)
# ======================

def run_scanner():
    # GitHub Actions'da giriş yaparken hata almamak için username/password boş bırakılabilir
    tv = TvDatafeed()

    new_al = []
    breakout_near = []

    print("Tarama başlatılıyor...")

    for symbol in BIST100_SYMBOLS:
        try:
            df = tv.get_hist(
                symbol=symbol,
                exchange="BIST",
                interval=Interval.in_daily,
                n_bars=60
            )

            if df is None or len(df) < 22:
                continue

            close_today = df["close"].iloc[-1]
            close_yesterday = df["close"].iloc[-2]

            # Turtle Sistem 1: Son 20 günün en yükseği (Bugün ve Dün için ayrı)
            donchian_today = df["high"].iloc[-21:-1].max()
            donchian_yesterday = df["high"].iloc[-22:-2].max()

            # YENİ AL SİNYALİ (Breakout)
            breakout_today = close_today > donchian_today
            breakout_yesterday = close_yesterday > donchian_yesterday

            if breakout_today and not breakout_yesterday:
                new_al.append(f"🟢 *{symbol}* - Fiyat: {close_today:.2f}")

            # BREAKOUT YAKIN (Mesafe %2'den azsa)
            distance = (donchian_today - close_today) / close_today * 100
            if not breakout_today and distance <= 2:
                breakout_near.append(f"👀 *{symbol}* - Mesafe: %{distance:.2f}")

        except Exception as e:
            print(f"{symbol} hatası: {e}")

    # ======================
    # MESAJ OLUŞTURMA VE GÖNDERME
    # ======================
    msg = ""

    if new_al:
        msg += "🚀 **TURTLE SİSTEM 1: YENİ AL**\n"
        msg += "\n".join(new_al) + "\n\n"

    if breakout_near:
        msg += "🔔 **BREAKOUT YAKIN (%2)**\n"
        msg += "\n".join(breakout_near)

    if msg != "":
        send_telegram(msg)
        print("Sinyal Telegram'a gönderildi.")
    else:
        print("Yeni sinyal bulunamadı.")

if __name__ == "__main__":
    run_scanner()
