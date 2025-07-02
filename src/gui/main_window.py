from src.utils.backup_handler import validate_destination_path, perform_backup
from src.utils.nas_mapper import is_network_path, map_network_drive
from src.gui.nas_credential_prompt import NasCredentialPrompt
from src.utils.logger import setup_logger
from tkinter import (
    Tk, 
    Label, Entry, Button, Checkbutton, Text,
    StringVar, BooleanVar, 
    filedialog, messagebox, 
    END
)
from tkinter.ttk import Progressbar

class MainWindow(Tk):

    def __init__(self):
        # Initialize window
        super().__init__()
        self.title("Backup Directory Utility")
        self.geometry("600x400")
        self.resizable(False, False)
        # Initialize logger
        self.logger = setup_logger(
            "backup_app", 
            log_callback=lambda msg: self.logs.insert(END, msg+"\n")
        )
        # Initialize variables
        self.source_path = StringVar()
        self.dest_path = StringVar()
        self.compress = BooleanVar()
        # Build layout
        self.layout()

    def run(self):
        self.mainloop()

    def browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_path.set(path)
            self.logger.info(f"Selected source: {path}")

    def browse_dest(self):
        path = filedialog.askdirectory()
        if path:
            mapped_path = self.try_map_network_path(path)
            self.dest_path.set(mapped_path)
            if not validate_destination_path(mapped_path):
                self.logger.error(f"Invalid destination: {mapped_path}")
                messagebox.showerror("Invalid Path", "Cannot access destination. Check NAS connection or permissions.")
                self.start_btn.config(state="disabled")
            else:
                self.logger.info(f"Valid destination: {mapped_path}")
                self.start_btn.config(state="normal")
    
    def try_map_network_path(self, path):
        if is_network_path(path) and not validate_destination_path(path):
            if messagebox.askyesno("Map Network Drive", "This appears to be a network path. Do you want to map it?"):
                cred = NasCredentialPrompt(self).result
                if cred:
                    success = map_network_drive(
                        cred['drive'], cred['unc'],
                        cred.get('user'), cred.get('password')
                    )
                    if success:
                        self.logger.info(f"Mapped {cred['unc']} to {cred['drive']}:")
                        messagebox.showinfo("Mapped", f"{cred['unc']} mapped to {cred['drive']}:")
                        return f"{cred['drive']}:\\"
                    else:
                        self.logger.error("Network drive mapping failed.")
                        messagebox.showerror("Error", "Failed to map network drive.")
                        self.start_btn.config(state="disabled")
                        return path
        return path
    
    def start_backup(self):
        src = self.source_path.get()
        dst = self.dest_path.get()
        comp = self.compress.get()
        if not src or not dst:
            messagebox.showwarning("Missing Paths", "Please select both source and destination directories.")
            self.logger.warning("Backup attempted without valid source/destination.")
            return
        self.progress['value'] = 0
        self.logger.info("Starting backup...")
        self.update()
        try:
            perform_backup(
                src, dst, comp, 
                log_callback=lambda msg: self.logs.insert(END, msg + "\n")
            )
            self.logger.info("Backup complete.")
        except Exception as e:
            self.logger.error(f"Error: {e}")
            messagebox.showerror("Backup Failed", str(e))
        self.progress['value'] = 100
        self.update()

    def layout(self):
        # GUI layout
        # Source
        Label(self, text="Source Directory:").pack(pady=5)
        Entry(self, textvariable=self.source_path, width=60).pack()
        Button(self, text="Browse", command=self.browse_source).pack(pady=2)
        # Destination
        Label(self, text="Destination Directory").pack(pady=5)
        Entry(self, textvariable=self.dest_path, width=60).pack()
        Button(self, text="Browse", command=self.browse_dest).pack(pady=2)
        # Compression
        Checkbutton(self, text="Compress to ZIP", variable=self.compress).pack(pady=5)
        # Start
        self.start_btn = Button(self, text="Start Backup", command=self.start_backup)
        self.start_btn.pack(pady=10)
        # Progress
        self.progress = Progressbar(self, length=400, mode='determinate')
        self.progress.pack(pady=5)
        # Logs
        self.logs = Text(self, height=10, width=70)
        self.logs.pack(pady=10)