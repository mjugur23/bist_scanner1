import os
import requests
import pandas as pd
import numpy as np
from tvDatafeed import TvDatafeed, Interval
from datetime import datetime

# ======================
# CONFIG & SETTINGS
# ======================
BOT_TOKEN = "8636859505:AAFGvfaT8JDMoDmwbUZNoJ0OA-NdToeB3Uk"
CHAT_ID = "5886003690"
BREAKOUT_NEAR_THRESHOLD = 0.02

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200: print(f"Telegram Hatası: {response.text}")
    except Exception as e: print(f"Bağlantı hatası: {e}")

# ======================
# TURTLE ENGINE (SENİN KODUN)
# ======================
def _prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["entry_high_20"] = df["high"].rolling(20).max().shift(1)
    df["entry_low_20"] = df["low"].rolling(20).min().shift(1)
    df["exit_low_10"] = df["low"].rolling(10).min().shift(1)
    return df

def _simulate_state(df: pd.DataFrame):
    position = 0
    position_history = []
    for idx, row in df.iterrows():
        eh = row.get("entry_high_20")
        exl = row.get("exit_low_10")
        close = row.get("close")
        if pd.isna(eh) or pd.isna(exl):
            position_history.append(position)
            continue
        if position == 1 and close < exl:
            position = 0
        if position == 0 and close > eh:
            position = 1
        position_history.append(position)
    df["position"] = position_history
    return df

# ======================
# TARAMA (SCANNER)
# ======================
def run_scanner():
    tv = TvDatafeed()
    new_al = []
    breakout_near = []

    # Not: BIST_SYMBOLS listesi burada tanımlı olmalı (Daha önce paylaştığın liste)
    for symbol in BIST_SYMBOLS:
        try:
            df = tv.get_hist(symbol=symbol, exchange="BIST", interval=Interval.in_daily, n_bars=100)
            if df is None or len(df) < 30: continue

            df = _prepare_df(df)
            df = _simulate_state(df)
            
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            curr_pos = last["position"]
            prev_pos = prev["position"]
            close = last["close"]
            entry_high = last["entry_high_20"]

            # 🟢 YENİ AL (AFYON burada elenecek)
            if curr_pos == 1 and prev_pos != 1:
                new_al.append(f"🚀 *{symbol}* - Fiyat: {close:.2f} (Zirve: {entry_high:.2f})")
            
            # 🟡 BREAKOUT YAKIN
            elif curr_pos == 0 and close < entry_high:
                dist = (entry_high - close) / entry_high
                if dist <= BREAKOUT_NEAR_THRESHOLD:
                    new_al_val = entry_high
                    breakout_near.append(f"👀 *{symbol}* - %{dist*100:.2f} (Direnç: {entry_high:.2f})")

        except Exception as e:
            print(f"{symbol} hata: {e}")

    # Mesaj Gönderimi
    msg = ""
    if new_al:
        msg += "🚨 **TURTLE YENİ AL SİNYALİ**\n\n" + "\n".join(new_al) + "\n\n"
    if breakout_near:
        msg += "🔔 **BREAKOUT YAKIN (PUSU)**\n\n" + "\n".join(breakout_near)

    if msg:
        send_telegram(msg)

# SEMBOLLERİ BURAYA EKLEYEBİLİRSİN
BIST_SYMBOLS = [
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

if __name__ == "__main__":
    run_scanner()
