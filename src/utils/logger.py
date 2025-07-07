import logging
import os
from datetime import datetime

LOG_DIR = os.path.join(os.getcwd(), "logs")

def setup_logger(name:str, log_callback=None, log_dir=None):
    log_dir = log_dir or LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.hasHandlers():
        timestamp = datetime.now().strftime("%Y%m%d")
        file_path = os.path.join(log_dir, f"backup_{timestamp}.log")
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