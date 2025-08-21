"""Tests for database services."""

import os
from unittest.mock import patch

import pytest
from sqlalchemy.orm import sessionmaker

from project.database.connection import Base, engine
from project.database.models import SecureWarning
from project.database.services import WarningService


class TestWarningService:
    """Test warning service functionality."""

    @classmethod
    def setup_class(cls):
        """Setup test database."""
        cls.Session = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=engine)

    def setup_method(self):
        """Setup for each test."""
        # Mock environment variables
        self.env_patch = patch.dict(
            os.environ,
            {
                "ENCRYPTION_KEY": "test_key_12345678901234567890123456789012",
                "SALT_KEY": "test_salt_1234567890123456789012345678",
                "PEPPER_KEY": "test_pepper_123456789012345678901234567",
            },
        )
        self.env_patch.start()

        # Create service
        self.service = WarningService()

        # Close any existing session and create a fresh one
        if hasattr(self.service, "db"):
            self.service.db.close()
        self.service.db = self.Session()

    def teardown_method(self):
        """Cleanup after each test."""
        # Clean up database
        self.service.db.query(SecureWarning).delete()
        self.service.db.commit()
        self.service.close()
        self.env_patch.stop()

    def test_add_warning(self):
        """Test adding a warning."""
        warning = self.service.add_warning(
            guild_id="123456789012345678",
            user_id="987654321098765432",
            moderator_id="555666777888999000",
            reason="Test warning reason",
        )

        assert warning.id is not None
        assert warning.get_decrypted_reason() == "Test warning reason"

        # Verify it's in database
        db_warning = (
            self.service.db.query(SecureWarning)
            .filter(SecureWarning.id == warning.id)
            .first()
        )
        assert db_warning is not None

    def test_add_warning_empty_reason(self):
        """Test adding warning with empty reason."""
        with pytest.raises(ValueError):
            self.service.add_warning(
                guild_id="123456789012345678",
                user_id="987654321098765432",
                moderator_id="555666777888999000",
                reason="",
            )

    def test_get_user_warnings(self):
        """Test getting user warnings."""
        guild_id = "123456789012345678"
        user_id = "987654321098765432"
        moderator_id = "555666777888999000"

        # Add multiple warnings
        warning1 = self.service.add_warning(
            guild_id, user_id, moderator_id, "First warning"
        )
        warning2 = self.service.add_warning(
            guild_id, user_id, moderator_id, "Second warning"
        )

        # Get warnings
        warnings = self.service.get_user_warnings(guild_id, user_id)

        assert len(warnings) == 2
        # Should be ordered by created_at desc (newest first)
        assert warnings[0].id == warning2.id
        assert warnings[1].id == warning1.id

    def test_get_user_warnings_different_guild(self):
        """Test that warnings are isolated by guild."""
        guild1 = "123456789012345678"
        guild2 = "876543210987654321"
        user_id = "987654321098765432"
        moderator_id = "555666777888999000"

        # Add warning to guild1
        self.service.add_warning(guild1, user_id, moderator_id, "Guild 1 warning")

        # Add warning to guild2
        self.service.add_warning(guild2, user_id, moderator_id, "Guild 2 warning")

        # Each guild should only see its own warnings
        guild1_warnings = self.service.get_user_warnings(guild1, user_id)
        guild2_warnings = self.service.get_user_warnings(guild2, user_id)

        assert len(guild1_warnings) == 1
        assert len(guild2_warnings) == 1
        assert guild1_warnings[0].get_decrypted_reason() == "Guild 1 warning"
        assert guild2_warnings[0].get_decrypted_reason() == "Guild 2 warning"

    def test_get_warning_count(self):
        """Test getting warning count."""
        guild_id = "123456789012345678"
        user_id = "987654321098765432"
        moderator_id = "555666777888999000"

        # Initially no warnings
        assert self.service.get_warning_count(guild_id, user_id) == 0

        # Add warnings
        self.service.add_warning(guild_id, user_id, moderator_id, "Warning 1")
        assert self.service.get_warning_count(guild_id, user_id) == 1

        self.service.add_warning(guild_id, user_id, moderator_id, "Warning 2")
        assert self.service.get_warning_count(guild_id, user_id) == 2

    def test_delete_warning(self):
        """Test soft deleting a warning."""
        warning = self.service.add_warning(
            guild_id="123456789012345678",
            user_id="987654321098765432",
            moderator_id="555666777888999000",
            reason="Test warning",
        )

        # Delete warning
        result = self.service.delete_warning(warning.id)
        assert result is True

        # Warning should be soft deleted
        db_warning = (
            self.service.db.query(SecureWarning)
            .filter(SecureWarning.id == warning.id)
            .first()
        )
        assert db_warning.is_deleted is True
        assert db_warning.deleted_at is not None

    def test_delete_nonexistent_warning(self):
        """Test deleting non-existent warning."""
        result = self.service.delete_warning(99999)
        assert result is False

    def test_get_user_warnings_exclude_deleted(self):
        """Test that deleted warnings are excluded by default."""
        guild_id = "123456789012345678"
        user_id = "987654321098765432"
        moderator_id = "555666777888999000"

        # Add warnings
        warning1 = self.service.add_warning(
            guild_id, user_id, moderator_id, "Active warning"
        )
        warning2 = self.service.add_warning(
            guild_id, user_id, moderator_id, "To be deleted"
        )

        # Delete one warning
        self.service.delete_warning(warning2.id)

        # Should only get active warnings
        warnings = self.service.get_user_warnings(guild_id, user_id)
        assert len(warnings) == 1
        assert warnings[0].id == warning1.id

        # Should get all warnings when including deleted
        all_warnings = self.service.get_user_warnings(
            guild_id, user_id, include_deleted=True
        )
        assert len(all_warnings) == 2

    def test_export_user_data(self):
        """Test GDPR data export."""
        guild_id = "123456789012345678"
        user_id = "987654321098765432"
        moderator_id = "555666777888999000"

        # Add some data
        warning = self.service.add_warning(
            guild_id, user_id, moderator_id, "Test warning"
        )

        # Export data
        export_data = self.service.export_user_data(user_id)

        assert "user_id_hash" in export_data
        assert "warnings" in export_data
        assert "moderation_logs" in export_data
        assert len(export_data["warnings"]) == 1
        assert export_data["warnings"][0]["reason"] == "Test warning"

    def test_delete_user_data(self):
        """Test GDPR data deletion."""
        guild_id = "123456789012345678"
        user_id = "987654321098765432"
        moderator_id = "555666777888999000"

        # Add some data
        warning1 = self.service.add_warning(
            guild_id, user_id, moderator_id, "Warning 1"
        )
        warning2 = self.service.add_warning(
            guild_id, user_id, moderator_id, "Warning 2"
        )

        # Delete user data
        result = self.service.delete_user_data(user_id)
        assert result is True

        # All warnings should be soft deleted
        warnings = self.service.get_user_warnings(guild_id, user_id)
        assert len(warnings) == 0  # No active warnings

        # But should exist when including deleted
        all_warnings = self.service.get_user_warnings(
            guild_id, user_id, include_deleted=True
        )
        assert len(all_warnings) == 2
        assert all(w.is_deleted for w in all_warnings)
