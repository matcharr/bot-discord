"""Automated cleanup tasks for database maintenance."""

import logging
import os
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_

from .connection import get_db_session
from .models import ModerationLog, SecureWarning


logger = logging.getLogger(__name__)


class DatabaseCleanup:
    """Handles automated cleanup of old data."""

    def __init__(self):
        self.db = get_db_session()

    def hard_delete_old_soft_deleted(self, days_old: int = 90):
        """Permanently delete soft-deleted records older than X days.
        Default: 90 days (3 months) for GDPR compliance.

        Legal basis:
        - GDPR: "Without undue delay" = 30 days recommended
        - Grace period for appeals: +60 days
        - Total: 90 days is conservative and compliant
        """
        if days_old < 0:
            raise ValueError("days_old must be non-negative")
        cutoff_date = datetime.now(UTC) - timedelta(days=days_old)

        try:
            # Find old soft-deleted warnings
            old_warnings = (
                self.db.query(SecureWarning)
                .filter(
                    and_(
                        SecureWarning.is_deleted.is_(True),
                        SecureWarning.deleted_at < cutoff_date,
                    ),
                )
                .all()
            )

            count = len(old_warnings)

            if count > 0:
                # Hard delete them
                for warning in old_warnings:
                    self.db.delete(warning)

                self.db.commit()
                logger.info(
                    f"Hard deleted {count} old warnings (older than {days_old} days)",
                )
            else:
                logger.info("No old soft-deleted warnings to clean up")

            return count

        except Exception:
            self.db.rollback()
            logger.exception("Failed to cleanup old warnings")
            return 0

    def cleanup_old_logs(self, days_old: int = 730):
        """Clean up very old moderation logs (2 years default).
        Keep for longer than warnings for audit purposes.

        Legal basis:
        - Audit requirements: 2-7 years depending on jurisdiction
        - Discord ToS compliance: 2 years is standard
        - Anti-harassment evidence: 2 years reasonable
        """
        if days_old < 0:
            raise ValueError("days_old must be a positive integer")
        cutoff_date = datetime.now(UTC) - timedelta(days=days_old)

        try:
            deleted_count = (
                self.db.query(ModerationLog)
                .filter(ModerationLog.created_at < cutoff_date)
                .delete()
            )

            self.db.commit()
            logger.info(
                f"Deleted {deleted_count} old moderation logs (older than {days_old} days)",
            )
            return deleted_count

        except Exception:
            self.db.rollback()
            logger.exception("Failed to cleanup old logs")
            return 0

    def get_cleanup_stats(self) -> dict:
        """Get statistics about data that can be cleaned up."""
        try:
            now = datetime.now(UTC)

            # Count soft-deleted warnings by age
            soft_deleted_30d = (
                self.db.query(SecureWarning)
                .filter(
                    and_(
                        SecureWarning.is_deleted.is_(True),
                        SecureWarning.deleted_at < now - timedelta(days=30),
                    ),
                )
                .count()
            )

            soft_deleted_180d = (
                self.db.query(SecureWarning)
                .filter(
                    and_(
                        SecureWarning.is_deleted.is_(True),
                        SecureWarning.deleted_at < now - timedelta(days=180),
                    ),
                )
                .count()
            )

            # Count old logs
            old_logs_365d = (
                self.db.query(ModerationLog)
                .filter(ModerationLog.created_at < now - timedelta(days=365))
                .count()
            )

            return {
                "soft_deleted_warnings_30d": soft_deleted_30d,
                "soft_deleted_warnings_180d": soft_deleted_180d,
                "old_logs_365d": old_logs_365d,
                "cleanup_date": now.isoformat(),
            }

        except Exception:
            logger.exception("Failed to get cleanup stats")
            return {}

    def close(self):
        """Close database connection."""
        self.db.close()


# Convenience function
def run_cleanup(warning_days: int = 90, log_days: int = 730) -> dict:
    """Run automated cleanup and return statistics."""
    cleanup = DatabaseCleanup()
    try:
        stats_before = cleanup.get_cleanup_stats()

        warnings_deleted = cleanup.hard_delete_old_soft_deleted(warning_days)
        logs_deleted = cleanup.cleanup_old_logs(log_days)

        stats_after = cleanup.get_cleanup_stats()

        return {
            "warnings_hard_deleted": warnings_deleted,
            "logs_deleted": logs_deleted,
            "stats_before": stats_before,
            "stats_after": stats_after,
        }
    finally:
        cleanup.close()


class LegalCompliance:
    """Handles legal compliance and data retention policies."""

    # Legal retention periods (in days)
    GDPR_SOFT_DELETE_MAX = int(os.getenv("GDPR_SOFT_DELETE_MAX", 90))
    AUDIT_LOG_RETENTION = int(os.getenv("AUDIT_LOG_RETENTION", 730))
    SECURITY_LOG_RETENTION = int(os.getenv("SECURITY_LOG_RETENTION", 365))
    LEGAL_HOLD_MAX = int(os.getenv("LEGAL_HOLD_MAX", 2555))

    @staticmethod
    def get_retention_policy() -> dict:
        """Get the current data retention policy."""
        return {
            "user_warnings": {
                "soft_delete": "Immediate upon user request",
                "hard_delete": f"{LegalCompliance.GDPR_SOFT_DELETE_MAX} days after soft delete",
                "legal_basis": "GDPR Article 17 - Right to erasure",
            },
            "moderation_logs": {
                "retention": f"{LegalCompliance.AUDIT_LOG_RETENTION} days",
                "legal_basis": "Legitimate interest for platform safety",
            },
            "security_logs": {
                "retention": f"{LegalCompliance.SECURITY_LOG_RETENTION} days",
                "legal_basis": "Security and fraud prevention",
            },
            "legal_hold": {
                "max_retention": f"{LegalCompliance.LEGAL_HOLD_MAX} days",
                "legal_basis": "Legal proceedings and dispute resolution",
            },
        }

    @staticmethod
    def is_compliant_retention(days: int, data_type: str) -> bool:
        """Check if retention period is legally compliant."""
        limits = {
            "warnings": LegalCompliance.GDPR_SOFT_DELETE_MAX,
            "logs": LegalCompliance.AUDIT_LOG_RETENTION,
            "security": LegalCompliance.SECURITY_LOG_RETENTION,
        }
        return days <= limits.get(data_type, LegalCompliance.LEGAL_HOLD_MAX)
