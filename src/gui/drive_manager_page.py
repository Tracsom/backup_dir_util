from src.gui.nas_credential_prompt import NasCredentialPrompt
from src.utils.network_drive import NetworkDrive
from src.utils.logger import set_logger
from tkinter import (
    Frame, LabelFrame, Label, Listbox, Button, Scrollbar, StringVar, Text,
    END, SINGLE, DISABLED, NORMAL,
    messagebox
)

class DriveManagerPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.status = StringVar(value="Ready")
        self.logger = set_logger("backup_app", self._log)
        Label(
            self, 
            text="Drive Manager", 
            font=("Helvetica", 16, "bold")
        ).pack(pady=(10, 5))
        # --- Drive List ---
        list_frame = LabelFrame(self, text="Mapped Drives", padx=10, pady=5)
        list_frame.pack(fill="x", padx=10, pady=5)
        self.drive_list = Listbox(list_frame, selectmode=SINGLE, width=60, height=8)
        self.drive_list.pack(side="left", fill="both", expand=True)
        scrollbar = Scrollbar(list_frame, command=self.drive_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.drive_list.config(yscrollcommand=scrollbar.set)
        # --- Status Message ---
        self.status_label = Label(self, textvariable=self.status, font=("Helvetica", 10, "italic"))
        self.status_label.pack(pady=(0, 10))
        # --- Actions ---
        action_frame = LabelFrame(self, text="Drive Operations", padx=10, pady=5)
        action_frame.pack(fill="x", padx=10, pady=5)
        btn_row = Frame(action_frame)
        btn_row.pack()
        Button(btn_row, text="Map New Drive", width=18, command=self._map_new).pack(padx=5)
        Button(btn_row, text="Unmap Selected", width=18, command=self._unmap_selected).pack(padx=5)
        Button(btn_row, text="Reconnect Selected", width=18, command=self._reconnect_selected).pack(padx=5)
        # --- Log Panel ---
        log_frame = LabelFrame(self, text="Drive Manager Log", padx=10, pady=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_text = Text(log_frame, height=10, width=80, state=DISABLED, wrap="word")
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll = Scrollbar(log_frame, command=self.log_text.yview)
        scroll.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scroll.set)
        # Refresh view
        self._refresh_drive_list()
    
    def _refresh_drive_list(self):
        self.drive_list.delete(0, END)
        drives = NetworkDrive.list_mapped()
        for d in drives:
            entry = f"{d['drive']} -> {d['remote']} [{d['status']}]"
            self.drive_list.insert(END, entry)
            index = self.drive_list.size() - 1
            # Set color based on status
            if d['status'] == 'OK':
                self.drive_list.itemconfig(index, {'fg': 'green'})
            elif d['status'] == 'DISCONNECTED' or d['status'] == 'Disconnected':
                self.drive_list.itemconfig(index, {'fg': 'gray'})
            else:
                self.drive_list.itemconfig(index, {'fg': 'red'})
        self._set_status(f"{len(drives)} drive(s) mapped.", "neutral")
    
    def _map_new(self):
        cred = NasCredentialPrompt(self).result
        if cred:
            drive = NetworkDrive(drive_letter=cred['drive'], unc_path=cred['unc'])
            success = drive.map(username=cred.get('user'), password=cred.get('password'))
            if success:
                self.logger.info(f"Mapped {drive}.")
                self._set_status(f"Mapped {drive.drive_letter}: -> {drive.unc_path}", "success")
                messagebox.showinfo("Success", f"Mapped to {drive.drive_letter}:")
                self._refresh_drive_list()
            else:
                self.logger.error(f"Failed to map {drive}")
                self._set_status("Mapping failed.", "error")
                messagebox.showerror("Error", "Mapping failed.")

    def _unmap_selected(self):
        selected = self.drive_list.curselection()
        if not selected:
            return
        entry = self.drive_list.get(selected[0])
        drive_letter = entry.split(":")[0]
        if messagebox.askyesno("Confirm", f"Unmap {drive_letter}: ?"):
            drive = NetworkDrive(drive_letter=drive_letter)
            success = drive.unmap()
            if success:
                self.logger.info(f"Unmapped {drive}")
                self._set_status(f"Unmapped {drive.drive_letter}:", "success")
                self._refresh_drive_list()
            else:
                self.logger.error(f"Failed to unmap {drive}")
                self._set_status("Unmap failed.", "error")
                messagebox.showerror("Error", f"Failed to unmap {drive_letter}:")

    def _reconnect_selected(self):
        selected = self.drive_list.curselection()
        if not selected:
            return
        entry = self.drive_list.get(selected[0])
        drive_letter, unc = [x.strip().strip(":") for x in entry.split("->")]
        drive = NetworkDrive(drive_letter=drive_letter, unc_path=unc)
        cred = NasCredentialPrompt(self).result
        if cred:
            success = drive.reconnect(username=cred.get('user'), password=cred.get('password'))
            if success:
                self._log(f"Reconnected {drive}")
                self._set_status(f"Reconnected {drive.drive_letter}:", "success")
                messagebox.showinfo("Success", f"Reconnected {drive}")
                self._refresh_drive_list()
            else:
                self._log(f"Reconnect failed for {drive}", level="error")
                self._set_status("Reconnect failed.", "error")
                messagebox.showerror("Error", "Reconnect failed.")

    def _set_status(self, msg, state="neutral"):
        self.status.set(msg)
        color = {
            "success": "green",
            "error": "red",
            "neutral": "gray"
        }.get(state, "gray")
        self.status_label.config(fg=color)

    def _log(self, msg, level="info"):
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, f"{msg}\n")
        self.log_text.see(END)
        self.log_text.config(state=DISABLED)