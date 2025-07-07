from src.gui.app_controller import AppController
from tkinter import messagebox
import sys

def main():
    try:
        app = AppController()
        app.mainloop()
    except Exception as e:
        print(f"[ERROR] Application failed to launch: {e}", file=sys.stderr)
        try:
            messagebox.showerror("Startup Error", f"Application failed to launch:\n{e}")
        except:
            pass # Failsafe: tkinter may not be available yet

if __name__ == "__main__":
    main()