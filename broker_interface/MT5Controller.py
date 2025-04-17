# ---------- broker_interface/MT5Controller.py ----------
"""
Handles connection and communication with MetaTrader 5 terminal.
"""
import logging
import MetaTrader5 as mt5


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
    def __init__(self) -> None:
        self.logger = setup_logger()

    def connect(self, login: int, password: str, server: str) -> bool:
        if not mt5.initialize(login=login, password=password, server=server):
            self.logger.error("MT5 initialize failed: %s", mt5.last_error())
            return False
        self.logger.info("Connected to MetaTrader 5: login %d", login)
        return True

    def shutdown(self) -> None:
        mt5.shutdown()
        self.logger.info("MetaTrader 5 shutdown complete")
