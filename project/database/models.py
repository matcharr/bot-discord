"""Database models for secure Discord bot data storage."""

import logging
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship, validates

from .connection import Base
from .security import security_manager


logger = logging.getLogger(__name__)

# Constants for validation
ALLOWED_ACTION_TYPES = {
    "warn",
    "kick",
    "ban",
    "unban",
    "mute",
    "unmute",
    "timeout",
    "purge",
    "warning_deleted",
    "warning_edited",
}


class SecureWarning(Base):
    """Secure warning storage with encryption and hashing."""

    __tablename__ = "warnings"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Hashed identifiers for privacy (64 chars for SHA-256)
    guild_id_hash = Column(String(64), nullable=False, index=True)
    user_id_hash = Column(String(64), nullable=False, index=True)
    moderator_id_hash = Column(String(64), nullable=False, index=True)

    # Encrypted sensitive data
    reason_encrypted = Column(Text, nullable=False)

    # Lookup key for efficient queries (16 chars truncated)
    lookup_key = Column(String(16), nullable=False, index=True)

    # Metadata with timezone awareness
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Soft delete for GDPR compliance
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Data integrity
    version = Column(Integer, default=1, nullable=False)  # For optimistic locking

    # Composite indexes for performance
    __table_args__ = (
        Index("idx_guild_user_active", "guild_id_hash", "user_id_hash", "is_deleted"),
        Index("idx_lookup_active", "lookup_key", "is_deleted"),
        Index("idx_created_at", "created_at"),
    )

    @validates("reason_encrypted")
    def validate_reason_encrypted(self, _key, value):
        """Ensure reason is not empty after encryption."""
        if not value or len(value.strip()) == 0:
            raise ValueError("Encrypted reason cannot be empty")
        return value

    @classmethod
    def create_warning(
        cls,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        reason: str,
    ) -> "SecureWarning":
        """Create a new warning with automatic encryption and hashing."""
        if not reason or len(reason.strip()) == 0:
            raise ValueError("Warning reason cannot be empty")

        # Log anonymized action for audit
        logger.info(
            f"Creating warning for user {security_manager.anonymize_for_logs(user_id)} "
            f"in guild {security_manager.anonymize_for_logs(guild_id)}",
        )

        return cls(
            guild_id_hash=security_manager.hash_discord_id(guild_id),
            user_id_hash=security_manager.hash_discord_id(user_id),
            moderator_id_hash=security_manager.hash_discord_id(moderator_id),
            reason_encrypted=security_manager.encrypt_text(reason.strip()),
            lookup_key=security_manager.create_lookup_key(guild_id, user_id),
        )

    def get_decrypted_reason(self) -> str:
        """Get the decrypted warning reason."""
        try:
            return security_manager.decrypt_text(self.reason_encrypted)
        except ValueError:
            logger.exception(f"Failed to decrypt warning {self.id}")
            # Return safe default to avoid leaking encryption details
            return "[DECRYPTION_FAILED]"

    def soft_delete(self):
        """Soft delete this warning for GDPR compliance with optimistic locking."""
        if self.is_deleted:
            logger.warning(f"Warning {self.id} is already deleted")
            return

        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)
        self.version += 1  # Increment version for optimistic locking
        logger.info(f"Soft deleted warning {self.id} (version {self.version})")

    def to_dict(self, include_sensitive: bool = True) -> dict:
        """Convert to dictionary with optional sensitive data."""
        base_dict = {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "lookup_key": self.lookup_key,
            "is_deleted": self.is_deleted,
        }

        if include_sensitive and not self.is_deleted:
            base_dict["reason"] = self.get_decrypted_reason()

        return base_dict


class ModerationLog(Base):
    """Comprehensive audit log of all moderation actions."""

    __tablename__ = "moderation_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Hashed identifiers
    guild_id_hash = Column(String(64), nullable=False, index=True)
    user_id_hash = Column(String(64), nullable=False, index=True)
    moderator_id_hash = Column(String(64), nullable=False, index=True)

    # Action details
    action_type = Column(
        String(50),
        nullable=False,
        index=True,
    )  # warn, kick, ban, etc.
    reason_encrypted = Column(Text, nullable=True)

    # Optional reference to warning
    warning_id = Column(Integer, ForeignKey("warnings.id"), nullable=True)
    warning = relationship("SecureWarning", backref="logs")

    # Metadata
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Additional context (encrypted)
    context_encrypted = Column(Text, nullable=True)  # Additional details

    # Indexes
    __table_args__ = (
        Index("idx_guild_action_date", "guild_id_hash", "action_type", "created_at"),
        Index("idx_user_actions", "user_id_hash", "created_at"),
    )

    @validates("action_type")
    def validate_action_type(self, _key, value):
        """Validate action type is from allowed list."""
        if value not in ALLOWED_ACTION_TYPES:
            raise ValueError(
                f"Invalid action type: {value}. Must be one of {ALLOWED_ACTION_TYPES}",
            )
        return value

    @classmethod
    def create_log(
        cls,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        action_type: str,
        reason: str | None = None,
        context: str | None = None,
        warning_id: int | None = None,
    ) -> "ModerationLog":
        """Create a new moderation log entry."""
        # Log anonymized action
        logger.info(
            f"Logging {action_type} action by moderator "
            f"{security_manager.anonymize_for_logs(moderator_id)} "
            f"on user {security_manager.anonymize_for_logs(user_id)}",
        )

        return cls(
            guild_id_hash=security_manager.hash_discord_id(guild_id),
            user_id_hash=security_manager.hash_discord_id(user_id),
            moderator_id_hash=security_manager.hash_discord_id(moderator_id),
            action_type=action_type.lower(),
            reason_encrypted=security_manager.encrypt_text(reason) if reason else None,
            context_encrypted=(
                security_manager.encrypt_text(context) if context else None
            ),
            warning_id=warning_id,
        )

    def get_decrypted_reason(self) -> str:
        """Get the decrypted reason."""
        if not self.reason_encrypted:
            return ""
        try:
            return security_manager.decrypt_text(self.reason_encrypted)
        except ValueError:
            return "[DECRYPTION_FAILED]"

    def get_decrypted_context(self) -> str:
        """Get the decrypted context."""
        if not self.context_encrypted:
            return ""
        try:
            return security_manager.decrypt_text(self.context_encrypted)
        except ValueError:
            return "[DECRYPTION_FAILED]"


class GDPRRequest(Base):
    """Track GDPR data requests for compliance."""

    __tablename__ = "gdpr_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id_hash = Column(String(64), nullable=False, index=True)
    request_type = Column(String(20), nullable=False)  # 'export', 'delete'
    status = Column(
        String(20),
        default="pending",
        nullable=False,
    )  # 'pending', 'completed', 'failed'

    @validates("request_type")
    def validate_request_type(self, _key, value):
        """Validate request type is from allowed list."""
        allowed_types = {"export", "delete"}
        if value not in allowed_types:
            raise ValueError(
                f"Invalid request type: {value}. Must be one of {allowed_types}",
            )
        return value

    @validates("status")
    def validate_status(self, _key, value):
        """Validate status is from allowed list."""
        allowed_statuses = {"pending", "completed", "failed"}
        if value not in allowed_statuses:
            raise ValueError(
                f"Invalid status: {value}. Must be one of {allowed_statuses}",
            )
        return value

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    @classmethod
    def create_request(cls, user_id: str, request_type: str) -> "GDPRRequest":
        """Create a new GDPR request."""
        return cls(
            user_id_hash=security_manager.hash_discord_id(user_id),
            request_type=request_type,
        )
