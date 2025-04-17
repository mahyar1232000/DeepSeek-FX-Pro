# ---------- ai_engine/ModelUpdater.py ----------
"""
Updates and persists models based on new data.
"""
import logging
from typing import Dict, Any

import joblib


class ModelUpdater:
    def __init__(self, save_dir: str) -> None:
        self.save_dir = save_dir
        self.logger = logging.getLogger("ModelUpdater")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
            )
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def save_model(self, symbol: str, model: Any) -> None:
        path = f"{self.save_dir}/{symbol}_model.pkl"
        joblib.dump(model, path)
        self.logger.info("Model saved to %s", path)

    def load_model(self, symbol: str) -> Any:
        path = f"{self.save_dir}/{symbol}_model.pkl"
        try:
            model = joblib.load(path)
            self.logger.info("Model loaded from %s", path)
            return model
        except FileNotFoundError:
            self.logger.error("Model file not found: %s", path)
            return None
