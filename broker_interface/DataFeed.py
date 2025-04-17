# ---------- broker_interface/DataFeed.py ----------
"""
Fetches market data from MetaTrader 5.
"""
import logging
from datetime import datetime
from typing import Optional
import pandas as pd
import MetaTrader5 as mt5


class DataFeed:
    def __init__(self) -> None:
        self.logger = logging.getLogger("DataFeed")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def get_ohlcv(self, symbol: str, timeframe: int, bars: int) -> Optional[pd.DataFrame]:
        data = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
        if data is None or len(data) == 0:
            self.logger.error("No data returned for symbol %s", symbol)
            return None
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        self.logger.info("Fetched %d bars for %s", len(df), symbol)
        return df
