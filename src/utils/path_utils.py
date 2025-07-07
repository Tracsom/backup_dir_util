import sys
import os

def get_runtime_path(*paths):
    """
    Returns a path relative to app root (works in both dev and PyInstaller builds).
    Example: get_runtime_path('logs') -> absolute path to logs/
    """
    if getattr(sys, 'frozen', False): # Running as a  compiled .exe
        base = sys._MEIPASS
    else: # Running in development mode
        base = os.path.dirname(os.path.abspath(__file__))
        # path_utils.py is in src/utils/
        base = os.path.abspath(os.path.join(base, '..', '..'))
    return os.path.join(base, *paths)