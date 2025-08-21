"""Tests for database models."""

import os
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sqlalchemy.orm import sessionmaker

from project.database.connection import Base, engine
from project.database.models import GDPRRequest, ModerationLog, SecureWarning


class TestDatabaseModels:
    """Test database models functionality."""

    @classmethod
    def setup_class(cls):
        """Setup test database."""
        # Use in-memory SQLite for tests
        cls.Session = sessionmaker(bind=engine)

        # Create tables
        Base.metadata.create_all(bind=engine)

    def setup_method(self):
        """Setup for each test."""
        self.session = self.Session()

        # Mock environment variables for consistent testing
        # Mock environment variables with valid base64 keys
        from cryptography.fernet import Fernet

        test_key = Fernet.generate_key().decode()

        self.env_patch = patch.dict(
            os.environ,
            {
                "ENCRYPTION_KEY": test_key,
                "SALT_KEY": "dGVzdF9zYWx0XzEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg=",
                "PEPPER_KEY": "dGVzdF9wZXBwZXJfMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3",
            },
        )
        self.env_patch.start()

    def teardown_method(self):
        """Cleanup after each test."""
        # Clean up database
        self.session.query(SecureWarning).delete()
        self.session.query(ModerationLog).delete()
        self.session.query(GDPRRequest).delete()
        self.session.commit()
        self.session.close()
        self.env_patch.stop()

    def test_create_secure_warning(self):
        """Test creating a secure warning."""
        warning = SecureWarning.create_warning(
            guild_id="123456789012345678",
            user_id="987654321098765432",
            moderator_id="555666777888999000",
            reason="Test warning reason",
        )

        # Check that fields are populated
        assert warning.guild_id_hash is not None
        assert warning.user_id_hash is not None
        assert warning.moderator_id_hash is not None
        assert warning.reason_encrypted is not None
        assert warning.lookup_key is not None

        # Check that hashes are 64 characters
        assert len(warning.guild_id_hash) == 64
        assert len(warning.user_id_hash) == 64
        assert len(warning.moderator_id_hash) == 64

        # Check that lookup key is 16 characters
        assert len(warning.lookup_key) == 16

        # Check that reason can be decrypted
        decrypted_reason = warning.get_decrypted_reason()
        assert decrypted_reason == "Test warning reason"

    def test_warning_validation(self):
        """Test warning validation."""
        # Empty reason should raise error
        with pytest.raises(ValueError):
            SecureWarning.create_warning(
                guild_id="123456789012345678",
                user_id="987654321098765432",
                moderator_id="555666777888999000",
                reason="",
            )

        # Whitespace-only reason should raise error
        with pytest.raises(ValueError):
            SecureWarning.create_warning(
                guild_id="123456789012345678",
                user_id="987654321098765432",
                moderator_id="555666777888999000",
                reason="   ",
            )

    def test_warning_soft_delete(self):
        """Test soft delete functionality."""
        warning = SecureWarning.create_warning(
            guild_id="123456789012345678",
            user_id="987654321098765432",
            moderator_id="555666777888999000",
            reason="Test warning",
        )

        # Save to database to get defaults
        self.session.add(warning)
        self.session.commit()
        self.session.refresh(warning)

        # Initially not deleted
        assert warning.is_deleted is False
        assert warning.deleted_at is None

        # Soft delete
        warning.soft_delete()
        assert warning.is_deleted is True
        assert warning.deleted_at is not None
        assert isinstance(warning.deleted_at, datetime)

    def test_warning_to_dict(self):
        """Test warning dictionary conversion."""
        warning = SecureWarning.create_warning(
            guild_id="123456789012345678",
            user_id="987654321098765432",
            moderator_id="555666777888999000",
            reason="Test warning",
        )

        # Save to get ID
        self.session.add(warning)
        self.session.commit()

        # Test dictionary conversion
        warning_dict = warning.to_dict()

        assert "id" in warning_dict
        assert "reason" in warning_dict
        assert "created_at" in warning_dict
        assert "lookup_key" in warning_dict
        assert "is_deleted" in warning_dict

        assert warning_dict["reason"] == "Test warning"
        assert warning_dict["is_deleted"] is False

    def test_warning_to_dict_deleted(self):
        """Test dictionary conversion for deleted warning."""
        warning = SecureWarning.create_warning(
            guild_id="123456789012345678",
            user_id="987654321098765432",
            moderator_id="555666777888999000",
            reason="Test warning",
        )

        # Save to database to get defaults
        self.session.add(warning)
        self.session.commit()
        self.session.refresh(warning)

        warning.soft_delete()

        # Deleted warning should not include sensitive data
        warning_dict = warning.to_dict()
        assert (
            "reason" not in warning_dict
        )  # Sensitive data excluded for deleted warnings

    def test_create_moderation_log(self):
        """Test creating moderation log."""
        log = ModerationLog.create_log(
            guild_id="123456789012345678",
            user_id="987654321098765432",
            moderator_id="555666777888999000",
            action_type="warn",
            reason="Test log reason",
            context="Additional context",
        )

        assert log.guild_id_hash is not None
        assert log.user_id_hash is not None
        assert log.moderator_id_hash is not None
        assert log.action_type == "warn"
        assert log.reason_encrypted is not None
        assert log.context_encrypted is not None

        # Test decryption
        assert log.get_decrypted_reason() == "Test log reason"
        assert log.get_decrypted_context() == "Additional context"

    def test_moderation_log_validation(self):
        """Test moderation log validation."""
        # Invalid action type should raise error
        with pytest.raises(ValueError):
            ModerationLog.create_log(
                guild_id="123456789012345678",
                user_id="987654321098765432",
                moderator_id="555666777888999000",
                action_type="invalid_action",
            )

    def test_create_gdpr_request(self):
        """Test creating GDPR request."""
        request = GDPRRequest.create_request(
            user_id="987654321098765432", request_type="export"
        )

        # Save to database to get defaults
        self.session.add(request)
        self.session.commit()
        self.session.refresh(request)

        assert request.user_id_hash is not None
        assert request.request_type == "export"
        assert request.status == "pending"
        assert request.created_at is not None
        assert request.completed_at is None
