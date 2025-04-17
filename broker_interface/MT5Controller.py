import MetaTrader5 as mt5
from typing import Dict, Optional
import logging


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("MT5Controller")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class MT5Controller:
    def __init__(self, config: Dict):
        self.config = config
        self.connected = False

    def connect(self, login: int, password: str, server: str) -> bool:
        """Connect to MT5 terminal"""
        if not mt5.initialize():
            self.logger.error("Failed to initialize MT5")
            return False
        if not mt5.login(login=login, password=password, server=server):
            self.logger.error("MT5 login failed: %s", mt5.last_error())
            return False
        self.logger.info("Connected to MetaTrader 5: login %d", login)
        return True

    def shutdown(self) -> None:
        mt5.shutdown()
        self.logger.info("MetaTrader 5 shutdown complete")
