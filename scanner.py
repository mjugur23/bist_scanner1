import os
import requests
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from datetime import datetime

# ======================
# YAPILANDIRMA (CONFIG)
# ======================
# BotFather'dan gelen token ve senin Chat ID'n
BOT_TOKEN = "8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk"
CHAT_ID = "5886003690" 

def send_telegram(msg):
    """Telegram üzerinden bildirim gönderen fonksiyon."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": 5886003690,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Telegram Hatası: {response.text}")
        else:
            print("Mesaj başarıyla gönderildi.")
    except Exception as e:
        print(f"Bağlantı hatası: {e}")

# ======================
# SEMBOLLER (BIST 100)
# ======================
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
# TARAMA (SCANNER)
# ======================

def run_scanner():
    tv = TvDatafeed()
    now_str = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    # Başlangıç bildirimi
    send_telegram(f"🤖 **BIST Tarayıcı Başlatıldı**\n📅 Tarih: {now_str}\n\nLütfen bekleyin, 500+ hisse taranıyor...")

    new_al = []
    breakout_near = []

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
            
            # Donchian 20 Günlük Kanal (Bugün ve Dün hariç son 20 günün en yükseği)
            donchian_high = df["high"].iloc[-21:-1].max()

            # --- TAZE KIRILIM (AL) ---
            # Bugün zirveyi kırdı ve dün henüz kırmamıştı
            if close_today > donchian_high and close_yesterday <= donchian_high:
                new_al.append(f"🚀 *{symbol}* - Fiyat: {close_today:.2f}")

            # --- BREAKOUT YAKIN ---
            # Kırılım olmadı ama fiyat zirveye %2'den yakın
            else:
                distance = ((donchian_high - close_today) / close_today) * 100
                if 0 < distance <= 2:
                    breakout_near.append(f"👀 *{symbol}* - Mesafe: %{distance:.2f}")

        except Exception as e:
            # Hataları loga yaz ama taramayı durdurma
            print(f"{symbol} tarama hatası: {e}")

    # ======================
    # MESAJ OLUŞTURMA
    # ======================
    final_msg = ""
    
    # Sadece taze AL sinyali varsa başlık ekle
    if new_al:
        final_msg += "🚨 **TURTLE TAZE KIRILIM (AL)**\n"
        final_msg += "*(Sadece bugün ilk kez kıranlar)*\n\n"
        final_msg += "\n".join(new_al) + "\n\n"

    # Pusu listesini istersen göndermeyebilirsin ya da altına ekleyebilirsin
    if breakout_near:
        final_msg += "🔔 **DİRENCİNE YAKIN (Pusu)**\n"
        final_msg += "\n".join(breakout_near)

    # ÖNEMLİ GÜNCELLEME: 
    # Sadece yeni bir sinyal (AL veya Pusu) varsa mesaj gönder.
    # Böylece "Sinyal bulunamadı" mesajlarıyla telefonun gereksiz meşgul olmaz.
    if final_msg:
        send_telegram(final_msg)
    else:
        # Eğer bir sinyal yoksa sadece GitHub loglarına yazar, Telegram'a mesaj atmaz.
        print(f"[{now_str}] Tarama yapıldı, kriterlere uyan yeni hisse yok. Telegram'a mesaj gönderilmedi.")

if __name__ == "__main__":
    run_scanner()
