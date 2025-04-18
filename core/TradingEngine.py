# core/TradingEngine.py
import os, logging, MetaTrader5 as mt5
from typing import List
from broker_interface.MT5Controller import MT5Controller       # :contentReference[oaicite:4]{index=4}
from broker_interface.DataFeed    import DataFeed             # :contentReference[oaicite:5]{index=5}
from broker_interface.OrderManager import OrderManager
from core.OrderExecutor           import OrderExecutor
from core.PortfolioManager        import PortfolioManager     # :contentReference[oaicite:6]{index=6}
from core.PerformanceTracker      import PerformanceTracker
from core.AlertSystem             import AlertSystem
from ai_engine.StrategyGenerator  import StrategyGenerator
from ai_engine.RiskEvaluator      import RiskEvaluator
from ai_engine.ModelUpdater       import ModelUpdater
from ai_engine.ForecastModule     import ForecastModule      # :contentReference[oaicite:7]{index=7}
from utils.SecurityModule         import load_credentials   # :contentReference[oaicite:8]{index=8}

class TradingEngine:
    def __init__(self, cfg: dict, creds: dict):
        self.cfg = cfg
        self.creds = creds

        # Logging & TF
        loglvl = cfg['logging']['level'].upper()
        logging.basicConfig(level=getattr(logging, loglvl))
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = cfg['logging']['tf_log_level']

        # MT5 & data
        self.mt5 = MT5Controller()
        self.data_feed = DataFeed()

        # Strategy & execution
        self.strategy_gen = StrategyGenerator()
        self.risk_eval    = RiskEvaluator(cfg['risk'])
        self.executor     = OrderExecutor(OrderManager())
        self.portfolio    = PortfolioManager()
        self.tracker      = PerformanceTracker()
        self.alerts       = AlertSystem()

        # Models
        os.makedirs(cfg['model']['path'], exist_ok=True)
        self.model_updater = ModelUpdater(cfg['model']['path'])
        self.forecaster    = ForecastModule(self.model_updater)

    def initialize(self) -> bool:
        # load & apply credentials
        try:
            creds = self.creds
        except Exception as e:
            logging.error("Cred load error: %s", e)
            return False

        # MT5 init & login
        if not self.mt5.connect(
            login=creds["login"], password=creds["password"], server=creds["server"]
        ):
            return False
        return True

    def run_cycle(self, symbol: str, timeframe: int, bars: int):
        df = self.data_feed.get_ohlcv(symbol, timeframe, bars)
        if df is None:
            return

        features = {"close": df["close"].to_numpy(), "volume": df["tick_volume"].to_numpy()}
        # ensure forecasting model is loaded
        _ = self.forecaster.forecast(symbol, df)

        # generate a concrete strategy dict
        strat = self.strategy_gen.generate_market_strategy(
            data=features,
            symbol=symbol,
            stop_loss_pct=self.cfg['strategy']['stop_loss_pct'],
            take_profit_pct=self.cfg['strategy']['take_profit_pct']
        )

        # skip if no actionable trade
        if strat is None:
            logging.info("No trade signal for %s", symbol)
            return

        # compute volume from risk
        # Here you'd pull your real equity; we'll assume 10000 for example
        equity = 10000.0
        strat['volume'] = self.risk_eval.calculate_position_size(
            equity=equity,
            stop_loss=strat['stop_loss'] - strat['entry'],
            risk_pct=self.cfg['risk']['risk_pct']
        )

        # risk‐check then execute
        if self.risk_eval.evaluate(strat):
            self.executor.execute(strat)
            self.portfolio.update_position(strat['symbol'], strat['volume'])
            self.tracker.record_trade(strat.get('expected_pnl', 0.0))
            self.model_updater.save_model(symbol, self.strategy_gen.model_registry.get(symbol))
            self.alerts.send(f"Executed trade for {symbol}")
        else:
            logging.info("Trade for %s skipped by risk", symbol)

    def run(self, mode: str = 'live', symbols: List[str] = None):
        if not self.initialize():
            return
        syms = symbols or self.cfg['strategy']['symbols']
        for tf in self.cfg['strategy']['timeframes']:
            for sym in syms:
                try:
                    self.run_cycle(sym, tf, self.cfg['strategy']['bars'])
                except Exception as e:
                    logging.exception("Error in cycle %s@%d: %s", sym, tf, e)
