import os
import requests
import pandas as pd
from tvDatafeed import TvDatafeed, Interval
from datetime import datetime

# ======================
# YAPILANDIRMA (CONFIG)
# ======================
# BotFather'dan gelen token ve senin Chat ID'n
BOT_TOKEN = "8665295187:AAEVNZQgFBmnECr4Oi18mtA8-KrvM0SFUN8"
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
    
    if new_al:
        final_msg += "🚨 **TURTLE TAZE KIRILIM (AL)**\n\n"
        final_msg += "\n".join(new_al) + "\n\n"

    if breakout_near:
        final_msg += "🔔 **DİRENCİNE YAKIN (Pusu)**\n\n"
        final_msg += "\n".join(breakout_near)

    # Hiç sinyal yoksa kullanıcıya bilgi ver
    if not final_msg:
        final_msg = f"✅ **Tarama Başarıyla Tamamlandı**\n\nŞu an kriterlere uyan yeni bir hisse bulunamadı."

    send_telegram(final_msg)
    print(f"[{now_str}] İşlem tamamlandı.")

if __name__ == "__main__":
    run_scanner()
