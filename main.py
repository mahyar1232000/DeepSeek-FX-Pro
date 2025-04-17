# main.py
# !/usr/bin/env python3
import os
import argparse
import yaml
from core.TradingEngine import TradingEngine
from utils.SecurityModule import SecurityManager, load_credentials


def parse_args():
    parser = argparse.ArgumentParser(description='DeepSeek FX Pro Trading Bot')
    parser.add_argument('--generate_key', action='store_true', help='Generate a new encryption key')
    parser.add_argument('--encrypt_credentials', action='store_true', help='Encrypt the credentials file')
    parser.add_argument('--mode', type=str, default='live', choices=['live', 'backtest'],
                        help='Trading mode: live or backtest')
    parser.add_argument('--symbols', type=str, help='Comma-separated list of symbols to trade (for live mode)')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Path to configuration file')
    return parser.parse_args()


def main():
    args = parse_args()

    if args.generate_key:
        security = SecurityManager()
        key = security.generate_key().decode()
        print(f"Generated Encryption Key: {key}")
        return

    if args.encrypt_credentials:
        security = SecurityManager()
        login = input("Enter your MT5 login: ")
        password = input("Enter your MT5 password: ")
        server = input("Enter your MT5 server: ")
        credentials = f"{login}:{password}:{server}"
        encrypted = security.encrypt_data(credentials)
        os.makedirs(os.path.dirname(args.config), exist_ok=True)
        with open('config/credentials.enc', 'wb') as f:
            f.write(encrypted)
        print(f"Credentials encrypted successfully to {os.path.abspath('config/credentials.enc')}")
        return

    # Load configuration
    if not os.path.exists(args.config):
        print(f"Configuration file {args.config} not found.")
        return

    with open(args.config, 'r') as f:
        cfg = yaml.safe_load(f)

    symbols = [s.strip() for s in args.symbols.split(',')] if args.symbols else None

    # Initialize and run trading engine
    engine = TradingEngine(cfg)
    engine.run(mode=args.mode, symbols=symbols)


if __name__ == "__main__":
    main()
