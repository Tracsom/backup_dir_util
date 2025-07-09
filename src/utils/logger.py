import os
import sys
import glob
import socket
import logging
import tempfile
from datetime import datetime

def clean_old_logs(directory, keep_last=90):
    """Clean old log files, keeping most recent `keep_last`."""
    files = sorted(glob.glob(os.path.join(directory, "*_backup_*.log")), reverse=True)
    for f in files[keep_last:]:
        try:
            os.remove(f)
        except Exception:
            pass

def get_default_log_dir():
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        base_dir =  os.path.dirname(sys.executable)
    else:
        # Running as script
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

LOG_DIR = get_default_log_dir() # Default log directory
HOSTNAME = socket.gethostname() # Get the system hostname

def setup_logger(name:str, log_callback=None, log_dir=None):
    log_dir = log_dir or LOG_DIR
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False # Prevent propagation to root logger

    # Add file handler only if not present
    file_handler_exists = any(
        isinstance(h, logging.FileHandler) and h.baseFilename.startswith(log_dir)
        for h in logger.handlers
    )
    if not file_handler_exists:
        timestamp = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(log_dir, f"{HOSTNAME}_backup_{timestamp}.log")
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(file_handler)
    # Add GUI handler only if not present for this callback
    if log_callback and not any(
        isinstance(h, LogCallbackHandler) and getattr(h, "callback", None) == log_callback
        for h in logger.handlers
    ):
        gui_handler = LogCallbackHandler(log_callback)
        gui_handler.setLevel(logging.INFO)
        gui_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(gui_handler)

    return logger

class LogCallbackHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        log_entry = self.format(record)
        self.callback(log_entry)