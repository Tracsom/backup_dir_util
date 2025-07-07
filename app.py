from src.gui.app_controller import AppController
from tkinter import messagebox
import traceback
import sys
import os

def main():
    try:
        app = AppController()
        app.mainloop()
    except Exception as e:
        print(f"[ERROR] Application failed to launch: {e}", file=sys.stderr)
        # Write error to startup.log next to .exe
        try:
            exe_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
            with open(os.path.join(exe_dir, 'startup.log'), 'a', encoding='utf-8') as f:
                f.write(traceback.format_exc())
        except:
            pass # Failsafe: tkinter may not be available yet
        try:
            messagebox.showerror("Error", f"Application failed to launch:\n{e}")
        except:
            pass
        sys.exit(1) # Signal failure

if __name__ == "__main__":
    main()