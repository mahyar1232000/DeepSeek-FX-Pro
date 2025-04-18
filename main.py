# main.py
import os, json, argparse, yaml, logging
from core.TradingEngine import TradingEngine
from utils.SecurityModule import load_credentials, SecurityManager


def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f)


def parse_args():
    p = argparse.ArgumentParser("DeepSeek FX Pro")
    p.add_argument("--mode", choices=["live", "backtest"], default="live")
    p.add_argument("--symbols", type=str, help="Comma‐separated symbols for live mode")
    p.add_argument("--generate_key", action="store_true")
    p.add_argument("--encrypt_credentials", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()
    cfg = load_config()

    # -- Key generation & credential encryption --
    if args.generate_key:
        km = SecurityManager(key_path=cfg["security"]["key_file"])
        print("Key written to", cfg["security"]["key_file"])
        return

    if args.encrypt_credentials:
        km = SecurityManager(key_path=cfg["security"]["key_file"])
        creds = {
            "login": input("MT5 Login: "),
            "password": input("MT5 Password: "),
            "server": input("MT5 Server: ")
        }
        enc = km.encrypt_credentials(creds)
        os.makedirs(os.path.dirname(cfg["security"]["credentials_file"]), exist_ok=True)
        with open(cfg["security"]["credentials_file"], "wb") as f:
            f.write(enc)
        print("Encrypted credentials to", cfg["security"]["credentials_file"])
        return

    # -- Live/backtest execution --
    creds = load_credentials(
        path=cfg["security"]["credentials_file"],
        key_path=cfg["security"]["key_file"]
    )
    risk = json.load(open(cfg["strategy"]["risk_params_file"]))
    symbols = json.load(open(cfg["strategy"]["symbols_file"]))
    engine = TradingEngine(risk_params=risk, creds=creds)

    if not engine.initialize():
        logging.error("Failed to connect to broker. Exiting.")
        return

    if args.mode == "live":
        syms = [s.strip() for s in args.symbols.split(",")] if args.symbols else symbols
        for tf in cfg["strategy"]["timeframes"]:
            for sym in syms:
                engine.run_cycle(sym, tf, cfg["strategy"]["bars"])
    else:
        # backtest implementation here...
        pass


if __name__ == "__main__":
    main()
