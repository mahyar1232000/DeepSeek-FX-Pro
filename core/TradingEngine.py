# ---------- core/TradingEngine.py ----------

import logging
import os
from typing import Dict, Any

from ai_engine.StrategyGenerator import StrategyGenerator
from ai_engine.RiskEvaluator import RiskEvaluator
from ai_engine.ForecastModule import ForecastModule
from ai_engine.ModelUpdater import ModelUpdater
from broker_interface.DataFeed import DataFeed
from broker_interface.MT5Controller import MT5Controller
from core.OrderExecutor import OrderExecutor
from core.PerformanceTracker import PerformanceTracker
from core.AlertSystem import AlertSystem
from core.PortfolioManager import PortfolioManager
from utils.SecurityModule import load_credentials
from broker_interface.OrderManager import OrderManager


class TradingEngine:
    def __init__(self, risk_params: Dict[str, Any], creds: Dict[str, str]) -> None:
        self.logger = logging.getLogger("TradingEngine")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
            )
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

        # connectivity & data
        self.mt5 = MT5Controller()
        self.data_feed = DataFeed()

        # model persistence & forecasting
        model_dir = "./models"
        os.makedirs(model_dir, exist_ok=True)
        self.model_updater = ModelUpdater(save_dir=model_dir)
        self.forecaster = ForecastModule(model_updater=self.model_updater)

        # strategy & risk (now from config)
        self.strategy_generator = StrategyGenerator()
        self.risk_evaluator = RiskEvaluator(parameters=risk_params)

        # execution & tracking
        self.portfolio_manager = PortfolioManager()
        self.performance_tracker = PerformanceTracker()
        self.alerts = AlertSystem()
        self.order_manager = OrderManager()
        self.executor = OrderExecutor(self.order_manager)

    def initialize(self) -> bool:
        # use creds passed at init
        return self.mt5.connect(
            login=creds["login"],
            password=creds["password"],
            server=creds["server"]
        )

    def run_cycle(self, symbol: str, timeframe: int, bars: int) -> None:
        df = self.data_feed.get_ohlcv(symbol, timeframe, bars)
        if df is None:
            self.logger.warning("No data for %s", symbol)
            return

        forecast = self.forecaster.forecast(symbol, df)

        features = {
            "close": df["close"].to_numpy(),
            "volume": df["tick_volume"].to_numpy()
        }
        strategy = self.strategy_generator.generate_market_strategy(
            data=features,
            symbol=symbol
        )

        if self.risk_evaluator.evaluate(strategy):
            self.executor.execute(strategy)
            self.portfolio_manager.update_position(
                strategy["symbol"], strategy["volume"]
            )
            self.performance_tracker.record_trade(
                strategy.get("expected_pnl", 0.0)
            )
            self.model_updater.save_model(
                symbol,
                self.strategy_generator.model_registry[symbol]
            )
            self.alerts.send(f"Executed trade on {symbol}")
        else:
            self.logger.info("Strategy rejected for %s", symbol)
