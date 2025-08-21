"""Backup utilities for bot data."""

import logging
import shutil
from datetime import datetime
from pathlib import Path


logger = logging.getLogger(__name__)


class BackupManager:
    """Manages backups of bot data files."""

    def __init__(
        self,
        data_dir: Path = Path("data"),
        backup_dir: Path = Path("backups"),
    ):
        self.data_dir = data_dir
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, filename: str) -> Path | None:
        """Create a timestamped backup of a data file."""
        source_file = self.data_dir / filename

        if not source_file.exists():
            logger.warning(f"Source file {source_file} does not exist")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filename.stem}_{timestamp}{filename.suffix}"
        backup_path = self.backup_dir / backup_filename

        try:
            shutil.copy2(source_file, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception:
            logger.exception("Failed to create backup")
            return None

    def restore_backup(self, backup_filename: str, target_filename: str) -> bool:
        """Restore a backup file."""
        backup_path = self.backup_dir / backup_filename
        target_path = self.data_dir / target_filename

        if not backup_path.exists():
            logger.error(f"Backup file {backup_path} does not exist")
            return False

        try:
            shutil.copy2(backup_path, target_path)
            logger.info(f"Restored backup from {backup_path} to {target_path}")
            return True
        except Exception:
            logger.exception("Failed to restore backup")
            return False

    def list_backups(self, filename_pattern: str = "*") -> list:
        """List available backup files."""
        return list(self.backup_dir.glob(f"{filename_pattern}*"))

    def cleanup_old_backups(self, keep_count: int = 10):
        """Remove old backup files, keeping only the most recent ones."""
        backups = sorted(
            self.backup_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        for backup in backups[keep_count:]:
            try:
                backup.unlink()
                logger.info(f"Removed old backup: {backup}")
            except Exception:
                logger.exception(f"Failed to remove backup {backup}")


# Global backup manager instance
backup_manager = BackupManager()
