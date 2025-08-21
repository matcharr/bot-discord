"""Tests for database security functionality."""

import pytest
import os
from unittest.mock import patch
from project.database.security import SecurityManager


class TestSecurityManager:
    """Test security manager functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        # Use valid base64 test keys
        from cryptography.fernet import Fernet
        test_key = Fernet.generate_key().decode()
        
        with patch.dict(os.environ, {
            'ENCRYPTION_KEY': test_key,
            'SALT_KEY': 'dGVzdF9zYWx0XzEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg=',
            'PEPPER_KEY': 'dGVzdF9wZXBwZXJfMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3'
        }):
            self.security = SecurityManager()
    
    def test_hash_discord_id(self):
        """Test Discord ID hashing."""
        user_id = "123456789012345678"
        
        # Hash should be consistent
        hash1 = self.security.hash_discord_id(user_id)
        hash2 = self.security.hash_discord_id(user_id)
        assert hash1 == hash2
        
        # Different IDs should produce different hashes
        different_id = "987654321098765432"
        hash3 = self.security.hash_discord_id(different_id)
        assert hash1 != hash3
        
        # Hash should be 64 characters (SHA-256)
        assert len(hash1) == 64
        assert all(c in '0123456789abcdef' for c in hash1)
    
    def test_encrypt_decrypt_text(self):
        """Test text encryption and decryption."""
        original_text = "This is a test warning reason with émojis 🚨"
        
        # Encrypt
        encrypted = self.security.encrypt_text(original_text)
        assert encrypted != original_text
        assert len(encrypted) > len(original_text)
        
        # Decrypt
        decrypted = self.security.decrypt_text(encrypted)
        assert decrypted == original_text
    
    def test_encrypt_empty_text(self):
        """Test encryption of empty text."""
        assert self.security.encrypt_text("") == ""
        assert self.security.encrypt_text(None) == ""
    
    def test_decrypt_empty_text(self):
        """Test decryption of empty text."""
        assert self.security.decrypt_text("") == ""
        assert self.security.decrypt_text(None) == ""
    
    def test_decrypt_invalid_data(self):
        """Test decryption of invalid data."""
        with pytest.raises(ValueError):
            self.security.decrypt_text("invalid_encrypted_data")
    
    def test_create_lookup_key(self):
        """Test lookup key creation."""
        guild_id = "123456789012345678"
        user_id = "987654321098765432"
        
        # Lookup key should be consistent
        key1 = self.security.create_lookup_key(guild_id, user_id)
        key2 = self.security.create_lookup_key(guild_id, user_id)
        assert key1 == key2
        
        # Different combinations should produce different keys
        key3 = self.security.create_lookup_key(user_id, guild_id)  # Swapped
        assert key1 != key3
        
        # Key should be 16 characters
        assert len(key1) == 16
    
    def test_secure_compare(self):
        """Test timing-safe string comparison."""
        string1 = "test_string_123"
        string2 = "test_string_123"
        string3 = "different_string"
        
        assert self.security.secure_compare(string1, string2) is True
        assert self.security.secure_compare(string1, string3) is False
    
    def test_anonymize_for_logs(self):
        """Test log anonymization."""
        user_id = "123456789012345678"
        
        # Should produce consistent anonymized ID
        anon1 = self.security.anonymize_for_logs(user_id)
        anon2 = self.security.anonymize_for_logs(user_id)
        assert anon1 == anon2
        
        # Should be different from main hash
        main_hash = self.security.hash_discord_id(user_id)
        assert anon1 != main_hash
        
        # Should be 8 characters for logs
        assert len(anon1) == 8