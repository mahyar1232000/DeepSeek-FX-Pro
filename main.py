# ---------- main.py ----------
import logging
import yaml
from core.TradingEngine import TradingEngine
from utils.AdvancedLogger import setup_logger


def load_config(path: str = 'config/config.yaml') -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    setup_logger('DeepSeekFX', config['log_file'])
    engine = TradingEngine()
    if not engine.initialize():
        logging.error("Failed to connect to broker.")
        return

    for symbol in config['symbols']:
        engine.run_cycle(symbol, config['timeframe'], config['bars'])


if __name__ == "__main__":
    main()
