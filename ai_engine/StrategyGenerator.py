# ---------- ai_engine/StrategyGenerator.py ----------
"""
Generates trading strategies using deep learning and ensemble methods.
"""

import logging
from typing import Dict, Tuple, Optional, Any

import numpy as np
import tensorflow as tf
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import MinMaxScaler


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("StrategyModule")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


class StrategyModule:
    def __init__(self) -> None:
        self.model_registry: Dict[str, tf.keras.Model] = {}
        self.scaler = MinMaxScaler()
        self.logger = setup_logger()

    def create_deep_model(self, input_shape: Tuple[int, int]) -> tf.keras.Model:
        """Create and compile an LSTM-based model."""
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(256, return_sequences=True, input_shape=input_shape),
            tf.keras.layers.Dropout(0.4),
            tf.keras.layers.LSTM(128),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(3, activation="softmax"),
        ])
        model.compile(
            optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
        )
        self.logger.info("Deep model created with input shape %s", input_shape)
        return model

    def create_ensemble_model(self) -> GradientBoostingClassifier:
        """Create an ensemble Gradient Boosting classifier."""
        model = GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.05, random_state=42
        )
        self.logger.info("Ensemble model created: GradientBoostingClassifier")
        return model

    def _preprocess_data(
            self, data: Dict[str, np.ndarray], window_size: int = 30
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preprocess raw market data into training features and labels.
        :param data: Dict with 'close' and 'volume' arrays.
        :param window_size: Number of timesteps per sample.
        :return: Tuple of (X, y).
        """
        closes = np.asarray(data["close"])
        volumes = np.asarray(data["volume"])
        features = np.stack([closes, volumes], axis=1)
        scaled = self.scaler.fit_transform(features)
        X, y = [], []

        for i in range(window_size, len(scaled) - 1):
            X.append(scaled[i - window_size: i])
            delta = closes[i + 1] - closes[i]
            if delta > 0.1:
                y.append([1, 0, 0])  # Buy
            elif delta < -0.1:
                y.append([0, 1, 0])  # Sell
            else:
                y.append([0, 0, 1])  # Hold

        X_arr = np.array(X)
        y_arr = np.array(y)
        self.logger.info(
            "Preprocessed data: %d samples, window size %d",
            X_arr.shape[0], window_size,
        )
        return X_arr, y_arr

    def generate_market_strategy(
            self,
            data: Dict[str, np.ndarray],
            symbol: str,
            use_ensemble: bool = False,
            epochs: int = 50,
            batch_size: int = 64,
    ) -> None:
        """
        Train and store a prediction model for a given symbol.
        """
        X_train, y_train = self._preprocess_data(data)

        if use_ensemble:
            model = self.create_ensemble_model()
            model.fit(
                X_train.reshape(X_train.shape[0], -1), np.argmax(y_train, axis=1)
            )
        else:
            model = self.create_deep_model((X_train.shape[1], X_train.shape[2]))
            model.fit(
                X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1
            )

        self.model_registry[symbol] = model
        self.logger.info("Model trained and registered for symbol %s", symbol)

    def predict(
            self, symbol: str, data: Dict[str, np.ndarray], window_size: int = 30
    ) -> Optional[int]:
        """
        Predict the next action for a symbol: 0=Buy, 1=Sell, 2=Hold.
        """
        model = self.model_registry.get(symbol)
        if model is None:
            self.logger.error("Model for symbol %s not found", symbol)
            return None

        closes = np.asarray(data["close"])
        volumes = np.asarray(data["volume"])
        features = np.stack([closes, volumes], axis=1)
        scaled = self.scaler.transform(features)
        last_window = scaled[-window_size:]

        # Use predict_proba if available
        if hasattr(model, "predict_proba"):
            preds = model.predict_proba(last_window.reshape(1, -1))
        else:
            preds = model.predict(np.expand_dims(last_window, axis=0))

        action = int(np.argmax(preds, axis=1)[0])
        self.logger.info(
            "Prediction for %s: %d (Buy=0/Sell=1/Hold=2)", symbol, action
        )
        return action
