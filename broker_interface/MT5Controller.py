import MetaTrader5 as mt5
import logging
import time
from pathlib import Path
from typing import Dict

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
        self.logger = setup_logger()
        self.connected = False

        # Construct the path to terminal64.exe in the mt5 folder at the project root
        self.mt5_path = str(Path(__file__).resolve().parent.parent / "mt5" / "terminal64.exe")

    def connect(self) -> bool:
        """Connect to MT5 terminal"""
        login = self.config.get("login")
        password = self.config.get("password")
        server = self.config.get("server")

        if not all([login, password, server]):
            self.logger.error("Missing login credentials in configuration.")
            return False

        if not mt5.initialize(path=self.mt5_path, login=login, password=password, server=server):
            self.logger.error("MT5 initialize failed: %s", mt5.last_error())
            return False

        self.connected = True
        self.logger.info("Connected to MetaTrader 5: login %d", login)
        return True

    def disconnect(self):
        """Disconnect from MT5"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            self.logger.info("🔌 Disconnected from MT5")

    def reconnect(self):
        """Reconnect to MT5"""
        self.disconnect()
        time.sleep(5)
        return self.connect()

    def shutdown(self) -> None:
        mt5.shutdown()
        self.logger.info("MetaTrader 5 shutdown complete")
