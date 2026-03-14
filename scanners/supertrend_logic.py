import pandas as pd
import numpy as np

def check_supertrend(df, symbol, period=10, multiplier=3.0, near_threshold=0.015):
    if df is None or len(df) < period + 1:
        return None, None
        
    df = df.copy().reset_index(drop=True)
    df['hl2'] = (df['high'] + df['low']) / 2
    
    # Koddaki 'atr' hesabı (changeATR ? atr(period) : sma(tr, period))
    # TradingView'in standart atr(period) fonksiyonu RMA (ewm) kullanır.
    prev_close = df['close'].shift(1)
    tr = pd.concat([
        df['high'] - df['low'],
        (df['high'] - prev_close).abs(),
        (df['low'] - prev_close).abs()
    ], axis=1).max(axis=1)
    
    # Kıvanç Bey'in kodundaki varsayılan ATR (RMA)
    df['atr_val'] = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    df['up'] = df['hl2'] - (multiplier * df['atr_val'])
    df['dn'] = df['hl2'] + (multiplier * df['atr_val'])
    
    # Pine Script'teki := atamalarını simüle eden döngü
    t_up = np.zeros(len(df))
    t_dn = np.zeros(len(df))
    trend = np.ones(len(df)) # nz(trend[1], 1)

    for i in range(1, len(df)):
        # TrendUp := close[1] > TrendUp[1] ? max(Up, TrendUp[1]) : Up
        if df['close'].iloc[i-1] > t_up[i-1]:
            t_up[i] = max(df['up'].iloc[i], t_up[i-1])
        else:
            t_up[i] = df['up'].iloc[i]
            
        # TrendDown := close[1] < TrendDown[1] ? min(Dn, TrendDown[1]) : Dn
        if df['close'].iloc[i-1] < t_dn[i-1] or t_dn[i-1] == 0:
            t_dn[i] = df['dn'].iloc[i] if t_dn[i-1] == 0 else min(df['dn'].iloc[i], t_dn[i-1])
        else:
            t_dn[i] = df['dn'].iloc[i]
            
        # Trend := close > TrendDown[1] ? 1 : close < TrendUp[1] ? -1 : nz(Trend[1], 1)
        # BURASI KRİTİK: Bugünün fiyatı, dünün bandıyla kıyaslanıyor
        if df['close'].iloc[i] > t_dn[i-1] and t_dn[i-1] != 0:
            trend[i] = 1
        elif df['close'].iloc[i] < t_up[i-1] and t_up[i-1] != 0:
            trend[i] = -1
        else:
            trend[i] = trend[i-1]

    # Sonuçları DataFrame'e ekle
    df['trend_val'] = trend
    df['t_up_final'] = t_up
    df['t_dn_final'] = t_dn

    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Sinyal Kontrolü
    # Trend != Trend[1] (Trend değişimi)
    if curr['trend_val'] == 1 and prev['trend_val'] == -1:
        return "NEW", f"✨ *{symbol}* - Fiyat: {curr['close']:.2f} (ST Kırıldı!)"
    
    elif curr['trend_val'] == -1:
        # Direnç dünkü t_dn değeridir (Pine Script mantığı)
        resistance = prev['t_dn_final']
        dist = (resistance - curr['close']) / resistance
        if 0 < dist <= near_threshold:
            return "NEAR", f"🔭 *{symbol}* - Mesafe: %{dist*100:.2f} (Direnç: {resistance:.2f})"
            
    return None, None
