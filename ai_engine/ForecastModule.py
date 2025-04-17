# ---------- ai_engine/ForecastModule.py ----------
"""
Handles time-series forecasting using pre-trained models.
"""

import logging
from typing import Dict, Any, List

import numpy as np
import pandas as pd

from ai_engine.ModelUpdater import ModelUpdater


class ForecastModule:
    def __init__(self, model_updater: ModelUpdater) -> None:
        """
        model_updater: used to load/save symbol-specific models.
        """
        self.model_updater = model_updater
        self.models: Dict[str, Any] = {}
        self.logger = logging.getLogger("ForecastModule")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
            )
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def load_model(self, symbol: str) -> bool:
        """
        Attempt to load a model for `symbol` from disk.
        Returns True if loaded successfully.
        """
        model = self.model_updater.load_model(symbol)
        if model is not None:
            self.models[symbol] = model
            return True
        return False

    def forecast(
        self,
        symbol: str,
        data: Any,            # → pd.DataFrame or np.ndarray
        periods: int = 10
    ) -> List[float]:
        """
        Generate a forecast for the next `periods` values of `symbol`
        based on its time-series `data`.
        """
        # convert DataFrame inputs into NumPy arrays
        if isinstance(data, pd.DataFrame):
            arr = data.to_numpy()
        else:
            arr = np.asarray(data)

        model = self.models.get(symbol)
        if model is None:
            # try loading if not in memory
            if not self.load_model(symbol):
                self.logger.error("No model found for symbol %s", symbol)
                return []
            model = self.models[symbol]

        # assume model.predict accepts arr of shape (n_samples, n_features)
        preds = model.predict(arr)
        result = preds[-periods:].tolist()
        self.logger.info("Forecast for %s: %s", symbol, result)
        return result

    # alias so TradingEngine.predict() still works if desired
    predict = forecast
