import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(name:str, log_callback=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger
    # File handler
    timestamp = datetime.now().strftime("%Y%m%d")
    file_path = os.path.join(LOG_DIR, f"backup_{timestamp}.log")
    file_handler = logging.FileHandler(file_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(file_handler)
    # GUI callback handler (if supplied)
    if log_callback:
        gui_handler = LogCallbackHandler(log_callback)
        gui_handler.setLevel(logging.INFO)
        logger.addHandler(gui_handler)
    return logger

class LogCallbackHandler(logging.Handler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        log_entry = self.format(record)
        self.callback(log_entry)