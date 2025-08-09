"""Tests for moderation cog."""

import pytest
from unittest.mock import patch, MagicMock

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
        assert Moderation.parse_time("5") is None     # No unit
        assert Moderation.parse_time("5x") is None    # Invalid unit
    
    def test_parse_time_edge_cases(self):
        """Test parse_time edge cases."""
        assert Moderation.parse_time("10080m") == 604800  # 1 week in minutes
        assert Moderation.parse_time("10081m") is None    # Over 1 week
        assert Moderation.parse_time("168h") == 604800    # 1 week in hours
        assert Moderation.parse_time("169h") is None      # Over 1 week
        assert Moderation.parse_time("30d") == 2592000    # 30 days
        assert Moderation.parse_time("31d") is None       # Over 30 days
    
    @patch('cogs.moderation.Path')
    @patch('cogs.moderation.config')
    def test_load_warnings_file_not_exists(self, mock_config, mock_path):
        """Test loading warnings when file doesn't exist."""
        mock_bot = MagicMock()
        mock_config.max_warnings_before_action = 5
        mock_path.return_value.mkdir.return_value = None
        mock_path.return_value.exists.return_value = False
        
        with patch('cogs.moderation.validate_hierarchy'), \
             patch('cogs.moderation.log_moderation_action'):
            mod = Moderation(mock_bot)
            assert mod.warnings == {}
    
    @patch('cogs.moderation.config')
    def test_save_warnings_success(self, mock_config):
        """Test successful warnings save."""
        mock_bot = MagicMock()
        mock_config.max_warnings_before_action = 5
        
        with patch('cogs.moderation.Path') as mock_path, \
             patch('builtins.open', create=True) as mock_open, \
             patch('json.dump') as mock_json_dump, \
             patch('json.load') as mock_json_load, \
             patch('cogs.moderation.validate_hierarchy'), \
             patch('cogs.moderation.log_moderation_action'):
            
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = False
            mock_json_load.return_value = {}  # Return empty dict for warnings
            
            mod = Moderation(mock_bot)
            result = mod._save_warnings()
            
            assert result is True
    
    @patch('cogs.moderation.config')
    def test_load_warnings_file_exists(self, mock_config):
        """Test loading warnings when file exists with valid data."""
        mock_bot = MagicMock()
        mock_config.max_warnings_before_action = 5
        
        test_warnings = {"123": ["reason1", "reason2"]}
        
        with patch('cogs.moderation.Path') as mock_path, \
             patch('builtins.open', create=True) as mock_open, \
             patch('json.load') as mock_json_load, \
             patch('cogs.moderation.validate_hierarchy'), \
             patch('cogs.moderation.log_moderation_action'):
            
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.exists.return_value = True
            mock_json_load.return_value = test_warnings
            
            mod = Moderation(mock_bot)
            assert mod.warnings == test_warnings