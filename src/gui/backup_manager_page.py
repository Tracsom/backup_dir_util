from src.utils.backup_job import BackupJob
from src.utils.logger import setup_logger
from tkinter import (
    Frame, Label, Entry, Button, Checkbutton, Text, Scrollbar, LabelFrame,
    BooleanVar, StringVar,
    filedialog,
    END, DISABLED, NORMAL
)
from tkinter.ttk import Progressbar
from os.path import expanduser

class BackupManagerPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.logger = setup_logger("backup_app", self._log)
        # UI Variables
        self.src_path = StringVar()
        self.dst_path = StringVar()
        self.compress = BooleanVar()
        self.status_var = StringVar(value="Ready")
        # Build UI
        self._build_layout()

    def _build_layout(self):
        Label(
            self, 
            text="Backup Manager", 
            font=("Helvetica", 16, "bold")
        ).pack(pady=(10, 5))
        # --- Source selection ---
        src_frame = LabelFrame(self, text="Source Directory", padx=10, pady=5)
        src_frame.pack(fill="x", padx=10, pady=5)
        src_row = Frame(src_frame)
        src_row.pack(fill="x")
        Entry(src_row, textvariable=self.src_path, width=55).pack(side="left", padx=5, expand=True, fill="x")
        Button(src_row, text="Browse", command=self._browse_src).pack(side="right", padx=5)
        self._bind_validation_events(src_row)
        # --- Destination selection ---
        dst_frame = LabelFrame(self, text="Destination Directory", padx=10, pady=5)
        dst_frame.pack(fill="x", padx=10, pady=5)
        dst_row = Frame(dst_frame)
        dst_row.pack(fill="x")
        Entry(dst_row, textvariable=self.dst_path, width=60).pack(side="left", padx=5, expand=True, fill="x")
        Button(dst_row, text="Browse", command=self._browse_dest).pack(side="right", padx=5)
        self._bind_validation_events(dst_row)
        # --- Options ---
        options_frame = LabelFrame(self, text="Options", padx=10, pady=5)
        options_frame.pack(fill="x", padx=10, pady=5)
        Checkbutton(options_frame, text="Compress to ZIP", variable=self.compress).pack(anchor="w")
        # --- Progress and Status ---
        progress_frame = Frame(self)
        progress_frame.pack(pady=(10, 0))
        self.progress = Progressbar(progress_frame, length=500, mode="determinate")
        self.progress.pack()
        Label(self, textvariable=self.status_var, font=("Helvetica", 10, "italic")).pack(pady=(2, 10))
        # --- Start Button ---
        self.start_btn = Button(self, text="Start Backup", command=self._start_backup, state=DISABLED)
        self.start_btn.pack(pady=5)
        # Log output
        log_frame = LabelFrame(self, text="Backup Log", padx=10, pady=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        self.log_text = Text(log_frame, height=12, width=80, state=DISABLED, wrap="word")
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll = Scrollbar(log_frame, command=self.log_text.yview)
        scroll.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scroll.set)

    def _bind_validation_events(self, widget):
        widget.bind_all("<FocusOut>", self._validate_paths)
        widget.bind_all("<KeyRelease>", self._validate_paths)

    def _browse_src(self):
        path = filedialog.askdirectory(initialdir=expanduser("~"))
        if path:
            self.src_path.set(path)
            self._validate_paths()

    def _browse_dest(self):
        path = filedialog.askdirectory(initialdir=expanduser("~"))
        if path:
            self.dst_path.set(path)
            self._validate_paths()

    def _validate_paths(self, *_):
        src = self.src_path.get().strip()
        dst = self.dst_path.get().strip()
        if not (src and dst):
            self.start_btn.config(state=DISABLED)
            return
        valid_src = BackupJob.validate_source_path(src)
        valid_dst = BackupJob.validate_destination_path(dst)
        self.start_btn.config(state=NORMAL if valid_src and valid_dst else DISABLED)

    def _start_backup(self):
        src = self.src_path.get().strip()
        dst = self.dst_path.get().strip()
        compress = self.compress.get()
        self.progress['value'] = 0
        self.status_var.set("Backup in progress...")
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
            self.logger.info("Backup complete.")
            self.status_var.set("Backup complete.")
            self.progress['value'] = 100
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            self.status_var.set("Backup failed.")
            self.progress['value'] = 0

    def _log(self, msg, level="info"):
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, msg+"\n")
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)