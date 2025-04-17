# ---------- core/PortfolioManager.py ----------
"""
Tracks asset allocation, balances, and exposure.
"""
import logging
from typing import Dict


class PortfolioManager:
    def __init__(self) -> None:
        self.positions: Dict[str, float] = {}
        self.logger = logging.getLogger("PortfolioManager")

    def update_position(self, symbol: str, volume: float) -> None:
        self.positions[symbol] = self.positions.get(symbol, 0.0) + volume
        self.logger.info("Updated position for %s: %.2f", symbol, self.positions[symbol])

    def get_position(self, symbol: str) -> float:
        return self.positions.get(symbol, 0.0)
