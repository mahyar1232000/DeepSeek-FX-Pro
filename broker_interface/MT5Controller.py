# broker_interface/MT5Controller.py
import MetaTrader5 as mt5
import logging
import time
from pathlib import Path


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("MT5Controller")
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger


class MT5Controller:
    def __init__(self, terminal_path: str = None):
        self.logger = setup_logger()
        self.connected = False
        self.mt5_path = terminal_path or str(
            Path(__file__).resolve().parent.parent / "mt5" / "terminal64.exe"
        )

    def connect(self, login: int, password: str, server: str) -> bool:
        if not mt5.initialize(
                path=self.mt5_path, login=login, password=password, server=server
        ):
            self.logger.error("MT5 initialize failed: %s", mt5.last_error())
            return False
        self.connected = True
        self.logger.info("Connected to MetaTrader5 as %d", login)
        return True

    def disconnect(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.logger.info("Disconnected from MetaTrader5")
