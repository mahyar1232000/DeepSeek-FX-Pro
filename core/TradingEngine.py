# core/TradingEngine.py
import os
import logging
from broker_interface.MT5Controller import MT5Controller
from broker_interface.DataFeed import DataFeed
from broker_interface.OrderManager import OrderManager
from ai_engine.ModelUpdater import ModelUpdater
from ai_engine.ForecastModule import ForecastModule
from ai_engine.StrategyGenerator import StrategyGenerator
from ai_engine.RiskEvaluator import RiskEvaluator
from core.OrderExecutor import OrderExecutor
from core.PerformanceTracker import PerformanceTracker
from core.AlertSystem import AlertSystem
from core.PortfolioManager import PortfolioManager
from utils.SecurityModule import load_credentials


class TradingEngine:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.logger = logging.getLogger("TradingEngine")
        log_level = self.config.get('log_level', 'INFO').upper()
        logging.basicConfig(level=getattr(logging, log_level))

        # Suppress TensorFlow GPU warnings if GPU not available
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = self.config.get('tf_log_level', '2')

        # Model updater for loading/saving forecast models
        save_dir = self.config.get('model_save_dir', 'models')
        os.makedirs(save_dir, exist_ok=True)
        self.model_updater = ModelUpdater(save_dir)

        # Forecasting module
        self.forecaster = ForecastModule(self.model_updater)

        # Strategy generation
        self.strategy_generator = StrategyGenerator()

        # Risk evaluation with parameters from config
        risk_params = self.config.get('risk_parameters', {})
        self.risk_evaluator = RiskEvaluator(risk_params)

        # Other core components
        self.mt5 = MT5Controller()
        self.data_feed = DataFeed()
        self.order_manager = OrderManager()
        self.executor = OrderExecutor(self.order_manager)
        self.portfolio_manager = PortfolioManager()
        self.performance_tracker = PerformanceTracker()
        self.alerts = AlertSystem()

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

        # Determine symbols to process
        if mode == 'live':
            symbol_list = symbols or self.config.get('symbols', [])
        else:
            symbol_list = self.config.get('backtest', {}).get('symbols', [])

        timeframe = self.config.get('timeframe', 60)
        bars = self.config.get('bars', 500)
        self.logger.info("Starting %s mode for symbols: %s", mode, symbol_list)

        for symbol in symbol_list:
            try:
                self.run_cycle(symbol, timeframe, bars)
            except Exception as e:
                self.logger.exception("Error during run cycle for %s: %s", symbol, e)

        self.logger.info("Run complete.")

    def run_cycle(self, symbol: str, timeframe: int, bars: int) -> None:
        data = self.data_feed.get_ohlcv(symbol, timeframe, bars)
        if data is None:
            self.logger.warning("No data for %s", symbol)
            return

        # Forecasting
        forecast = self.forecaster.predict(symbol, data)

        # Strategy generation
        strategy = self.strategy_generator.generate(data, forecast)

        # Risk check
        if self.risk_evaluator.evaluate(strategy):
            # Execute and track
            self.executor.execute(strategy)
            self.portfolio_manager.update_position(strategy['symbol'], strategy['volume'])
            self.performance_tracker.record_trade(strategy.get('expected_pnl', 0))
            # Save updated model if provided
            model = strategy.get('model')
            if model:
                self.model_updater.save_model(symbol, model)
            self.alerts.send(f"Trade executed for {strategy['symbol']}")
        else:
            self.logger.info("Trade for %s did not pass risk checks.", symbol)
