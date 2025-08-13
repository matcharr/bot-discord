"""Tests for moderation cog."""

from unittest.mock import MagicMock, patch

import pytest

from cogs.moderation import Moderation


class TestModeration:
    """Test moderation functionality."""

    def test_parse_time_valid_inputs(self):
        """Test parse_time with valid inputs."""
        assert Moderation.parse_time("5m") == 300
        assert Moderation.parse_time("2h") == 7200
        assert Moderation.parse_time("1d") == 86400

    def test_parse_time_invalid_inputs(self):
        """Test parse_time with invalid inputs."""
        assert Moderation.parse_time("") is None
        assert Moderation.parse_time("invalid") is None
        assert Moderation.parse_time("0m") is None
        assert Moderation.parse_time("-5m") is None
        assert Moderation.parse_time("999d") is None  # Too long
        assert Moderation.parse_time(None) is None
        assert Moderation.parse_time("5") is None  # No unit
        assert Moderation.parse_time("5x") is None  # Invalid unit

    def test_parse_time_edge_cases(self):
        """Test parse_time edge cases."""
        assert Moderation.parse_time("10080m") == 604800  # 1 week in minutes
        assert Moderation.parse_time("10081m") is None  # Over 1 week
        assert Moderation.parse_time("168h") == 604800  # 1 week in hours
        assert Moderation.parse_time("169h") is None  # Over 1 week
        assert Moderation.parse_time("30d") == 2592000  # 30 days
        assert Moderation.parse_time("31d") is None  # Over 30 days

    @patch("cogs.moderation.init_database")
    @patch("cogs.moderation.get_config")
    def test_moderation_cog_initialization(self, mock_get_config, mock_init_db):
        """Test moderation cog initializes with database."""
        mock_bot = MagicMock()
        mock_get_config.return_value.max_warnings_before_action = 5
        mock_init_db.return_value = None

        mod = Moderation(mock_bot)
        assert mod.bot == mock_bot
        mock_init_db.assert_called_once()

    @patch("cogs.moderation.init_database")
    @patch("cogs.moderation.get_config")
    def test_database_service_integration(self, mock_get_config, mock_init_db):
        """Test that moderation cog integrates with database service."""
        mock_bot = MagicMock()
        mock_get_config.return_value.max_warnings_before_action = 5

        mod = Moderation(mock_bot)

        # Verify database initialization is called during setup
        mock_init_db.assert_called_once()
        # Verify bot is properly set
        assert mod.bot == mock_bot

    @patch("cogs.moderation.init_database")
    @patch("cogs.moderation.get_config")
    def test_database_initialization_failure(self, mock_get_config, mock_init_db):
        """Test moderation cog handles database initialization failure."""
        mock_bot = MagicMock()
        mock_get_config.return_value.max_warnings_before_action = 5
        mock_init_db.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception, match="Database connection failed"):
            Moderation(mock_bot)
