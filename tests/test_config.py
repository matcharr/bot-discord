import os
import pytest
from unittest.mock import patch
from project.config import BotConfig


class TestBotConfig:
    """Test bot configuration."""
    
    @patch.dict(os.environ, {
        'BOT_TOKEN': 'test_token',
        'REPORT_CHANNEL_ID': '123456789',
        'SPAM_THRESHOLD': '3',
        'LOG_LEVEL': 'DEBUG'
    })
    def test_config_from_env(self):
        """Test config creation from environment variables."""
        config = BotConfig.from_env()
        
        assert config.token == 'test_token'
        assert config.report_channel_id == 123456789
        assert config.spam_threshold == 3
        assert config.log_level == 'DEBUG'
        assert config.command_prefix == '!'  # default
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_required_env_vars(self):
        """Test error when required env vars are missing."""
        with pytest.raises(ValueError, match="BOT_TOKEN"):
            BotConfig.from_env()
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test'}, clear=True)
    def test_missing_channel_id(self):
        """Test error when channel ID is missing."""
        with pytest.raises(ValueError, match="REPORT_CHANNEL_ID"):
            BotConfig.from_env()