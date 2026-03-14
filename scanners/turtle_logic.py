import pandas as pd

def check_turtle(df, symbol, near_threshold=0.015):
    # En az 22 bar çekildiğinden emin oluyoruz
    if df is None or len(df) < 22:
        return None, None
        
    df = df.copy().reset_index(drop=True)
    
    # 20 Günlük Kanal Üst Bant (Bugünü dahil etmiyoruz)
    df["eh20"] = df["high"].rolling(20).max().shift(1)
    
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3]
    
    curr_close = curr['close']
    eh20 = curr['eh20']

    # TAZE KIRILIM MANTIĞI (En Stabil Hali)
    # Bugün kanalın üstündeyiz.
    is_above = curr_close > eh20
    
    # Son 2 günden birinde kanalın altındaydık (Piyasa kapalıyken çakışmayı önler)
    was_below = (prev['close'] <= prev['eh20']) or (prev2['close'] <= prev2['eh20'])

    if is_above and was_below:
        return "NEW", f"🚀 *{symbol}* - Fiyat: {curr_close:.2f} (20G Zirve: {eh20:.2f})"
    
    # PUSU MANTIĞI
    elif curr_close <= eh20:
        dist = (eh20 - curr_close) / eh20
        if 0 < dist <= near_threshold:
            return "NEAR", f"🔔 *{symbol}* - Mesafe: %{dist*100:.2f} (Hedef: {eh20:.2f})"
            
    return None, None
