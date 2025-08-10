"""Database models for secure Discord bot data storage."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from .connection import Base
from .security import security_manager


class SecureWarning(Base):
    """Secure warning storage with encryption and hashing."""
    
    __tablename__ = "warnings"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Hashed identifiers for privacy
    guild_id_hash = Column(String(64), nullable=False, index=True)
    user_id_hash = Column(String(64), nullable=False, index=True)
    moderator_id_hash = Column(String(64), nullable=False)
    
    # Encrypted sensitive data
    reason_encrypted = Column(Text, nullable=False)
    
    # Lookup key for efficient queries
    lookup_key = Column(String(16), nullable=False, unique=True, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_guild_user', 'guild_id_hash', 'user_id_hash'),
    )
    
    @classmethod
    def create_warning(
        cls,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        reason: str
    ) -> "SecureWarning":
        """Create a new warning with automatic encryption and hashing."""
        return cls(
            guild_id_hash=security_manager.hash_discord_id(guild_id),
            user_id_hash=security_manager.hash_discord_id(user_id),
            moderator_id_hash=security_manager.hash_discord_id(moderator_id),
            reason_encrypted=security_manager.encrypt_text(reason),
            lookup_key=security_manager.create_lookup_key(guild_id, user_id)
        )
    
    def get_decrypted_reason(self) -> str:
        """Get the decrypted warning reason."""
        return security_manager.decrypt_text(self.reason_encrypted)
    
    def to_dict(self) -> dict:
        """Convert to dictionary with decrypted data."""
        return {
            "id": self.id,
            "reason": self.get_decrypted_reason(),
            "created_at": self.created_at.isoformat(),
            "lookup_key": self.lookup_key
        }


class ModerationLog(Base):
    """Log of all moderation actions for audit trail."""
    
    __tablename__ = "moderation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    guild_id_hash = Column(String(64), nullable=False, index=True)
    user_id_hash = Column(String(64), nullable=False, index=True)
    moderator_id_hash = Column(String(64), nullable=False)
    
    action_type = Column(String(50), nullable=False)  # warn, kick, ban, etc.
    reason_encrypted = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    @classmethod
    def create_log(
        cls,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        action_type: str,
        reason: str = None
    ) -> "ModerationLog":
        """Create a new moderation log entry."""
        return cls(
            guild_id_hash=security_manager.hash_discord_id(guild_id),
            user_id_hash=security_manager.hash_discord_id(user_id),
            moderator_id_hash=security_manager.hash_discord_id(moderator_id),
            action_type=action_type,
            reason_encrypted=security_manager.encrypt_text(reason) if reason else None
        )