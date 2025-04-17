# utils/SecurityModule.py
import os
import base64
from cryptography.fernet import Fernet


def load_key(path='config/secret.key'):
    if not os.path.exists(path):
        raise FileNotFoundError("Encryption key file not found.")
    with open(path, 'rb') as f:
        return f.read()


def load_credentials(path='config/credentials.enc', key_path='config/secret.key'):
    try:
        key = load_key(key_path)
        with open(path, 'rb') as f:
            encrypted_data = f.read()
        decrypted = Fernet(key).decrypt(encrypted_data).decode()
        login, password, server = decrypted.split(":")
        return {"login": login, "password": password, "server": server}
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None


class SecurityManager:
    def __init__(self, key_path='config/secret.key'):
        self.key_path = key_path
        if not os.path.exists(self.key_path):
            self.key = self.generate_key()
        else:
            self.key = load_key(self.key_path)
        self.fernet = Fernet(self.key)

    def generate_key(self):
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
        with open(self.key_path, 'wb') as f:
            f.write(key)
        return key

    def encrypt_data(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode())

    def decrypt_data(self, encrypted_data: bytes) -> str:
        return self.fernet.decrypt(encrypted_data).decode()
