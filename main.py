# ---------- main.py ----------

import os
import json
import logging

import yaml
from core.TradingEngine import TradingEngine
from utils.AdvancedLogger import setup_logger

def load_config(path: str = 'config/config.yaml') -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def main():
    config = load_config()

    # --- Setup logging ---
    log_conf = config['logging']
    log_file = log_conf['file']                 # was KeyError before :contentReference[oaicite:2]{index=2}
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    level = getattr(logging, log_conf.get('level', 'INFO').upper(), logging.INFO)
    setup_logger('DeepSeekFX', log_file, level)  # matches AdvancedLogger signature :contentReference[oaicite:3]{index=3}

    # --- Load strategy settings ---
    with open(config['strategy']['symbols'], 'r') as f:
        symbols = json.load(f)                  # e.g. ["EURUSD_o", ...] :contentReference[oaicite:4]{index=4}

    timeframes = config['strategy']['timeframes']
    bars = config['strategy']['bars']

    with open(config['strategy']['risk_params'], 'r') as f:
        risk_params = json.load(f)              # max_risk_per_trade, etc. :contentReference[oaicite:5]{index=5}

    # --- Initialize and run ---
    engine = TradingEngine(risk_params=risk_params)
    if not engine.initialize():
        logging.error("Failed to connect to broker.")
        return

    for tf in timeframes:
        for symbol in symbols:
            engine.run_cycle(symbol, tf, bars)

if __name__ == "__main__":
    main()
