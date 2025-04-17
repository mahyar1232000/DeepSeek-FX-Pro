# ---------- core/OrderExecutor.py ----------
"""
Bridges trade signals with broker execution.
"""
from broker_interface.OrderManager import OrderManager
from typing import Dict
import logging


class OrderExecutor:
    def __init__(self, order_manager: OrderManager) -> None:
        self.order_manager = order_manager
        self.logger = logging.getLogger("OrderExecutor")

    def execute(self, signal: Dict) -> None:
        success = self.order_manager.send_order(
            symbol=signal['symbol'],
            action=signal['action'],
            volume=signal['volume'],
            price=signal['price'],
            sl=signal['sl'],
            tp=signal['tp']
        )
        if success:
            self.logger.info("Executed order for %s", signal['symbol'])
        else:
            self.logger.warning("Order execution failed for %s", signal['symbol'])
