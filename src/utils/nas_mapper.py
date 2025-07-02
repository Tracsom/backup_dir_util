import os
import subprocess

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
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"[map_network_drive] Failed: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"[map_network_drive] Exception: {e}")
        return False
    
def unmap_drive(drive_letter):
    """
    Unmap the specified network drive.
    """
    cmd = ["net", "use", f"{drive_letter}:", "/delete", "/y"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception as e:
        print(f"[unmap_drive] Exception: {e}")
        return False