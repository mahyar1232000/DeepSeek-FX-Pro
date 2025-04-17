# utils/SecurityModule.py
import os
import json
from cryptography.fernet import Fernet


def load_key(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Encryption key file '{path}' not found.")
    with open(path, 'rb') as f:
        return f.read()


def load_credentials(path: str, key_path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Credentials file '{path}' not found.")
    key = load_key(key_path)
    encrypted_data = open(path, 'rb').read()
    try:
        decrypted_data = Fernet(key).decrypt(encrypted_data).decode()
        credentials = json.loads(decrypted_data)
        login = int(credentials["login"])
        password = credentials["password"]
        server = credentials["server"]
        return {"login": login, "password": password, "server": server}
    except Exception as e:
        print(f"Error decrypting credentials: {e}")
        return None


class SecurityManager:
    def __init__(self, key_path: str = 'config/key.key'):
        self.key_path = key_path
        if not os.path.exists(self.key_path):
            self.key = self.generate_key()
        else:
            self.key = load_key(self.key_path)
        self.fernet = Fernet(self.key)

    def generate_key(self) -> bytes:
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
        with open(self.key_path, 'wb') as f:
            f.write(key)
        return key

    def encrypt_data(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        return self.fernet.decrypt(encrypted_data).decode()
