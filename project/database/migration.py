"""Migration script to move from JSON warnings to secure database."""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

from .connection import init_database
from .models import SecureWarning
from .services import get_warning_service

logger = logging.getLogger(__name__)


class WarningMigration:
    """Handles migration from JSON warnings to secure database."""

    def __init__(self):
        self.data_dir = Path(os.getenv("DATA_DIR", "data"))
        self.warnings_file = self.data_dir / "warnings.json"
        self.backup_file = (
            self.data_dir
            / f"warnings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    def load_json_warnings(self) -> dict:
        """Load existing JSON warnings."""
        try:
            if self.warnings_file.exists():
                with self.warnings_file.open(encoding="utf-8") as file:
                    data = json.load(file)
                    if isinstance(data, dict):
                        return data
            return {}
        except Exception:
            logger.exception("Failed to load JSON warnings")
            return {}

    def backup_json_warnings(self) -> bool:
        """Create backup of JSON warnings before migration."""
        try:
            if self.warnings_file.exists():
                shutil.copy2(self.warnings_file, self.backup_file)
                logger.info(f"Backup created: {self.backup_file}")
                return True
            return False
        except Exception:
            logger.exception("Failed to create backup")
            return False

    def migrate_warnings(
        self,
        guild_id: str,
        moderator_id: str = "000000000000000000",
    ) -> dict:
        """Migrate JSON warnings to secure database.

        Args:
            guild_id: Discord guild ID for the warnings
            moderator_id: Default moderator ID for migrated warnings

        Returns:
            Migration statistics
        """
        stats = {
            "total_users": 0,
            "total_warnings": 0,
            "migrated_warnings": 0,
            "failed_warnings": 0,
            "errors": [],
        }

        try:
            # Initialize database
            init_database()

            # Load JSON data
            json_warnings = self.load_json_warnings()
            if not json_warnings:
                logger.info("No JSON warnings found to migrate")
                return stats

            # Create backup
            self.backup_json_warnings()

            # Migrate data
            try:
                service = get_warning_service()
                for user_id, warnings_list in json_warnings.items():
                    stats["total_users"] += 1

                    if not isinstance(warnings_list, list):
                        continue

                    for warning_reason in warnings_list:
                        stats["total_warnings"] += 1

                        try:
                            # Create warning in secure database
                            warning = service.add_warning(
                                guild_id=guild_id,
                                user_id=user_id,
                                moderator_id=moderator_id,
                                reason=warning_reason
                                or "Migrated warning - no reason provided",
                            )

                            stats["migrated_warnings"] += 1
                            logger.debug(
                                f"Migrated warning {warning.id} for user {user_id}",
                            )

                        except Exception as e:
                            stats["failed_warnings"] += 1
                            error_msg = (
                                f"Failed to migrate warning for user {user_id}: {e}"
                            )
                            stats["errors"].append(error_msg)
                            logger.exception(error_msg)

                logger.info(
                    f"Migration completed: {stats['migrated_warnings']}/{stats['total_warnings']} warnings migrated",
                )

            finally:
                service.close()

        except Exception as e:
            error_msg = f"Migration failed: {e}"
            stats["errors"].append(error_msg)
            logger.exception(error_msg)

        return stats

    def verify_migration(self, guild_id: str) -> dict:
        """Verify that migration was successful."""
        verification = {"database_warnings": 0, "json_warnings": 0, "match": False}

        try:
            # Count JSON warnings
            json_warnings = self.load_json_warnings()
            json_count = sum(
                len(warnings)
                for warnings in json_warnings.values()
                if isinstance(warnings, list)
            )
            verification["json_warnings"] = json_count

            # Count database warnings
            service = get_warning_service()
            try:
                # This is a simplified count - in reality you'd need to query by guild
                # For now, we'll just check if we have any warnings
                db_count = (
                    service.db.query(SecureWarning)
                    .filter(
                        SecureWarning.guild_id_hash
                        == service.security.hash_guild_id(guild_id),
                        SecureWarning.is_deleted.is_(False),
                    )
                    .count()
                )
                verification["database_warnings"] = db_count

            finally:
                service.close()

            verification["match"] = (
                verification["database_warnings"] >= verification["json_warnings"]
            )

        except Exception:
            logger.exception("Verification failed")

        return verification


def run_migration(guild_id: str, moderator_id: str = "000000000000000000") -> dict:
    """Run the complete migration process.

    Args:
        guild_id: Discord guild ID
        moderator_id: Default moderator ID for migrated warnings

    Returns:
        Migration results
    """
    migration = WarningMigration()

    print("🔄 Starting warning migration...")
    print(f"Guild ID: {guild_id}")
    print(f"Default Moderator ID: {moderator_id}")

    # Run migration
    stats = migration.migrate_warnings(guild_id, moderator_id)

    # Print results
    print("\n📊 Migration Results:")
    print(f"  Users processed: {stats['total_users']}")
    print(f"  Total warnings: {stats['total_warnings']}")
    print(f"  Successfully migrated: {stats['migrated_warnings']}")
    print(f"  Failed: {stats['failed_warnings']}")

    if stats["errors"]:
        print(f"\n❌ Errors ({len(stats['errors'])}):")
        errors_to_show = min(5, len(stats["errors"]))
        for error in stats["errors"][:errors_to_show]:
            print(f"  - {error}")
        remaining = len(stats["errors"]) - errors_to_show
        if remaining > 0:
            print(f"  ... and {remaining} more errors")

    # Verify migration
    print("\n🔍 Verifying migration...")
    verification = migration.verify_migration(guild_id)
    print(f"  JSON warnings: {verification['json_warnings']}")
    print(f"  Database warnings: {verification['database_warnings']}")
    print(f"  Migration successful: {'✅' if verification['match'] else '❌'}")

    return {**stats, "verification": verification}


if __name__ == "__main__":
    # Example usage
    guild_id = input("Enter your Discord Guild ID: ").strip()
    moderator_id = input(
        "Enter default moderator ID (or press Enter for system): ",
    ).strip()

    if not moderator_id:
        moderator_id = "000000000000000000"  # System user

    results = run_migration(guild_id, moderator_id)
    print("\n🎉 Migration completed!")
