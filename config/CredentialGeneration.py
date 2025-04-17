import json
import os
from cryptography.fernet import Fernet


def generate_key(key_path='key.key'):
    """
    Generates a Fernet key and saves it to a file.
    """
    key = Fernet.generate_key()
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
    return key


def load_key(key_path='key.key'):
    """
    Loads the Fernet key from a file.
    """
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Key file '{key_path}' not found.")
    with open(key_path, 'rb') as key_file:
        return key_file.read()


def encrypt_credentials(credentials, key):
    """
    Encrypts the credentials dictionary using the provided key.
    """
    fernet = Fernet(key)
    credentials_json = json.dumps(credentials)
    encrypted_data = fernet.encrypt(credentials_json.encode())
    return encrypted_data


def save_encrypted_credentials(encrypted_data, output_path='credentials.enc'):
    """
    Saves the encrypted credentials to a file.
    """
    with open(output_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted_data)


def main():
    # Define your credentials
    credentials = {
        "login": 90217066,
        "password": "Mahyar1232000@",
        "server": "LiteFinance-MT5-Demo"
    }

    # Generate and save the key
    key = generate_key()

    # Encrypt the credentials
    encrypted_data = encrypt_credentials(credentials, key)

    # Save the encrypted credentials
    save_encrypted_credentials(encrypted_data)

    print("Credentials have been encrypted and saved successfully.")


if __name__ == "__main__":
    main()
