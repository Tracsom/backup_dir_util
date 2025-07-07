import os
import socket
import logging
import tempfile
from datetime import datetime
from src.utils.path_utils import get_runtime_path

LOG_DIR = get_runtime_path('logs') # Default log directory
HOSTNAME = socket.gethostname() # Get the system hostname
# Try logs folder next to app; fallback to temp directory if it fails
try:
    LOG_DIR = get_runtime_path("logs")
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception:
    LOG_DIR = os.path.join(tempfile.gettempdir(), "backup_logs")
    os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name:str, log_callback=None, log_dir=None):
    log_dir = log_dir or LOG_DIR
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.hasHandlers():
        timestamp = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(log_dir, f"{HOSTNAME}_backup_{timestamp}.log")
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(file_handler)
    
    if log_callback:
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