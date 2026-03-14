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
BIST_SYMBOLS = [
    "A1CAP","A1YEN","ACSEL","ADEL","ADESE","ADGYO","AEFES","AFYON",
    "AGESA","AGHOL","AGROT","AGYO","AHGAZ","AHSGY","AKBNK","AKCNS",
    "AKENR","AKFGY","AKFIS","AKFYE","AKGRT","AKHAN","AKMGY","AKSA",
    "AKSEN","AKSGY","AKSUE","AKYHO","ALARK","ALBRK","ALCAR","ALCTL",
    "ALFAS","ALGYO","ALKA","ALKIM","ALKLC","ALMAD","ALTNY","ALVES",
]

# ======================
# TARAMA (SCANNER)
# ======================

def run_scanner():
    tv = TvDatafeed()
    now_str = datetime.now().strftime('%H:%M:%S')
    
    new_al = []
    breakout_near = []

    for symbol in BIST_SYMBOLS:
        try:
            df = tv.get_hist(symbol=symbol, exchange="BIST", interval=Interval.in_daily, n_bars=60)
            
            if df is None or len(df) < 22:
                continue

            # Son 2 barın kapanışı ve bugünü saymadan önceki 20 günün EN YÜKSEĞİ (High)
            close_today = df["close"].iloc[-1]
            close_yesterday = df["close"].iloc[-2]
            donchian_high = df["high"].iloc[-21:-1].max()

            # --- KIRILIM (AL) ŞARTI ---
            if close_today > donchian_high and close_yesterday <= donchian_high:
                new_al.append(f"🚀 *{symbol}* - Fiyat: {close_today:.2f} (Direnç: {donchian_high:.2f} Kırıldı!)")
            
            # --- DİRENCE YAKIN (PUSU) ŞARTI ---
            else:
                distance = ((donchian_high - close_today) / close_today) * 100
                if 0 < distance <= 2:
                    breakout_near.append(f"👀 *{symbol}* - Mesafe: %{distance:.2f} (Direnç: {donchian_high:.2f})")

        except Exception as e:
            print(f"{symbol} hatası: {e}")

    # Mesaj Oluşturma
    final_msg = ""
    if new_al:
        final_msg += "🚨 **TURTLE TAZE KIRILIM (AL)**\n\n" + "\n".join(new_al) + "\n\n"
    if breakout_near:
        final_msg += "🔔 **DİRENCİNE YAKIN (Pusu)**\n\n" + "\n".join(breakout_near)

    if final_msg:
        send_telegram(final_msg)

if __name__ == "__main__":
    run_scanner()
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
