# ---------- utils/AdvancedLogger.py ----------
"""
Custom logger with rotating file support.
"""
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
