# ---------- broker_interface/OrderManager.py ----------
"""
Executes trade orders and manages order lifecycle.
"""
import logging
from typing import Dict
import MetaTrader5 as mt5


class OrderManager:
    def __init__(self) -> None:
        self.logger = logging.getLogger("OrderManager")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def send_order(self, symbol: str, action: int, volume: float, price: float, sl: float, tp: float) -> bool:
        order_type = mt5.ORDER_TYPE_BUY if action == 0 else mt5.ORDER_TYPE_SELL
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 10,
            "magic": 123456,
            "comment": "DeepSeek-FX-Pro",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            self.logger.error("Order failed: %s", result)
            return False
        self.logger.info("Order sent: %s", result)
        return True
