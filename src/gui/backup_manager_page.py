from src.utils.backup_job import BackupJob
from tkinter import (
    Frame, Label, Entry, Button, Checkbutton, Text, Scrollbar,
    BooleanVar, StringVar,
    filedialog,
    END, DISABLED, NORMAL
)
from tkinter.ttk import Progressbar

class BackupManagerPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # UI Variables
        self.src_path = StringVar()
        self.dst_path = StringVar()
        self.compress = BooleanVar()
        # Build UI
        self._build_layout()

    def _build_layout(self):
        Label(self, text="Backup Manager", font=("Helvetica", 16, "bold")).pack(pady=10)
        # Source input
        Label(self, text="Source Directory").pack()
        src_entry = Entry(self, textvariable=self.src_path, width=60)
        src_entry.pack(pady=2)
        src_entry.bind("<FocusOut>", self._validate_paths)
        src_entry.bind("<KeyRelease>", self._validate_paths)
        Button(self, text="Browse", command=self._browse_src).pack()
        # Destination input
        Label(self, text="Destination Directory").pack(pady=5)
        dest_entry = Entry(self, textvariable=self.dst_path, width=60)
        dest_entry.pack(pady=2)
        dest_entry.bind("<FocusOut>", self._validate_paths)
        dest_entry.bind("<KeyRelease>", self._validate_paths)
        Button(self, text="Browse", command=self._browse_dest).pack()
        # Compression
        Checkbutton(self, text="Compress to ZIP", variable=self.compress).pack(pady=5)
        # Log output
        self.log_text = Text(self, height=12, width=80, state=DISABLED)
        self.log_text.pack(pady=5)
        scroll = Scrollbar(self, command=self.log_text.yview)
        scroll.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scroll.set)
        # Start backup
        self.start_btn = Button(self, text="Start Backup", command=self._start_backup)
        self.start_btn.pack(pady=10)
        # Progress bar
        self.progress = Progressbar(self, length=500, mode="determinate")
        self.progress.pack(pady=5)

    def _browse_src(self):
        path = filedialog.askdirectory()
        if path:
            self.src_path.set(path)

    def _browse_dest(self):
        path = filedialog.askdirectory()
        if path:
            self.dst_path.set(path)

    def _validate_paths(self, *_):
        src = self.src_path.get().strip()
        dst = self.dst_path.get().strip()
        if not (src and dst):
            self.start_btn.config(state=DISABLED)
            return
        valid_src = BackupJob.validate_source_path(src)
        valid_dst = BackupJob.validate_destination_path(dst)
        if valid_src and valid_dst:
            self.start_btn.config(state=NORMAL)
        else:
            self.start_btn.config(state=DISABLED)

    def _start_backup(self):
        src = self.src_path.get().strip()
        dst = self.dst_path.get().strip()
        compress = self.compress.get()
        self.progress['value'] = 0
        self.update()
        def update_progress(current, total):
            pct = int((current/total) * 100)
            self.progress['value'] = pct
            self.update_idletasks()
        try:
            job = BackupJob(
                src=src,
                dest=dst,
                compress=compress,
                log_callback=self._log
            )
            job.run(progress_callback=update_progress)
            self._log("Backup complete.")
            self.progress['value'] = 100
        except Exception as e:
            self._log(f"Backup failed: {e}", level="error")
            self.progress['value'] = 0

    def _log(self, msg, level="info"):
        self.controller.logger.__getattribute__(level)(msg)
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, msg+"\n")
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)