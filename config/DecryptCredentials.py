from cryptography.fernet import Fernet
import json

# Load the key
with open('key.key', 'rb') as key_file:
    key = key_file.read()

# Load and decrypt the credentials
with open('credentials.enc', 'rb') as enc_file:
    encrypted_data = enc_file.read()

fernet = Fernet(key)
decrypted_data = fernet.decrypt(encrypted_data)
credentials = json.loads(decrypted_data.decode())

print(credentials)
