# PSEUDOCODE:
"""
Import MainWindow from src.gui.main_window
run MainWindow class (tkinter mainloop)
"""

from src.gui.main_window import MainWindow

def main():
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main()