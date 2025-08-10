"""Security utilities for data encryption and hashing."""

import hashlib
import os
import base64
from typing import Optional
from cryptography.fernet import Fernet


class SecurityManager:
    """Manages encryption and hashing for sensitive data."""
    
    def __init__(self):
        """Initialize security manager with keys from environment."""
        self._encryption_key = self._get_encryption_key()
        self._salt = self._get_salt()
        self._cipher = Fernet(self._encryption_key)
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key."""
        key_str = os.getenv("ENCRYPTION_KEY")
        if not key_str:
            # Generate new key for development
            key = Fernet.generate_key()
            print(f"⚠️  Generated new encryption key: {key.decode()}")
            print("Add this to your .env file: ENCRYPTION_KEY=" + key.decode())
            return key
        return key_str.encode()
    
    def _get_salt(self) -> str:
        """Get or generate salt for hashing."""
        salt = os.getenv("SALT_KEY")
        if not salt:
            # Generate new salt for development
            salt = base64.urlsafe_b64encode(os.urandom(32)).decode()
            print(f"⚠️  Generated new salt: {salt}")
            print("Add this to your .env file: SALT_KEY=" + salt)
        return salt
    
    def hash_discord_id(self, discord_id: str) -> str:
        """Hash a Discord ID with salt for privacy."""
        combined = f"{discord_id}{self._salt}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def encrypt_text(self, text: str) -> str:
        """Encrypt sensitive text data."""
        if not text:
            return ""
        encrypted_bytes = self._cipher.encrypt(text.encode())
        return base64.urlsafe_b64encode(encrypted_bytes).decode()
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt sensitive text data."""
        if not encrypted_text:
            return ""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_bytes = self._cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            print(f"⚠️  Decryption failed: {e}")
            return "[DECRYPTION_FAILED]"
    
    def create_lookup_key(self, guild_id: str, user_id: str) -> str:
        """Create a unique lookup key for guild+user combination."""
        combined = f"{guild_id}:{user_id}:{self._salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]


# Global security manager instance
security_manager = SecurityManager()