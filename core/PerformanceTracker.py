# ---------- core/PerformanceTracker.py ----------
"""
Monitors PnL, drawdown, and win rate.
"""
import logging
from typing import List


class PerformanceTracker:
    def __init__(self) -> None:
        self.trades: List[float] = []
        self.logger = logging.getLogger("PerformanceTracker")

    def record_trade(self, pnl: float) -> None:
        self.trades.append(pnl)
        self.logger.info("Recorded trade PnL: %.2f", pnl)

    def get_total_pnl(self) -> float:
        return sum(self.trades)

    def get_win_rate(self) -> float:
        wins = [t for t in self.trades if t > 0]
        return len(wins) / len(self.trades) if self.trades else 0.0

    def get_max_drawdown(self) -> float:
        peak = 0
        drawdown = 0
        balance = 0
        for pnl in self.trades:
            balance += pnl
            if balance > peak:
                peak = balance
            dd = peak - balance
            if dd > drawdown:
                drawdown = dd
        return drawdown
