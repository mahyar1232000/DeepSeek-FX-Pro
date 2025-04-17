# ---------- main.py ----------
import os
import json
import logging

import yaml
from core.TradingEngine import TradingEngine
from utils.AdvancedLogger import setup_logger
from utils.SecurityModule import load_credentials


def load_config(path: str = 'config/config.yaml') -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def main():
    config = load_config()

    # --- Setup logging ---
    log_conf = config['logging']
    log_file = log_conf['file']
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    level = getattr(logging, log_conf.get('level', 'INFO').upper(), logging.INFO)
    setup_logger('DeepSeekFX', log_file, level)

    # --- Load credentials ---
    try:
        creds = load_credentials(
            key_path=config['security']['key_file'],
            enc_path=config['security']['credentials_file']
        )
    except Exception as e:
        logging.error("Unable to load credentials: %s", e)
        logging.error("Make sure you've generated a key and encrypted credentials.")
        return

    # --- Load strategy settings ---
    with open(config['strategy']['symbols'], 'r') as f:
        symbols = json.load(f)
    timeframes = config['strategy']['timeframes']
    bars = config['strategy']['bars']
    with open(config['strategy']['risk_params'], 'r') as f:
        risk_params = json.load(f)

    # --- Initialize engine ---
    engine = TradingEngine(risk_params=risk_params, creds=creds)
    if not engine.initialize():
        logging.error("Failed to connect to broker.")
        return

    # --- Run cycles ---
    for tf in timeframes:
        for symbol in symbols:
            engine.run_cycle(symbol, tf, bars)


if __name__ == "__main__":
    main()
