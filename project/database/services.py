"""Database services for warning and moderation management."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from .connection import get_db_session
from .models import GDPRRequest, ModerationLog, SecureWarning
from .security import security_manager

logger = logging.getLogger(__name__)


class WarningService:
    """Service for managing warnings with security and GDPR compliance."""

    def __init__(self):
        self.db = get_db_session()

    def add_warning(
        self, guild_id: str, user_id: str, moderator_id: str, reason: str
    ) -> SecureWarning:
        """Add a new warning to the database."""
        try:
            # Create warning
            warning = SecureWarning.create_warning(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                reason=reason,
            )

            # Save to database
            self.db.add(warning)
            self.db.commit()
            self.db.refresh(warning)

            # Create audit log
            log = ModerationLog.create_log(
                guild_id=guild_id,
                user_id=user_id,
                moderator_id=moderator_id,
                action_type="warn",
                reason=reason,
                warning_id=warning.id,
            )
            self.db.add(log)
            self.db.commit()

            logger.info(f"Warning {warning.id} added successfully")
            return warning

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to add warning: {e}")
            raise

    def get_user_warnings(
        self, guild_id: str, user_id: str, include_deleted: bool = False
    ) -> List[SecureWarning]:
        """Get all warnings for a user in a specific guild."""
        try:
            guild_hash = security_manager.hash_discord_id(guild_id)
            user_hash = security_manager.hash_discord_id(user_id)

            query = self.db.query(SecureWarning).filter(
                and_(
                    SecureWarning.guild_id_hash == guild_hash,
                    SecureWarning.user_id_hash == user_hash,
                )
            )

            if not include_deleted:
                query = query.filter(SecureWarning.is_deleted == False)

            warnings = query.order_by(desc(SecureWarning.created_at)).all()

            logger.info(
                f"Retrieved {len(warnings)} warnings for user "
                f"{security_manager.anonymize_for_logs(user_id)}"
            )
            return warnings

        except Exception as e:
            logger.error(f"Failed to get user warnings: {e}")
            raise

    def get_warning_count(self, guild_id: str, user_id: str) -> int:
        """Get the count of active warnings for a user."""
        try:
            guild_hash = security_manager.hash_discord_id(guild_id)
            user_hash = security_manager.hash_discord_id(user_id)

            count = (
                self.db.query(SecureWarning)
                .filter(
                    and_(
                        SecureWarning.guild_id_hash == guild_hash,
                        SecureWarning.user_id_hash == user_hash,
                        SecureWarning.is_deleted == False,
                    )
                )
                .count()
            )

            return count

        except Exception as e:
            logger.error(f"Failed to get warning count: {e}")
            return 0

    def delete_warning(self, warning_id: int) -> bool:
        """Soft delete a warning."""
        try:
            warning = (
                self.db.query(SecureWarning)
                .filter(SecureWarning.id == warning_id)
                .first()
            )

            if not warning:
                return False

            warning.soft_delete()
            self.db.commit()

            logger.info(f"Warning {warning_id} soft deleted")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete warning {warning_id}: {e}")
            return False

    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all data for a user (GDPR compliance)."""
        try:
            user_hash = security_manager.hash_discord_id(user_id)

            # Get all warnings
            warnings = (
                self.db.query(SecureWarning)
                .filter(SecureWarning.user_id_hash == user_hash)
                .all()
            )

            # Get all moderation logs
            logs = (
                self.db.query(ModerationLog)
                .filter(ModerationLog.user_id_hash == user_hash)
                .all()
            )

            export_data = {
                "user_id_hash": user_hash,
                "export_date": datetime.now(timezone.utc).isoformat(),
                "warnings": [w.to_dict() for w in warnings],
                "moderation_logs": [
                    {
                        "id": log.id,
                        "action_type": log.action_type,
                        "reason": log.get_decrypted_reason(),
                        "context": log.get_decrypted_context(),
                        "created_at": log.created_at.isoformat(),
                    }
                    for log in logs
                ],
            }

            # Create GDPR request record
            gdpr_request = GDPRRequest.create_request(user_id, "export")
            gdpr_request.status = "completed"
            gdpr_request.completed_at = datetime.now(timezone.utc)
            self.db.add(gdpr_request)
            self.db.commit()

            logger.info(
                f"Data exported for user {security_manager.anonymize_for_logs(user_id)}"
            )
            return export_data

        except Exception as e:
            logger.error(f"Failed to export user data: {e}")
            raise

    def delete_user_data(self, user_id: str) -> bool:
        """Delete all data for a user (GDPR right to be forgotten)."""
        try:
            user_hash = security_manager.hash_discord_id(user_id)

            # Soft delete all warnings
            warnings = (
                self.db.query(SecureWarning)
                .filter(SecureWarning.user_id_hash == user_hash)
                .all()
            )

            for warning in warnings:
                warning.soft_delete()

            # Note: We keep moderation logs for audit purposes but could anonymize them further

            # Create GDPR request record
            gdpr_request = GDPRRequest.create_request(user_id, "delete")
            gdpr_request.status = "completed"
            gdpr_request.completed_at = datetime.now(timezone.utc)
            self.db.add(gdpr_request)

            self.db.commit()

            logger.info(
                f"Data deleted for user {security_manager.anonymize_for_logs(user_id)}"
            )
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete user data: {e}")
            return False

    def close(self):
        """Close database connection."""
        self.db.close()


# Convenience function for getting a warning service
def get_warning_service() -> WarningService:
    """Get a new warning service instance."""
    return WarningService()
