import pandas as pd

def check_turtle(df, symbol, near_threshold=0.02):
    # En az 30 bar kontrolü (10 günlük dip hesabı için gerekli)
    if df is None or len(df) < 30:
        return None, None
        
    df = df.copy().reset_index(drop=True)
    
    # 1. BİREBİR SENİN HESAPLAMALARIN (20 Gün Zirve, 10 Gün Dip)
    df["entry_high_20"] = df["high"].rolling(20).max().shift(1)
    df["exit_low_10"] = df["low"].rolling(10).min().shift(1)
    
    # 2. HAFIZA VE SİMÜLASYON DÖNGÜSÜ (Eksik olan hayat kurtarıcı kısım)
    position = 0
    position_history = []
    
    for idx, row in df.iterrows():
        eh = row.get("entry_high_20")
        exl = row.get("exit_low_10")
        close = row.get("close")
        
        if pd.isna(eh) or pd.isna(exl):
            position_history.append(position)
            continue
            
        # Pozisyondan çıkış (10 günlük dip kırılırsa)
        if position == 1 and close < exl:
            position = 0
        # Pozisyona giriş / Kırılım (20 günlük zirve geçilirse)
        elif position == 0 and close > eh:
            position = 1
            
        position_history.append(position)
        
    df["position"] = position_history
    
    # 3. SİNYAL KARARI (Bugün ve Dün)
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    curr_pos = last["position"]
    prev_pos = prev["position"]
    close = last["close"]
    entry_high = last["entry_high_20"]

    # 🟢 YENİ AL KONTROLÜ (Sadece bugün pozisyona girdiyse)
    if curr_pos == 1 and prev_pos != 1:
        return "NEW", f"🚀 *{symbol}* - Fiyat: {close:.2f} (Zirve: {entry_high:.2f})"
    
    # 🟡 PUSU KONTROLÜ (Pozisyonda değilsek ve zirveye yakınsak)
    elif curr_pos == 0 and close < entry_high:
        dist = (entry_high - close) / entry_high
        if 0 < dist <= near_threshold:
            return "NEAR", f"👀 *{symbol}* - Mesafe: %{dist*100:.2f} (Direnç: {entry_high:.2f})"
            
    return None, None
