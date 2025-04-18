# ai_engine/RiskEvaluator.py
import logging
from typing import Dict, Any, Optional

def setup_risk_logger() -> logging.Logger:
    logger = logging.getLogger("RiskEvaluator")
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger

class RiskEvaluator:
    def __init__(self, parameters: Dict[str, Any]) -> None:
        self.params = parameters
        self.logger = setup_risk_logger()

    def calculate_position_size(self, equity: float, stop_loss: float, risk_pct: float) -> float:
        risk_amount = equity * risk_pct / 100.0
        size = risk_amount / abs(stop_loss)
        self.logger.info("Position size calc: equity=%.2f, stop_loss=%.4f, risk_pct=%.2f → size=%.4f",
                         equity, stop_loss, risk_pct, size)
        return size

    def evaluate_trade_risk(self, entry_price: float, stop_loss_price: float, take_profit_price: float) -> Dict[str, float]:
        loss = abs(entry_price - stop_loss_price)
        reward = abs(take_profit_price - entry_price)
        rr_ratio = reward / loss if loss > 0 else float("inf")
        metrics = {"loss": loss, "reward": reward, "reward_risk_ratio": rr_ratio}
        self.logger.info("Trade risk metrics: %s", metrics)
        return metrics

    def evaluate(self, strategy: Optional[Dict[str, Any]]) -> bool:
        """
        Returns True if the strategy passes risk checks.
        Safely returns False if strategy is None or incomplete.
        """
        if not strategy:
            self.logger.info("No strategy to evaluate, skipping.")
            return False                                      # :contentReference[oaicite:3]{index=3}

        try:
            metrics = self.evaluate_trade_risk(
                strategy["entry"], strategy["stop_loss"], strategy["take_profit"]
            )
        except KeyError:
            self.logger.error("Incomplete strategy dict, skipping risk.")
            return False

        min_rr = self.params.get("min_reward_risk_ratio", 1.5)
        ok = metrics["reward_risk_ratio"] >= min_rr
        self.logger.info(
            "Strategy %s risk-evaluation → %s (rr %.2f ≥ min %.2f)",
            strategy.get("symbol"), ok, metrics["reward_risk_ratio"], min_rr
        )
        return ok
