import pandas as pd

def check_turtle(df, symbol, near_threshold=0.015):
    if df is None or len(df) < 22:
        return None, None
        
    df = df.copy().reset_index(drop=True)
    
    # 20 Günlük Kanal (Dün ve öncesi)
    df["eh20"] = df["high"].rolling(20).max().shift(1)
    
    # Bugünün verileri
    curr_close = df['close'].iloc[-1]
    eh20_now = df['eh20'].iloc[-1]
    
    # TAZE KIRILIM KONTROLÜ (Garantici Yöntem)
    # 1. Bugün kanalın üstündeyiz
    # 2. Ama bir önceki barda (veya ondan öncekinde) kanalın içindeydik
    is_breakout = curr_close > eh20_now
    
    # Son 2 barın en az birinde fiyatın kanal altında olduğunu kontrol et
    # Bu, piyasa kapalıyken oluşan "aynı veri" çakışmasını aşmamızı sağlar
    was_below = (df['close'].iloc[-2] <= df['eh20'].iloc[-2]) or (df['close'].iloc[-3] <= df['eh20'].iloc[-3])

    if is_breakout and was_below:
        return "NEW", f"🚀 *{symbol}* - TAZE KIRILIM! Fiyat: {curr_close:.2f} (Zirve: {eh20_now:.2f})"
    
    # PUSU KONTROLÜ
    elif curr_close <= eh20_now:
        dist = (eh20_now - curr_close) / eh20_now
        if 0 < dist <= near_threshold:
            return "NEAR", f"🔔 *{symbol}* - Mesafe: %{dist*100:.2f} (Hedef: {eh20_now:.2f})"
            
    return None, None
