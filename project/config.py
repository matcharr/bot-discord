import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    """Bot configuration from environment variables."""

    # Required
    token: str
    report_channel_id: int

    # Optional with defaults
    command_prefix: str = "!"
    case_insensitive: bool = True

    # Anti-raid settings
    spam_threshold: int = 5
    kick_threshold: int = 10
    cooldown_seconds: int = 10

    # Logging
    log_level: str = "INFO"

    # Moderation settings
    max_warnings_before_action: int = 5
    enable_audit_logging: bool = True

    @classmethod
    def from_env(cls) -> "BotConfig":
        """Create config from environment variables."""
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("BOT_TOKEN environment variable is required")

        report_channel_id = os.getenv("REPORT_CHANNEL_ID")
        if not report_channel_id:
            raise ValueError("REPORT_CHANNEL_ID environment variable is required")

        return cls(
            token=token,
            report_channel_id=int(report_channel_id),
            command_prefix=os.getenv("COMMAND_PREFIX", "!"),
            case_insensitive=os.getenv("CASE_INSENSITIVE", "true").lower() == "true",
            spam_threshold=int(os.getenv("SPAM_THRESHOLD", "5")),
            kick_threshold=int(os.getenv("KICK_THRESHOLD", "10")),
            cooldown_seconds=int(os.getenv("COOLDOWN_SECONDS", "10")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            max_warnings_before_action=int(
                os.getenv("MAX_WARNINGS_BEFORE_ACTION", "5")
            ),
            enable_audit_logging=os.getenv("ENABLE_AUDIT_LOGGING", "true").lower()
            == "true",
        )


# Global config instance - lazy loaded
_config = None


def get_config() -> BotConfig:
    """Get the global config instance, creating it if needed."""
    global _config
    if _config is None:
        _config = BotConfig.from_env()
    return _config
