import os
import shutil
import zipfile
from datetime import datetime
from src.utils.logger import setup_logger

class BackupJob:
    def __init__(self, src, dest, compress=False, log_callback=None):
        self.logger = setup_logger("backup_app")
        self.src = src
        self.dest = dest
        self.compress = compress
        self.timestamp = datetime.now().strftime("%Y-%m-%d")
        self.log = self._build_logger_proxy(log_callback)

    # --- Magic Methods ---
    def __str__(self):
        return f"BackupJob: {self.src} -> {self.dest} (compress={self.compress})"
    
    def __repr__(self):
        return f"BackupJob(src='{self.src}', dest='{self.dest}', compress={self.compress})"

    # --- Properties with validation ---
    @property
    def src(self):
        return self._src
    
    @src.setter
    def src(self, value):
        if not os.path.isdir(value):
            raise ValueError(f"Source path is not a valid directory: {value}")
        self._src = os.path.abspath(value)

    @property
    def dest(self):
        return self._dest
    
    @dest.setter
    def dest(self, value):
        if not os.path.isdir(value):
            raise ValueError(f"Destination path is not a valid directory: {value}")
        test_file = os.path.join(value, f"__test_{os.getpid()}.tmp")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            raise PermissionError(f"Destination path not writeable: {value}. Error: {e}")
        self._dest = os.path.abspath(value)

    # --- Public method ---
    def run(self, progress_callback=None):
        try:
            if self.compress:
                self._zip_backup(progress_callback)
            else:
                self._full_backup(progress_callback)
            return True
        except Exception as e:
            self.log(f"Backup failed: {e}", level="error")
            raise

    # --- Internal methods ---
    def _zip_backup(self, progress_callback=None):
        folder_name = os.path.basename(os.path.normpath(self.src))
        zip_name = f"{folder_name}_{self.timestamp}.zip"
        zip_path = os.path.join(self.dest, zip_name)
        if os.path.exists(zip_path):
            self.log(f"ZIP archive already exists: {zip_path}. Skipping backup.")
            return
        total_files = sum(len(files) for _, _, files in os.walk(self.src))
        processed = 0
        self.log(f"Creating ZIP archive: {zip_path}")
        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(self.src):
                    for file in files:
                        abs_path = os.path.join(root, file)
                        arcname = os.path.relpath(abs_path, self.src)
                        zipf.write(abs_path, arcname)
                        self.log(f"Added {arcname}")
                        processed += 1
                        if progress_callback:
                            progress_callback(processed, total_files)
            self.log("ZIP archive completed.")
        except Exception as e:
            self.log(f"ZIP backup failed: {e}", level="error")
            raise RuntimeError(f"Backup failed: {e}")

    def _full_backup(self, progress_callback=None):
        folder_name = os.path.basename(os.path.normpath(self.src))
        target_path = os.path.join(self.dest, folder_name)
        # Handle existing folder
        if os.path.exists(target_path):
            backups_dir = os.path.join(self.dest, "backups")
            os.makedirs(backups_dir, exist_ok=True)
            archived_name = f"{folder_name}_{self.timestamp}"
            archived_path = os.path.join(backups_dir, archived_name)
            if os.path.exists(archived_path):
                self.log(f"An archive for today already exists: {archived_path}. Skipping backup.")
                return
            self.log(f"Archiving existing backup to: {archived_path}")
            try:
                shutil.move(target_path, archived_path)
            except Exception as e:
                self.log(f"Failed to archive existing backup: {e}", level="error")
                raise RuntimeError(f"Backup failed: {e}")
        # Copy new
        self.log(f"Copying new backup to: {target_path}")
        try:
            total_files = sum(len(files) for _, _, files in os.walk(self.src))
            processed = 0
            os.makedirs(target_path, exist_ok=True)
            for root, dirs, files in os.walk(self.src):
                rel_root = os.path.relpath(root, self.src)
                target_root = os.path.join(target_path, rel_root)
                os.makedirs(target_root, exist_ok=True)
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(target_root, file)
                    shutil.copy2(src_file, dst_file) # Method preserving metadata
                    processed += 1
                    if progress_callback:
                        progress_callback(processed, total_files)
            self.log("Copy complete.")
        except Exception as e:
            self.log(f"Backup failed during copy: {e}", level="error")
            raise RuntimeError(f"Backup failed: {e}")
    
    def _build_logger_proxy(self, log_callback):
        def log(msg, level="info"):
            getattr(self.logger, level)(msg)
            if log_callback:
                log_callback(msg)
        return log
    
    # --- Utility methods ---
    @staticmethod
    def validate_destination_path(path:str)->bool:
        try:
            test_file = os.path.join(path, f"__test_{os.getpid()}.tmp")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except Exception:
            return False
        
    @staticmethod
    def validate_source_path(path:str)->bool:
        return os.path.isdir(path)