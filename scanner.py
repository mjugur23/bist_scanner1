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
for symbol in BIST100_SYMBOLS:
        try:
            # 60 barlık veri çekiyoruz
            df = tv.get_hist(symbol=symbol, exchange="BIST", interval=Interval.in_daily, n_bars=60)
            
            if df is None or len(df) < 22:
                continue

            # --- HESAPLAMA MANTIGI GÜNCELLEMESİ ---
            # Bugünün ve dünün verilerini netleştirelim
            close_today = df["close"].iloc[-1]
            close_yesterday = df["close"].iloc[-2]
            
            # Donchian High: Bugünü saymadan geriye dönük tam 20 günün EN YÜKSEK (High) değeri
            # iloc[-21:-1] -> Son bar hariç (bugün), ondan önceki 20 barı alır.
            donchian_high = df["high"].iloc[-21:-1].max()

            # --- KIRILIM (AL) ŞARTI ---
            if close_today > donchian_high and close_yesterday <= donchian_high:
                # Mesaja direnç seviyesini de ekledik ki kontrol edebilesin
                new_al.append(f"🚀 *{symbol}* - Fiyat: {close_today:.2f} (Direnç: {donchian_high:.2f} Kırıldı!)")
            
            # --- DİRENCE YAKIN (PUSU) ŞARTI ---
            else:
                distance = ((donchian_high - close_today) / close_today) * 100
                # Eğer fiyat direncin altındaysa ve mesafe %2'den azsa
                if 0 < distance <= 2:
                    # Buradaki Direnç bilgisi senin grafiğindeki çizgiyle aynı olmalı
                    breakout_near.append(f"👀 *{symbol}* - Mesafe: %{distance:.2f} (Direnç: {donchian_high:.2f})")

        except Exception as e:
            print(f"{symbol} hatası: {e}"){e}")

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
