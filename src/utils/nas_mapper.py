import os
import subprocess
from src.utils.logger import setup_logger

logger = setup_logger("backup_app")

def is_network_path(path):
    return path.replace("/", "\\").startswith("\\\\")

def map_network_drive(drive_letter, unc_path, username=None, password=None):
    """
    Attempt to map UNC path to drive letter using net use.
    Returns True on success, False otherwise.
    """
    cmd = ["net", "use", drive_letter+":", unc_path]
    if username and password:
        cmd.extend([password, "/user:"+username])
    cmd.append("/persistent:no")
    logger.info(f"Attempting to map drive {drive_letter}: to {unc_path}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"Successfully mapped {drive_letter}: to {unc_path}")
            return True
        else:
            logger.error(f"Drive mapping failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"Exception during drive mapping: {e}")
        return False
    
def unmap_drive(drive_letter):
    """
    Unmap the specified network drive.
    """
    cmd = ["net", "use", f"{drive_letter}:", "/delete", "/y"]
    logger.info(f"Attempting to unmap drive {drive_letter}:")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logger.info(f"Drive {drive_letter}: unmapped successfully.")
            return True
        else:
            logger.error(f"Failed to unmap drive {drive_letter}: {result.stderr.strip()}")
            return False
    except Exception as e:
        logger.error(f"Exception during unmap: {e}")
        return False