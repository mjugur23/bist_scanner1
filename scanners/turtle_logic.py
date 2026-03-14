import pandas as pd

def check_turtle(df, symbol, near_threshold=0.015):
    df = df.copy()
    # 20 Günlük Kanal ve 10 Günlük Çıkış
    df["eh20"] = df["high"].rolling(20).max().shift(1)
    df["el10"] = df["low"].rolling(10).min().shift(1)
    
    pos = 0
    for _, row in df.iterrows():
        if pos == 1 and row['close'] < row['el10']: pos = 0
        if pos == 0 and row['close'] > row['eh20']: pos = 1
    
    # Bugün mü kırdı? (Taze Sinyal)
    is_new_buy = (pos == 1 and df['close'].iloc[-2] <= df['eh20'].iloc[-1])
    curr_close = df['close'].iloc[-1]
    eh20 = df['eh20'].iloc[-1]
    
    if is_new_buy:
        return "NEW", f"🚀 *{symbol}* - Fiyat: {curr_close:.2f} (Zirve: {eh20:.2f})"
    elif pos == 0 and curr_close < eh20:
        dist = (eh20 - curr_close) / eh20
        if dist <= near_threshold:
            return "NEAR", f"👀 *{symbol}* - Mesafe: %{dist*100:.2f}"
    
    return None, None
