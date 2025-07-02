from src.gui.main_window import MainWindow
import sys

def main():
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"[ERROR] Application failed to launch: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()