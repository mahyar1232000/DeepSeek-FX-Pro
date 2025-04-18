# utils/SecurityModule.py
import os, json
from cryptography.fernet import Fernet


def load_key(path: str) -> bytes:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Encryption key file '{path}' not found.")
    return open(path, 'rb').read()


def load_credentials(path: str, key_path: str) -> dict:
    """Decrypts a JSON credentials file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Credentials file '{path}' not found.")
    key = load_key(key_path)
    encrypted_data = open(path, 'rb').read()
    try:
        decrypted = Fernet(key).decrypt(encrypted_data).decode('utf-8')
        creds = json.loads(decrypted)
        return {
            "login": int(creds["login"]),
            "password": creds["password"],
            "server": creds["server"]
        }
    except Exception as e:
        raise ValueError(f"Error decrypting credentials: {e}")


class SecurityManager:
    def __init__(self, key_path: str = 'config/key.key'):
        self.key_path = key_path
        if not os.path.exists(self.key_path):
            os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
            with open(self.key_path, 'wb') as f:
                f.write(Fernet.generate_key())
        self.fernet = Fernet(load_key(self.key_path))

    def encrypt_credentials(self, credentials: dict) -> bytes:
        """Encrypts a credentials dict into bytes."""
        payload = json.dumps(credentials)
        return self.fernet.encrypt(payload.encode('utf-8'))

    def decrypt_credentials(self, encrypted_data: bytes) -> dict:
        return json.loads(self.fernet.decrypt(encrypted_data).decode('utf-8'))
