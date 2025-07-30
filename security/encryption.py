from cryptography.fernet import Fernet
import base64
import os
from dotenv import load_dotenv

load_dotenv()

class DataEncryptor:
    def __init__(self):
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY environment variable not set")
        
        # Ensure key is 32 url-safe base64-encoded bytes
        if len(key) != 44:
            raise ValueError("Invalid encryption key length")
        
        self.cipher = Fernet(key.encode())

    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Initialize on module load
encryptor = DataEncryptor()

def encrypt_field(data: str) -> str:
    """Helper function for field encryption"""
    if not data:
        return data
    return encryptor.encrypt(data)

def decrypt_field(encrypted_data: str) -> str:
    """Helper function for field decryption"""
    if not encrypted_data:
        return encrypted_data
    return encryptor.decrypt(encrypted_data)