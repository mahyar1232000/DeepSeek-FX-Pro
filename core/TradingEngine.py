# core/TradingEngine.py
import logging, os
from typing import Dict, Any

from broker_interface.MT5Controller import MT5Controller
from broker_interface.DataFeed import DataFeed
from broker_interface.OrderManager import OrderManager
from core.OrderExecutor import OrderExecutor
from ai_engine.ModelUpdater import ModelUpdater
from ai_engine.ForecastModule import ForecastModule
from ai_engine.StrategyGenerator import StrategyGenerator
from ai_engine.RiskEvaluator import RiskEvaluator
from core.PortfolioManager import PortfolioManager
from core.PerformanceTracker import PerformanceTracker
from core.AlertSystem import AlertSystem


class TradingEngine:
    def __init__(self, risk_params: Dict[str, Any], creds: Dict[str, Any]):
        self.logger = logging.getLogger("TradingEngine")
        if not self.logger.handlers:
            h = logging.StreamHandler()
            h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
            self.logger.addHandler(h)
            self.logger.setLevel(logging.INFO)

        self.mt5 = MT5Controller()
        self.data_feed = DataFeed()
        self.order_manager = OrderManager()
        self.executor = OrderExecutor(self.order_manager)
        self.portfolio_manager = PortfolioManager()
        self.performance_tracker = PerformanceTracker()
        self.alerts = AlertSystem()

        # model & strategy
        os.makedirs("models", exist_ok=True)
        self.model_updater = ModelUpdater(save_dir="models")
        self.forecaster = ForecastModule(model_updater=self.model_updater)
        self.strategy_generator = StrategyGenerator()
        self.risk_evaluator = RiskEvaluator(parameters=risk_params)

        self.creds = creds

    def initialize(self) -> bool:
        return self.mt5.connect(
            login=self.creds["login"],
            password=self.creds["password"],
            server=self.creds["server"]
        )

    def run_cycle(self, symbol: str, timeframe: int, bars: int):
        df = self.data_feed.get_ohlcv(symbol, timeframe, bars)
        if df is None:
            self.logger.warning("No data for %s", symbol)
            return

        forecast = self.forecaster.forecast(symbol, df)
        features = {
            "close": df["close"].to_numpy(),
            "volume": df["tick_volume"].to_numpy()
        }
        strat = self.strategy_generator.generate_market_strategy(data=features, symbol=symbol)
        if self.risk_evaluator.evaluate(strat):
            self.executor.execute(strat)
            self.portfolio_manager.update_position(strat["symbol"], strat["volume"])
            self.performance_tracker.record_trade(strat.get("expected_pnl", 0.0))
            self.model_updater.save_model(symbol, self.strategy_generator.model_registry[symbol])
            self.alerts.send(f"Executed trade on {symbol}")
        else:
            self.logger.info("Strategy rejected for %s", symbol)
