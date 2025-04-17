# core/TradingEngine.py
import os
import logging
import yaml
from broker_interface.MT5Controller import MT5Controller
from broker_interface.DataFeed import DataFeed
from broker_interface.OrderManager import OrderManager
from ai_engine.ForecastModule import ForecastModule
from ai_engine.StrategyGenerator import StrategyGenerator
from ai_engine.RiskEvaluator import RiskEvaluator
from ai_engine.ModelUpdater import ModelUpdater
from core.OrderExecutor import OrderExecutor
from core.PerformanceTracker import PerformanceTracker
from core.AlertSystem import AlertSystem
from core.PortfolioManager import PortfolioManager
from utils.SecurityModule import load_credentials


class TradingEngine:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.logger = logging.getLogger("TradingEngine")
        log_level = config.get('log_level', 'INFO').upper()
        logging.basicConfig(level=getattr(logging, log_level))

        # Suppress TensorFlow GPU warnings if not needed
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = config.get('tf_log_level', '2')

        self.mt5 = MT5Controller()
        self.data_feed = DataFeed()
        self.forecaster = ForecastModule()
        self.strategy_generator = StrategyGenerator()
        self.risk_evaluator = RiskEvaluator()
        self.portfolio_manager = PortfolioManager()
        self.performance_tracker = PerformanceTracker()
        self.alerts = AlertSystem()
        self.order_manager = OrderManager()
        self.executor = OrderExecutor(self.order_manager)
        self.model_updater = ModelUpdater()

    def initialize(self) -> bool:
        creds = load_credentials()
        if not creds:
            self.logger.error("Failed to load credentials.")
            return False
        return self.mt5.connect(
            login=creds["login"],
            password=creds["password"],
            server=creds["server"]
        )

    def run(self, mode: str = 'live', symbols: list = None) -> None:
        if not self.initialize():
            self.logger.error("Initialization failed. Exiting.")
            return

        # Determine symbol list
        if mode == 'live':
            symbol_list = symbols if symbols is not None else self.config.get('symbols', [])
        else:
            symbol_list = self.config.get('backtest', {}).get('symbols', [])

        timeframe = self.config.get('timeframe', 60)
        bars = self.config.get('bars', 500)
        self.logger.info("Starting %s mode for symbols: %s", mode, symbol_list)

        for symbol in symbol_list:
            try:
                self.run_cycle(symbol, timeframe, bars)
            except Exception as e:
                self.logger.exception("Error running cycle for %s: %s", symbol, e)

        self.logger.info("Run complete.")

    def run_cycle(self, symbol: str, timeframe: int, bars: int) -> None:
        data = self.data_feed.get_ohlcv(symbol, timeframe, bars)
        if data is None:
            self.logger.warning("No data to run cycle for %s", symbol)
            return

        forecast = self.forecaster.predict(data)
        strategy = self.strategy_generator.generate(data, forecast)

        if self.risk_evaluator.evaluate(strategy):
            self.executor.execute(strategy)
            self.portfolio_manager.update_position(strategy['symbol'], strategy['volume'])
            self.performance_tracker.record_trade(strategy['expected_pnl'])
            self.model_updater.update(data, strategy)
            self.alerts.send(f"Executed trade on {strategy['symbol']}")
        else:
            self.logger.info("Strategy rejected by risk evaluator.")
