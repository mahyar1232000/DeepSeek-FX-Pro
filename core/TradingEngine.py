# core/TradingEngine.py

import logging
import os
from typing import Dict, Any

from broker_interface.MT5Controller import MT5Controller
from broker_interface.DataFeed import DataFeed
from broker_interface.OrderManager import OrderManager
from core.OrderExecutor import OrderExecutor
from ai_engine.ModelUpdater import ModelUpdater
from ai_engine.StrategyGenerator import StrategyGenerator
from ai_engine.RiskEvaluator import RiskEvaluator
from core.PortfolioManager import PortfolioManager
from core.PerformanceTracker import PerformanceTracker
from core.AlertSystem import AlertSystem

class TradingEngine:
    def __init__(self, cfg: Dict[str, Any], creds: Dict[str, Any]):
        # Setup logging
        logging.basicConfig(level=cfg['logging']['level'])
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = str(cfg['logging']['tf_log_level'])

        # Broker & data interfaces
        self.mt5       = MT5Controller()
        self.data_feed = DataFeed()

        # Execution & portfolio
        self.executor  = OrderExecutor(OrderManager())
        self.portfolio = PortfolioManager()
        self.tracker   = PerformanceTracker()
        self.alerts    = AlertSystem()

        # Risk evaluator
        self.risk_eval = RiskEvaluator(cfg['risk'])

        # Model & strategy generator
        os.makedirs(cfg['model']['path'], exist_ok=True)
        updater = ModelUpdater(save_dir=cfg['model']['path'])
        self.strategy_gen = StrategyGenerator(model_updater=updater)

        # Store config and credentials
        self.cfg   = cfg
        self.creds = creds

    def initialize(self) -> bool:
        """Initialize MT5 connection using decrypted credentials."""
        return self.mt5.connect(
            login=self.creds["login"],
            password=self.creds["password"],
            server=self.creds["server"]
        )

    def run_cycle(self, symbol: str, timeframe: int, bars: int):
        """Fetch data, generate/trade on strategy, and update performance."""
        df = self.data_feed.get_ohlcv(symbol, timeframe, bars)
        if df is None:
            return

        # Build feature arrays for both training and prediction
        data = {
            "close":     df["close"].to_numpy(),
            "volume":    df["tick_volume"].to_numpy()
        }

        # Generate prediction (lazy trains if missing)
        action = self.strategy_gen.predict(symbol, data)
        if action is None or action == 2:   # 2 == Hold / no trade
            self.alerts.send(f"No trade signal for {symbol}")
            return

        # Compute entry, stop-loss and take-profit from config
        last_price = float(data["close"][-1])
        sl_pct = self.cfg['strategy']['stop_loss_pct']
        tp_pct = self.cfg['strategy']['take_profit_pct']

        sl = last_price * (1 - sl_pct)  # for long trades; inverse for shorts if you extend
        tp = last_price * (1 + tp_pct)
        strat = {
            "symbol":     symbol,
            "entry":      last_price,
            "stop_loss":  sl,
            "take_profit":tp
        }

        # Position sizing
        equity   = 10000.0   # replace with real equity query if available
        risk_pct = self.cfg['risk']['risk_pct']

        strat["volume"] = self.risk_eval.calculate_position_size(
            equity=equity,
            stop_loss=abs(strat["entry"] - strat["stop_loss"]),
            risk_pct=risk_pct
        )

        # Final risk check and execution
        if self.risk_eval.evaluate(strat):
            self.executor.execute(strat)
            self.portfolio.update_position(symbol, strat["volume"])
            self.tracker.record_trade(0.0)
            self.alerts.send(f"Executed trade on {symbol}")
        else:
            self.alerts.send(f"Trade for {symbol} vetoed by risk")

    def run(self, mode: str = 'live', symbols: list = None):
        """Main dispatch: initialize, then run cycles for each symbol/timeframe."""
        if not self.initialize():
            logging.error("Broker connection failed. Exiting.")
            return

        syms = symbols or self.cfg['strategy']['symbols']
        tfs  = self.cfg['strategy']['timeframes']
        bars = self.cfg['strategy']['bars']

        logging.info("Starting %s mode for symbols: %s", mode, syms)
        for sym in syms:
            for tf in tfs:
                try:
                    self.run_cycle(sym, tf, bars)
                except Exception as e:
                    logging.exception("Error in cycle %s@%d: %s", sym, tf, e)
