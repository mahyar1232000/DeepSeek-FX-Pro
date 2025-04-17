# ---------- utils/SecurityModule.py ----------
"""
Handles encryption and decryption of sensitive configuration.
"""
from cryptography.fernet import Fernet
import json


def generate_key() -> None:
    key = Fernet.generate_key()
    with open("config/key.key", "wb") as key_file:
        key_file.write(key)


def load_key() -> bytes:
    with open("config/key.key", "rb") as key_file:
        return key_file.read()


def encrypt_file(input_path: str, output_path: str, key: bytes) -> None:
    with open(input_path, "rb") as file:
        data = file.read()
    f = Fernet(key)
    encrypted = f.encrypt(data)
    with open(output_path, "wb") as file:
        file.write(encrypted)


def decrypt_file(input_path: str, key: bytes) -> bytes:
    with open(input_path, "rb") as file:
        data = file.read()
    f = Fernet(key)
    return f.decrypt(data)


def load_credentials() -> dict:
    key = load_key()
    decrypted = decrypt_file("config/credentials.enc", key)
    return json.loads(decrypted)
