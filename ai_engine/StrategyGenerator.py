# ai_engine/StrategyGenerator.py

import logging
from typing import Dict, Tuple, Any, Optional
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from ai_engine.ModelUpdater import ModelUpdater  # for saving/loading

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("StrategyGenerator")
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger

class StrategyGenerator:
    def __init__(self, model_updater: ModelUpdater, window_size: int = 30):
        self.model_updater = model_updater
        self.window_size = window_size
        self.model_registry: Dict[str, tf.keras.Model] = {}
        self.scaler = MinMaxScaler()
        self.logger = setup_logger()

    def _preprocess_data(
        self, data: Dict[str, np.ndarray]
    ) -> Tuple[np.ndarray, np.ndarray]:
        closes = np.asarray(data["close"])
        volumes = np.asarray(data["volume"])
        features = np.stack([closes, volumes], axis=1)
        scaled = self.scaler.fit_transform(features)
        X, y = [], []
        for i in range(self.window_size, len(scaled) - 1):
            X.append(scaled[i - self.window_size: i])
            delta = closes[i + 1] - closes[i]
            if delta > 0:
                y.append([1, 0, 0])   # Buy
            elif delta < 0:
                y.append([0, 1, 0])   # Sell
            else:
                y.append([0, 0, 1])   # Hold
        return np.array(X), np.array(y)

    def create_deep_model(self, input_shape: Tuple[int, int]) -> tf.keras.Model:
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(256, return_sequences=True, input_shape=input_shape),
            tf.keras.layers.Dropout(0.4),
            tf.keras.layers.LSTM(128),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(3, activation="softmax"),
        ])
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        self.logger.info("Deep model compiled with input shape %s", input_shape)
        return model

    def train_model(self, symbol: str, data: Dict[str, np.ndarray]) -> None:
        """Train a new model for `symbol` and persist it."""
        X_train, y_train = self._preprocess_data(data)
        model = self.create_deep_model((X_train.shape[1], X_train.shape[2]))
        model.fit(X_train, y_train, epochs=50, batch_size=64, verbose=1)
        # register in memory and save to disk
        self.model_registry[symbol] = model
        self.model_updater.save_model(symbol, model)
        self.logger.info("Trained and saved new model for %s", symbol)

    def predict(self, symbol: str, data: Dict[str, np.ndarray]) -> Optional[int]:
        """
        Predict next action (0=Buy, 1=Sell, 2=Hold).
        Auto-trains if model file is missing.
        """
        # if not in memory, attempt to load
        if symbol not in self.model_registry:
            model = self.model_updater.load_model(symbol)  # :contentReference[oaicite:4]{index=4}
            if model is not None:
                self.model_registry[symbol] = model
            else:
                self.logger.info("No existing model for %s; training new one", symbol)  # :contentReference[oaicite:5]{index=5}
                self.train_model(symbol, data)                                                   # :contentReference[oaicite:6]{index=6}

        model = self.model_registry.get(symbol)
        if model is None:
            self.logger.error("Failed to obtain model for %s", symbol)
            return None

        # prepare last window for prediction
        closes = np.asarray(data["close"])
        volumes = np.asarray(data["volume"])
        scaled = self.scaler.transform(np.stack([closes, volumes], axis=1))
        last_window = scaled[-self.window_size:]
        preds = (model.predict_proba(last_window.reshape(1, -1))
                 if hasattr(model, "predict_proba")
                 else model.predict(np.expand_dims(last_window, axis=0)))
        action = int(np.argmax(preds, axis=1)[0])
        self.logger.info("Prediction for %s: %d (Buy=0/Sell=1/Hold=2)", symbol, action)  # :contentReference[oaicite:7]{index=7}
        return action
