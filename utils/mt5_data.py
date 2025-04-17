# ---------- utils/mt5_data.py ----------
"""
Utility to initialize MT5 and download data as DataFrame.
"""
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime


def get_data(symbol: str, timeframe: int, bars: int) -> pd.DataFrame:
    if not mt5.initialize():
        raise RuntimeError("MT5 initialization failed")

    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    mt5.shutdown()
    return df
