# ai_engine/StrategyGenerator.py
import logging
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, Any, Optional

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("StrategyGenerator")
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger

class StrategyGenerator:
    def __init__(self):
        self.model_registry: Dict[str, tf.keras.Model] = {}
        self.scaler = MinMaxScaler()
        self.logger = setup_logger()

    # ... (keep your create_deep_model, create_ensemble_model, _preprocess_data) ...

    def predict(self, symbol: str, data: Dict[str, np.ndarray], window_size: int = 30) -> Optional[int]:
        """
        0 = Buy, 1 = Sell, 2 = Hold. Returns None if no model loaded.
        """
        model = self.model_registry.get(symbol)
        if model is None:
            self.logger.error("Model for symbol %s not found", symbol)
            return None
        # (feature prep omitted for brevity)...
        preds = (model.predict_proba if hasattr(model, "predict_proba")
                 else model.predict)(np.expand_dims(last_window, axis=0))
        action = int(np.argmax(preds, axis=1)[0])
        self.logger.info("Prediction for %s: %d (Buy=0/Sell=1/Hold=2)", symbol, action)
        return action

    def generate_market_strategy(
        self,
        data: Dict[str, np.ndarray],
        symbol: str,
        stop_loss_pct: float,
        take_profit_pct: float
    ) -> Optional[Dict[str, Any]]:
        """
        Build a trade dict: entry, stop_loss, take_profit, symbol.
        Returns None on Hold or missing model.
        """
        action = self.predict(symbol, data)                              # :contentReference[oaicite:2]{index=2}
        if action is None or action == 2:
            return None  # no trade

        last_price = float(data["close"][-1])
        if action == 0:  # Buy
            entry = last_price
            stop_loss = entry * (1 - stop_loss_pct)
            take_profit = entry * (1 + take_profit_pct)
        else:            # Sell
            entry = last_price
            stop_loss = entry * (1 + stop_loss_pct)
            take_profit = entry * (1 - take_profit_pct)

        self.logger.info(
            "Generated strategy for %s: entry=%.5f, SL=%.5f, TP=%.5f",
            symbol, entry, stop_loss, take_profit
        )
        return {
            "symbol": symbol,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "volume": None  # to be set by TradingEngine
        }
