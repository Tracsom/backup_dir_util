import re
import subprocess
from src.utils.logger import setup_logger

# Network Drive class
class NetworkDrive:
    def __init__(self, drive_letter, unc_path):
        self.drive_letter = drive_letter
        self.unc_path = unc_path 
        self.logger = setup_logger('backup_app')

    # --- Magic methods ---
    def __str__(self):
        return f"{self.drive_letter}: -> {self.unc_path or '[NOT SET]'}"
    
    def __repr__(self):
        return f"NetworkDrive(drive_letter='{self.drive_letter}', unc_path='{self.unc_path}')"
    
    def __eq__(self, other):
        return (isinstance(other, NetworkDrive)) and \
            self.drive_letter == other.drive_letter and \
            self.unc_path == other.unc_path
    
    def __hash__(self):
        return hash((self.drive_letter, self.unc_path))
    
    # --- Properties with validation ---
    @property
    def drive_letter(self):
        return self._drive_letter
    
    @drive_letter.setter
    def drive_letter(self, value):
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z]", value.strip()):
            raise ValueError(f"Invalid drive letter: '{value}'. Must be a single letter.")
        self._drive_letter = value.upper()

    @property
    def unc_path(self):
        return self._unc_path
    
    @unc_path.setter
    def unc_path(self, value):
        if value is None:
            self._unc_path = None
            return
        if not isinstance(value, str) or not re.match(r"^\\\\[^\\]+\\[^\\]+", value.strip()):
            raise ValueError(f"Invalid UNC path: '{value}'")
        self._unc_path = value.strip()

    # --- Drive Actions ---
    def map(self, username=None, password=None):
        cmd = ["net", "use", f"{self.drive_letter}:", self.unc_path]
        if username and password:
            cmd += [password, f"/user:{username}"]
        cmd.append("/persistent:no")
        self.logger.info(f"Mapping {self.drive_letter}: to {self.unc_path}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode==0:
                self.logger.info(f"Mapped successfully.")
                return True
            else:
                self.logger.error(f"Mapping failed: {result.stderr.strip()}")
                return False
        except Exception as e:
            self.logger.error(f"Exception during mapping: {e}")
            return False
        
    def unmap(self):
        cmd = ["net", "use", f"{self.drive_letter}:", "/delete", "/y"]
        self.logger.info(f"Unmapping {self.drive_letter}:")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.logger.info(f"Unmapped successfully.")
                return True
            else:
                self.logger.error(f"Unmap failed: {result.stderr.strip()}")
                return False
        except Exception as e:
            self.logger.error(f"Exception during unmap: {e}")
            return False
        
    def reconnect(self, username=None, password=None):
        """
        Re-map the drive with existing UNC path.
        """
        if not self.unc_path:
            self.logger.warning("Reconnect failed. UNC path not set.")
            return False
        return self.map(username, password)
        
    # --- Utility ---
    @staticmethod
    def is_network_path(path):
        return path.replace("/", "\\").startswith("\\\\")
    
    @staticmethod
    def list_mapped():
        """
        Returns a list of currently mapped drives.
        Format [ {'drive': 'Z:', 'remote':'\\\\NAS\\Backups'}, ... ]
        """
        try:
            result = subprocess.run(["net","use"], capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().splitlines()
            mappings = []
            for line in lines:
                if ":" in line and "\\" in line:
                    parts = line.split()
                    drive = parts[0]
                    remote = parts[-2] if parts[-1] == 'OK' else parts[-1]
                    mappings.append({'drive': drive, 'remote': remote})
            return mappings
        except Exception as e:
            logger = setup_logger("backup_app")
            logger.error(f"Failed to list map drives: {e}")
            return []