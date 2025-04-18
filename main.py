#!/usr/bin/env python3
import os, argparse, yaml, logging
from core.TradingEngine import TradingEngine
from utils.SecurityModule import SecurityManager, load_credentials

def load_config(path="config/config.yaml") -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def parse_args():
    p = argparse.ArgumentParser("DeepSeek FX Pro")
    p.add_argument('--generate_key', action='store_true',
                   help='Create a new Fernet key and save to config/key.key')
    p.add_argument('--encrypt_credentials', action='store_true',
                   help='Interactively encrypt your MT5 login into config/credentials.enc')
    p.add_argument('--mode', choices=['live','backtest'], default='live',
                   help='Trading mode')
    p.add_argument('--symbols', type=str,
                   help='Comma‑separated list of symbols (overrides config)')
    return p.parse_args()

def main():
    args = parse_args()
    cfg = load_config()

    # 1) Key generation
    if args.generate_key:
        km = SecurityManager(cfg['security']['key_file'])
        print("Key written to", cfg['security']['key_file'])
        return

    # 2) Encrypt credentials
    if args.encrypt_credentials:
        km = SecurityManager(cfg['security']['key_file'])
        creds = {
            "login": input("MT5 Login: "),
            "password": input("MT5 Password: "),
            "server": input("MT5 Server: ")
        }
        token = km.encrypt_credentials(creds)
        os.makedirs(os.path.dirname(cfg['security']['credentials_file']), exist_ok=True)
        with open(cfg['security']['credentials_file'], 'wb') as f:
            f.write(token)
        print("Encrypted credentials to", cfg['security']['credentials_file'])
        return

    # 3) Live or backtest run
    # 3.1 Load credentials
    try:
        creds = load_credentials(
            path=cfg['security']['credentials_file'],
            key_path=cfg['security']['key_file']
        )
    except Exception as e:
        logging.error("Failed to load credentials: %s", e)
        return

    # 3.2 Determine symbols
    if args.mode == 'live' and args.symbols:
        syms = [s.strip() for s in args.symbols.split(',')]
    else:
        syms = cfg['strategy']['symbols']

    # 3.3 Initialize & run
    engine = TradingEngine(cfg, creds)
    engine.run(mode=args.mode, symbols=syms)

if __name__ == "__main__":
    main()
