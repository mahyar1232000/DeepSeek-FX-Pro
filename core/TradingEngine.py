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
import MetaTrader5 as mt5


class TradingEngine:
    def __init__(self, config):
        self.config = config
        self.mt5 = MT5Controller(config)
        self.logger = logging.getLogger("TradingEngine")
        log_level = self.config.get('logging', {}).get('level', 'INFO').upper()
        logging.basicConfig(level=getattr(logging, log_level))
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = self.config.get('logging', {}).get('tf_log_level', '2')

        # Model updater and forecasting
        save_dir = self.config.get('model', {}).get('path', 'models')
        os.makedirs(save_dir, exist_ok=True)
        self.model_updater = ModelUpdater(save_dir)
        self.forecaster = ForecastModule(self.model_updater)

        # Strategy, risk, and execution
        self.strategy_generator = StrategyGenerator()
        risk_params = self.config.get('security', {}).get('risk_params', None) or self.config.get('risk_params', {})
        self.risk_evaluator = RiskEvaluator(risk_params)

        self.mt5 = MT5Controller(self.config)
        self.data_feed = DataFeed()
        self.order_manager = OrderManager()
        self.executor = OrderExecutor(self.order_manager)
        self.portfolio_manager = PortfolioManager()
        self.performance_tracker = PerformanceTracker()
        self.alerts = AlertSystem()

    def initialize(self) -> bool:
        sec_cfg = self.config.get('security', {})
        key_file = sec_cfg.get('key_file', 'config/key.key')
        credentials_file = sec_cfg.get('credentials_file', 'config/credentials.enc')
        try:
            creds = load_credentials(path=credentials_file, key_path=key_file)
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            return False
        if not creds:
            self.logger.error("Invalid credentials.")
            return False

        # Initialize MetaTrader 5 terminal
        terminal_path = "C:\\pythonproject\\DeepSeek-FX-Pro\\mt5\\terminal64.exe"  # Adjust path as needed
        if not mt5.initialize(path=terminal_path):
            self.logger.error(f"MetaTrader 5 initialization failed, error code = {mt5.last_error()}")
            return False

        # Log in to trading account
        login = int(creds["login"])  # Ensure login is an integer
        password = creds["password"]
        server = creds["server"]
        if not mt5.login(login, password=password, server=server):
            self.logger.error(f"Login failed, error code = {mt5.last_error()}")
            return False

        return True

    def run(self, mode: str = 'live', symbols: list = None) -> None:
        if not self.initialize():
            self.logger.error("Initialization failed. Exiting.")
            return
        symbol_list = symbols if mode == 'live' and symbols else self.config.get('strategy', {}).get('symbols', [])
        timeframe = self.config.get('strategy', {}).get('timeframes', [60])[0]
        bars = self.config.get('strategy', {}).get('bars', 500)
        self.logger.info("Starting %s mode for symbols: %s", mode, symbol_list)
        for symbol in symbol_list:
            try:
                self.run_cycle(symbol, timeframe, bars)
            except Exception as e:
                self.logger.exception("Error in run_cycle for %s: %s", symbol, e)
        self.logger.info("Run complete.")

    def run_cycle(self, symbol: str, timeframe: int, bars: int) -> None:
        data = self.data_feed.get_ohlcv(symbol, timeframe, bars)
        if data is None:
            self.logger.warning(f"No data for {symbol}")
            return
        forecast = self.forecaster.predict(symbol, data)
        strategy = self.strategy_generator.generate(data, forecast)
        if self.risk_evaluator.evaluate(strategy):
            self.executor.execute(strategy)
            self.portfolio_manager.update_position(strategy['symbol'], strategy['volume'])
            self.performance_tracker.record_trade(strategy.get('expected_pnl', 0))
            model = strategy.get('model')
            if model:
                self.model_updater.save_model(symbol, model)
            self.alerts.send(f"Trade executed for {strategy['symbol']}")
        else:
            self.logger.info("Trade for %s did not pass risk checks.", symbol)
