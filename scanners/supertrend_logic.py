import pandas as pd

def check_supertrend(df, symbol, period=10, multiplier=3.0, near_threshold=0.015):
    df = df.copy()
    df['hl2'] = (df['high'] + df['low']) / 2
    
    prev_close = df['close'].shift(1)
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - prev_close).abs()
    tr3 = (df['low'] - prev_close).abs()
    df['tr'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['atr'] = df['tr'].rolling(period).mean()

    df['up'] = df['hl2'] - (multiplier * df['atr'])
    df['dn'] = df['hl2'] + (multiplier * df['atr'])
    
    df['t_up'] = 0.0
    df['t_dn'] = 0.0
    df['trend'] = 1
    
    for i in range(1, len(df)):
        # Up Kilit
        if df['close'].iloc[i-1] > df['t_up'].iloc[i-1]:
            df.loc[df.index[i], 't_up'] = max(df['up'].iloc[i], df['t_up'].iloc[i-1])
        else:
            df.loc[df.index[i], 't_up'] = df['up'].iloc[i]
        # Down Kilit
        if df['close'].iloc[i-1] < df['t_dn'].iloc[i-1] or df['t_dn'].iloc[i-1] == 0:
            df.loc[df.index[i], 't_dn'] = min(df['dn'].iloc[i], df['t_dn'].iloc[i-1]) if df['t_dn'].iloc[i-1] != 0 else df['dn'].iloc[i]
        else:
            df.loc[df.index[i], 't_dn'] = df['dn'].iloc[i]
            
        if df['close'].iloc[i] > df['t_dn'].iloc[i-1] and df['t_dn'].iloc[i-1] != 0:
            df.loc[df.index[i], 'trend'] = 1
        elif df['close'].iloc[i] < df['t_up'].iloc[i-1]:
            df.loc[df.index[i], 'trend'] = -1
        else:
            df.loc[df.index[i], 'trend'] = df['trend'].iloc[i-1]

    curr_close = df['close'].iloc[-1]
    st_line = df['t_dn'].iloc[-1] if df['trend'].iloc[-1] == -1 else df['t_up'].iloc[-1]
    
    if df['trend'].iloc[-1] == 1 and df['trend'].iloc[-2] == -1:
        return "NEW", f"✨ *{symbol}* - Fiyat: {curr_close:.2f}"
    elif df['trend'].iloc[-1] == -1:
        dist = (st_line - curr_close) / st_line
        if 0 < dist <= near_threshold:
            return "NEAR", f"🕯️ *{symbol}* - Mesafe: %{dist*100:.2f}"
            
    return None, None
