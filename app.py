from src.gui.app_controller import AppController
import sys

def main():
    try:
        app = AppController()
        app.mainloop()
    except Exception as e:
        print(f"[ERROR] Application failed to launch: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()