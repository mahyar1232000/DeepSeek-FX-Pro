# ---------- utils/SecurityModule.py ----------
"""
Handles encryption and decryption of sensitive configuration.
"""
import os
import json
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def generate_key(path: str = "config/key.key") -> bytes:
    """
    Generate a new Fernet key and save it to `path`.
    """
    key = Fernet.generate_key()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as key_file:
        key_file.write(key)
    logger.info("Generated new Fernet key at %s", path)
    return key


def load_key(path: str = "config/key.key") -> bytes:
    """
    Load the Fernet key from an environment variable or file.
    """
    env_key = os.getenv("FERNET_KEY")
    if env_key:
        logger.info("Loaded Fernet key from environment variable FERNET_KEY")
        return env_key.encode()
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fernet key not found at {path}. "
                                "Run generate_key() to create one.")
    with open(path, "rb") as key_file:
        key = key_file.read().strip()
    return key


def encrypt_file(input_path: str, output_path: str, key: bytes) -> None:
    """
    Encrypt `input_path` to `output_path` using the provided key.
    """
    with open(input_path, "rb") as f:
        data = f.read()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(encrypted)
    logger.info("Encrypted %s to %s", input_path, output_path)


def decrypt_file(input_path: str, key: bytes) -> bytes:
    """
    Decrypt `input_path` using the provided key.
    """
    with open(input_path, "rb") as f:
        data = f.read()
    fernet = Fernet(key)
    try:
        return fernet.decrypt(data)
    except InvalidToken as e:
        raise ValueError(
            "Invalid Fernet key or corrupted encrypted credentials file."
        ) from e


def load_credentials(
    enc_path: str = None,
    key_path: str = None
) -> dict:
    """
    Load and decrypt JSON credentials from the encrypted file.
    """
    # fallback to config defaults if not passed
    enc_path = enc_path or os.getenv('CREDENTIALS_FILE', 'config/credentials.enc')
    key_path = key_path or os.getenv('FERNET_KEY_FILE', 'config/key.key')

    key = load_key(key_path)
    decrypted = decrypt_file(enc_path, key)
    return json.loads(decrypted)
