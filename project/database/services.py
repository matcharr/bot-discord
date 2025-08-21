"""Database services for warning and moderation management."""

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import and_, desc
from sqlalchemy.exc import SQLAlchemyError

from .connection import get_db_session
from .models import GDPRRequest, ModerationLog, SecureWarning
from .security import security_manager

logger = logging.getLogger(__name__)


class WarningService:
    """Service for managing warnings with security and GDPR compliance."""

    def add_warning(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        reason: str,
    ) -> SecureWarning:
        """Add a new warning to the database."""
        with get_db_session() as db:
            try:
                # Create warning
                warning = SecureWarning.create_warning(
                    guild_id=guild_id,
                    user_id=user_id,
                    moderator_id=moderator_id,
                    reason=reason,
                )

                # Save to database
                db.add(warning)
                db.commit()
                db.refresh(warning)

                # Create audit log
                log = ModerationLog.create_log(
                    guild_id=guild_id,
                    user_id=user_id,
                    moderator_id=moderator_id,
                    action_type="warn",
                    reason=reason,
                    warning_id=warning.id,
                )
                db.add(log)
                db.commit()

                logger.info(f"Warning {warning.id} added successfully")
                return warning

            except Exception:
                db.rollback()
                logger.exception("Failed to add warning")
                raise

    def get_user_warnings(
        self,
        guild_id: str,
        user_id: str,
        include_deleted: bool = False,
    ) -> list[SecureWarning]:
        """Get all warnings for a user in a specific guild."""
        with get_db_session() as db:
            try:
                guild_hash = security_manager.hash_discord_id(guild_id)
                user_hash = security_manager.hash_discord_id(user_id)

                query = db.query(SecureWarning).filter(
                    and_(
                        SecureWarning.guild_id_hash == guild_hash,
                        SecureWarning.user_id_hash == user_hash,
                    ),
                )

                if not include_deleted:
                    query = query.filter(SecureWarning.is_deleted is False)

                warnings = query.order_by(desc(SecureWarning.created_at)).all()

                logger.info(
                    f"Retrieved {len(warnings)} warnings for user "
                    f"{security_manager.anonymize_for_logs(user_id)}",
                )
                return warnings

            except Exception:
                logger.exception("Failed to get user warnings")
                raise

    def get_warning_count(self, guild_id: str, user_id: str) -> int:
        """Get the count of active warnings for a user."""
        with get_db_session() as db:
            try:
                guild_hash = security_manager.hash_discord_id(guild_id)
                user_hash = security_manager.hash_discord_id(user_id)

                return (
                    db.query(SecureWarning)
                    .filter(
                        and_(
                            SecureWarning.guild_id_hash == guild_hash,
                            SecureWarning.user_id_hash == user_hash,
                            SecureWarning.is_deleted is False,
                        ),
                    )
                    .count()
                )
            except Exception:
                logger.exception("Failed to get warning count")
                raise

    def delete_warning(self, warning_id: int, guild_id: str, moderator_id: str) -> bool:
        """Soft delete a warning with proper authorization checks.

        Args:
            warning_id: ID of the warning to delete
            guild_id: Guild ID to verify the warning belongs to this guild
            moderator_id: ID of the moderator performing the deletion

        Returns:
            True if warning was deleted, False if not found or unauthorized
        """
        with get_db_session() as db:
            try:
                guild_hash = security_manager.hash_discord_id(guild_id)

                # Get warning with guild verification and optimistic locking
                warning = (
                    db.query(SecureWarning)
                    .filter(
                        and_(
                            SecureWarning.id == warning_id,
                            SecureWarning.guild_id_hash == guild_hash,
                            SecureWarning.is_deleted is False,
                        ),
                    )
                    .with_for_update()  # Optimistic locking
                    .first()
                )

                if not warning:
                    logger.warning(
                        f"Warning {warning_id} not found or not authorized for guild "
                        f"{security_manager.anonymize_for_logs(guild_id)}",
                    )
                    return False

                # Store original version for optimistic locking check
                original_version = warning.version

                # Soft delete the warning
                warning.soft_delete()

                # Create audit log for deletion
                log = ModerationLog.create_log(
                    guild_id=guild_id,
                    user_id="unknown",  # We don't have user_id from warning directly
                    moderator_id=moderator_id,
                    action_type="warning_deleted",
                    reason=f"Warning {warning_id} deleted",
                    context=f"Original warning ID: {warning_id}, version: {original_version}",
                    warning_id=warning_id,
                )
                db.add(log)
                db.commit()

                logger.info(
                    f"Warning {warning_id} deleted by moderator "
                    f"{security_manager.anonymize_for_logs(moderator_id)} "
                    f"in guild {security_manager.anonymize_for_logs(guild_id)}",
                )
                return True

            except SQLAlchemyError as e:
                db.rollback()
                # Check if it's a concurrency issue
                if "version" in str(e).lower() or "concurrent" in str(e).lower():
                    logger.warning(
                        f"Warning {warning_id} was modified by another process - "
                        "concurrent modification detected",
                    )
                else:
                    logger.exception(
                        f"Database error while deleting warning {warning_id}",
                    )
                return False
            except Exception:
                db.rollback()
                logger.exception(f"Failed to delete warning {warning_id}")
                return False

    def get_warning_by_id(self, warning_id: int, guild_id: str) -> SecureWarning | None:
        """Get a specific warning by ID with guild authorization.

        Args:
            warning_id: ID of the warning
            guild_id: Guild ID to verify authorization

        Returns:
            Warning if found and authorized, None otherwise
        """
        with get_db_session() as db:
            try:
                guild_hash = security_manager.hash_discord_id(guild_id)

                warning = (
                    db.query(SecureWarning)
                    .filter(
                        and_(
                            SecureWarning.id == warning_id,
                            SecureWarning.guild_id_hash == guild_hash,
                            SecureWarning.is_deleted is False,
                        ),
                    )
                    .first()
                )

                if warning:
                    logger.debug(f"Retrieved warning {warning_id}")
                else:
                    logger.warning(
                        f"Warning {warning_id} not found or not authorized for guild "
                        f"{security_manager.anonymize_for_logs(guild_id)}",
                    )

                return warning

            except Exception:
                logger.exception(f"Failed to get warning {warning_id}")
                return None

    def bulk_delete_warnings(
        self,
        warning_ids: list[int],
        guild_id: str,
        moderator_id: str,
    ) -> dict[str, Any]:
        """Bulk delete multiple warnings with proper authorization and concurrency handling.

        Args:
            warning_ids: List of warning IDs to delete
            guild_id: Guild ID to verify authorization
            moderator_id: ID of the moderator performing the deletion

        Returns:
            Dictionary with success/failure counts and details
        """
        with get_db_session() as db:
            results = {
                "total_requested": len(warning_ids),
                "deleted": 0,
                "failed": 0,
                "not_found": 0,
                "errors": [],
            }

            try:
                guild_hash = security_manager.hash_discord_id(guild_id)

                # Get all warnings that exist and belong to this guild
                warnings = (
                    db.query(SecureWarning)
                    .filter(
                        and_(
                            SecureWarning.id.in_(warning_ids),
                            SecureWarning.guild_id_hash == guild_hash,
                            SecureWarning.is_deleted is False,
                        ),
                    )
                    .with_for_update()  # Lock all warnings for update
                    .all()
                )

                found_ids = {w.id for w in warnings}
                results["not_found"] = len(warning_ids) - len(found_ids)

                # Delete each warning
                for warning in warnings:
                    try:
                        original_version = warning.version
                        warning.soft_delete()

                        # Create audit log
                        log = ModerationLog.create_log(
                            guild_id=guild_id,
                            user_id="unknown",
                            moderator_id=moderator_id,
                            action_type="warning_deleted",
                            reason=f"Bulk deletion of warning {warning.id}",
                            context=f"Bulk operation, original version: {original_version}",
                            warning_id=warning.id,
                        )
                        db.add(log)
                        results["deleted"] += 1

                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Warning {warning.id}: {e!s}")
                        logger.exception(
                            f"Failed to delete warning {warning.id} in bulk operation",
                        )

                db.commit()

                logger.info(
                    f"Bulk deletion completed by moderator "
                    f"{security_manager.anonymize_for_logs(moderator_id)} "
                    f"in guild {security_manager.anonymize_for_logs(guild_id)}: "
                    f"{results['deleted']} deleted, {results['failed']} failed, "
                    f"{results['not_found']} not found",
                )

                return results

            except Exception as e:
                db.rollback()
                logger.exception("Bulk delete operation failed")
                results["errors"].append(f"Bulk operation failed: {e!s}")
                return results

    def export_user_data(self, user_id: str, guild_id: str) -> dict[str, Any]:
        """Export all data for a user in a specific guild (GDPR compliance).

        Args:
            user_id: Discord user ID
            guild_id: Guild ID to limit export scope

        Returns:
            Dictionary containing user's data for the specified guild
        """
        with get_db_session() as db:
            try:
                user_hash = security_manager.hash_discord_id(user_id)
                guild_hash = security_manager.hash_discord_id(guild_id)

                # Get warnings for this guild only
                warnings = (
                    db.query(SecureWarning)
                    .filter(
                        and_(
                            SecureWarning.user_id_hash == user_hash,
                            SecureWarning.guild_id_hash == guild_hash,
                        ),
                    )
                    .all()
                )

                # Get moderation logs for this guild only
                logs = (
                    db.query(ModerationLog)
                    .filter(
                        and_(
                            ModerationLog.user_id_hash == user_hash,
                            ModerationLog.guild_id_hash == guild_hash,
                        ),
                    )
                    .all()
                )

                export_data = {
                    "user_id_hash": user_hash,
                    "guild_id_hash": guild_hash,
                    "export_date": datetime.now(UTC).isoformat(),
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
                gdpr_request.completed_at = datetime.now(UTC)
                db.add(gdpr_request)
                db.commit()

                logger.info(
                    f"Data exported for user {security_manager.anonymize_for_logs(user_id)} "
                    f"in guild {security_manager.anonymize_for_logs(guild_id)}",
                )
                return export_data

            except Exception:
                logger.exception("Failed to export user data")
                raise

    def delete_user_data(self, user_id: str, guild_id: str) -> bool:
        """Delete all data for a user in a specific guild (GDPR right to be forgotten).

        Args:
            user_id: Discord user ID
            guild_id: Guild ID to limit deletion scope

        Returns:
            True if data was deleted successfully, False otherwise
        """
        with get_db_session() as db:
            try:
                user_hash = security_manager.hash_discord_id(user_id)
                guild_hash = security_manager.hash_discord_id(guild_id)

                # Soft delete warnings for this guild only
                warnings = (
                    db.query(SecureWarning)
                    .filter(
                        and_(
                            SecureWarning.user_id_hash == user_hash,
                            SecureWarning.guild_id_hash == guild_hash,
                            SecureWarning.is_deleted is False,
                        ),
                    )
                    .with_for_update()  # Prevent concurrent modifications
                    .all()
                )

                deleted_count = 0
                for warning in warnings:
                    warning.soft_delete()
                    deleted_count += 1

                # Note: We keep moderation logs for audit purposes but could anonymize them further
                # In a real implementation, you might want to anonymize rather than delete logs

                # Create GDPR request record
                gdpr_request = GDPRRequest.create_request(user_id, "delete")
                gdpr_request.status = "completed"
                gdpr_request.completed_at = datetime.now(UTC)
                db.add(gdpr_request)

                db.commit()

                logger.info(
                    f"Data deleted for user {security_manager.anonymize_for_logs(user_id)} "
                    f"in guild {security_manager.anonymize_for_logs(guild_id)} "
                    f"({deleted_count} warnings deleted)",
                )
                return True

            except Exception:
                db.rollback()
                logger.exception("Failed to delete user data")
                return False


# Convenience function for getting a warning service
def get_warning_service() -> WarningService:
    """Get a new warning service instance."""
    return WarningService()
