import re
import subprocess
from src.utils.logger import setup_logger

# Network Drive class
class NetworkDrive:
    NET_TIMEOUT = 10 # Seconds
    def __init__(self, drive_letter, unc_path=None):
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
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=NetworkDrive.NET_TIMEOUT)
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
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=NetworkDrive.NET_TIMEOUT)
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
    
    @classmethod
    def from_mapping(cls, mapping:dict):
        return cls(drive_letter=mapping['drive'][0], unc_path=mapping['remote'])
    
    @staticmethod
    def list_mapped():
        """
        Returns a list of currently mapped drives.
        Format: 
            [
                {'drive': 'Z:', 'remote':'\\\\NAS\\Backups', 'status':'OK'}, 
                ... 
            ]
        Filters out IPC and printer connections (no drive letter).
        """
        logger = setup_logger("backup_app")
        try:
            result = subprocess.run(["net", "use"], capture_output=True, text=True, timeout=NetworkDrive.NET_TIMEOUT)
            lines = result.stdout.strip().splitlines()
            mappings = []
            seen = set()
            for line in lines:
                # Match both OK and Disconnected entries
                if re.match(r"^(OK|Disconnected|DISCONNECTED)\s+", line):
                    parts = re.split(r"\s{2,}", line.strip())
                    if len(parts) >= 3:
                        status = parts[0].strip()
                        drive = parts[1].strip().upper()
                        remote = parts[2].strip()
                        # Filter out entries without drive letters (e.g., IPC$, printers)
                        if not re.fullmatch(r"[A-Z]:", drive):
                            logger.debug(f"Skipping non-drive mapping: {line}")
                            continue
                        if drive in seen:
                            logger.warning(f"Duplicate drive entry found: {drive}")
                            continue
                        seen.add(drive)
                        mappings.append({
                            'drive': drive,
                            'remote': remote,
                            'status': status
                        })
                    else:
                        logger.debug(f"Skipping malformed net use line: {line}")
            return mappings
        except Exception as e:
            logger = setup_logger("backup_app")
            logger.error(f"Failed to list map drives: {e}")
            return []