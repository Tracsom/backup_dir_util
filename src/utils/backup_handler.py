import os
import shutil
import zipfile
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger('backup_app')

def validate_destination_path(path:str)->bool:
    try:
        test_file = os.path.join(path, f"__test_{os.getpid()}.tmp")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except Exception as e:
        logger.warning(f"[validate_destination_path] Failed to write test file: {e}")
        return False

def perform_backup(src, dest, compress=False, log_callback=None):
    log = _build_logger_proxy(log_callback)
    folder_name = os.path.basename(os.path.normpath(src))
    timestamp = datetime.now().strftime("%Y-%m-%d")
    target_path = os.path.join(dest, folder_name)
    # Handle backup if compression is active
    if compress:
        zip_name = f"{folder_name}_{timestamp}.zip"
        zip_path = os.path.join(dest, zip_name)
        log(f"Creating ZIP archive: {zip_path}")
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(src):
                    for file in files:
                        abs_path = os.path.join(root, file)
                        arcname = os.path.relpath(abs_path, src)
                        zipf.write(abs_path, arcname)
                        log(f"Added {arcname}")
            return
        except Exception as e:
            log(f"ZIP backup failed: {e}", level="error")
            raise
    # Move existing folder to backups if it exists
    if os.path.exists(target_path):
        backups_dir = os.path.join(dest, "backups")
        os.makedirs(backups_dir, exist_ok=True)
        archived_name = f"{folder_name}_{timestamp}"
        archived_path = os.path.join(backups_dir, archived_name)
        if os.path.exists(archived_path):
            log(f"An archived backup for today already exists: {archived_path}. Skipping backup")
            return
        log(f"Archiving existing backup to: {archived_path}")
        try:
            shutil.move(target_path, archived_path)
        except Exception as e:
            log(f"Failed to archive old backup: {e}", level="error")
            raise
    # Copy new folder
    log(f"Copying new backup to: {target_path}")
    try:
        shutil.copytree(src, target_path)
    except Exception as e:
        log(f"Backup failed: {e}", level="error")
        raise
    else:
        log(f"Copy complete.")

def _build_logger_proxy(log_callback):
    """
    Returns a logging proxy function that routes messages to both
    the file logger and optional GUI callback.
    """
    def log(msg, level="info"):
        getattr(logger, level)(msg)
        if log_callback:
            log_callback(msg)
        return log