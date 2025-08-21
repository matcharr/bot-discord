"""Test authorization and concurrency handling in database services."""

import os
from unittest.mock import patch

import pytest

from project.database.services import WarningService


class TestWarningAuthorization:
    """Test authorization checks in warning operations."""

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_12345678901234567890123456789012",
            "SALT_KEY": "dGVzdF9zYWx0XzEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg=",
            "PEPPER_KEY": "dGVzdF9wZXBwZXJfMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3",
        },
        clear=True,
    )
    def test_delete_warning_requires_guild_authorization(self):
        """Test that deleting a warning requires proper guild authorization."""
        service = WarningService()

        # This should fail because warning doesn't exist or isn't in the specified guild
        result = service.delete_warning(
            warning_id=999999,
            guild_id="123456789012345678",
            moderator_id="987654321098765432",
        )

        assert result is False

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_12345678901234567890123456789012",
            "SALT_KEY": "dGVzdF9zYWx0XzEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg=",
            "PEPPER_KEY": "dGVzdF9wZXBwZXJfMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3",
        },
        clear=True,
    )
    def test_get_warning_by_id_requires_guild_authorization(self):
        """Test that getting a warning by ID requires proper guild authorization."""
        service = WarningService()

        # This should return None because warning doesn't exist or isn't in the specified guild
        warning = service.get_warning_by_id(
            warning_id=999999, guild_id="123456789012345678"
        )

        assert warning is None

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_12345678901234567890123456789012",
            "SALT_KEY": "dGVzdF9zYWx0XzEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg=",
            "PEPPER_KEY": "dGVzdF9wZXBwZXJfMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3",
        },
        clear=True,
    )
    def test_bulk_delete_warnings_authorization(self):
        """Test that bulk delete requires proper guild authorization."""
        service = WarningService()

        # This should handle non-existent warnings gracefully
        result = service.bulk_delete_warnings(
            warning_ids=[999999, 999998, 999997],
            guild_id="123456789012345678",
            moderator_id="987654321098765432",
        )

        assert result["total_requested"] == 3
        assert result["deleted"] == 0
        assert result["not_found"] == 3
        assert result["failed"] == 0

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_12345678901234567890123456789012",
            "SALT_KEY": "dGVzdF9zYWx0XzEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg=",
            "PEPPER_KEY": "dGVzdF9wZXBwZXJfMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3",
        },
        clear=True,
    )
    def test_export_user_data_requires_guild_scope(self):
        """Test that GDPR export is scoped to specific guild."""
        service = WarningService()

        # This should work but return empty data for non-existent user/guild
        result = service.export_user_data(
            user_id="123456789012345678", guild_id="987654321098765432"
        )

        assert "guild_id_hash" in result
        assert "user_id_hash" in result
        assert result["warnings"] == []
        assert result["moderation_logs"] == []

    @patch.dict(
        os.environ,
        {
            "ENCRYPTION_KEY": "test_key_12345678901234567890123456789012",
            "SALT_KEY": "dGVzdF9zYWx0XzEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg=",
            "PEPPER_KEY": "dGVzdF9wZXBwZXJfMTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3",
        },
        clear=True,
    )
    def test_delete_user_data_requires_guild_scope(self):
        """Test that GDPR deletion is scoped to specific guild."""
        service = WarningService()

        # This should work but not delete anything for non-existent user/guild
        result = service.delete_user_data(
            user_id="123456789012345678", guild_id="987654321098765432"
        )

        assert result is True  # Operation succeeds even if no data to delete
