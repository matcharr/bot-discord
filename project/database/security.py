"""Security utilities for data encryption and hashing."""

import base64
import hashlib
import logging
import os
import secrets
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class SecurityManager:
    """Manages encryption and hashing for sensitive data with enterprise-grade security."""

    def __init__(self):
        """Initialize security manager with keys from environment."""
        self._encryption_key = self._get_encryption_key()
        self._salt = self._get_salt()
        self._pepper = self._get_pepper()  # Additional security layer
        self._cipher = Fernet(self._encryption_key)

    def _get_encryption_key(self) -> bytes:
        """Get or derive encryption key using PBKDF2."""
        key_str = os.getenv("ENCRYPTION_KEY")
        if not key_str:
            # Generate cryptographically secure key for development
            key = Fernet.generate_key()
            logger.warning(
                "Generated new encryption key. Add ENCRYPTION_KEY to your .env file"
            )
            # Only show the key in a secure way, not in logs
            print(f"ENCRYPTION_KEY={key.decode()}")
            return key

        # If key is a password, derive it properly
        if len(key_str) < 32:  # Likely a password, not a key
            salt = os.getenv("KEY_DERIVATION_SALT", "default_salt").encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,  # OWASP recommended minimum
            )
            key = base64.urlsafe_b64encode(kdf.derive(key_str.encode()))
            return key

        return key_str.encode()

    def _get_salt(self) -> str:
        """Get or generate cryptographically secure salt."""
        salt = os.getenv("SALT_KEY")
        if not salt:
            # Generate cryptographically secure salt
            salt = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
            logger.warning("Generated new salt. Add SALT_KEY to your .env file")
            print(f"SALT_KEY={salt}")
        return salt

    def _get_pepper(self) -> str:
        """Get or generate pepper (server-side secret for additional security)."""
        pepper = os.getenv("PEPPER_KEY")
        if not pepper:
            pepper = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
            logger.warning("Generated new pepper. Add PEPPER_KEY to your .env file")
            print(f"PEPPER_KEY={pepper}")
        return pepper

    def hash_discord_id(self, discord_id: str) -> str:
        """Hash a Discord ID with salt and pepper for maximum privacy."""
        # Use both salt and pepper for defense in depth
        combined = f"{discord_id}{self._salt}{self._pepper}"
        # Use SHA-256 with multiple rounds for additional security
        hash_obj = hashlib.sha256(combined.encode())
        for _ in range(1000):  # 1000 rounds of hashing
            hash_obj = hashlib.sha256(hash_obj.digest())
        return hash_obj.hexdigest()

    def encrypt_text(self, text: str) -> str:
        """Encrypt sensitive text data with authenticated encryption."""
        if not text:
            return ""
        try:
            # Fernet provides authenticated encryption (AES 128 + HMAC)
            encrypted_bytes = self._cipher.encrypt(text.encode("utf-8"))
            return base64.urlsafe_b64encode(encrypted_bytes).decode("ascii")
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise ValueError("Failed to encrypt data")

    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt sensitive text data with integrity verification."""
        if not encrypted_text:
            return ""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode("ascii"))
            decrypted_bytes = self._cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            # Don't return partial data on failure
            raise ValueError("Failed to decrypt data - data may be corrupted")

    def create_lookup_key(self, guild_id: str, user_id: str) -> str:
        """Create a unique lookup key for guild+user combination."""
        # Use HMAC for lookup keys to prevent length extension attacks
        import hmac

        combined = f"{guild_id}:{user_id}"
        lookup_hash = hmac.new(
            self._pepper.encode(), combined.encode(), hashlib.sha256
        ).hexdigest()
        return lookup_hash[:16]  # Truncate for database efficiency

    def secure_compare(self, a: str, b: str) -> bool:
        """Timing-safe string comparison to prevent timing attacks."""
        return secrets.compare_digest(a, b)

    def anonymize_for_logs(self, discord_id: str) -> str:
        """Create a consistent but anonymous ID for logging purposes."""
        # Different from main hash to prevent correlation
        log_salt = "logging_salt_" + self._salt
        combined = f"{discord_id}{log_salt}"
        return hashlib.sha256(combined.encode()).hexdigest()[:8]


# Global security manager instance
security_manager = SecurityManager()
