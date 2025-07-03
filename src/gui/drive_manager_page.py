from src.gui.nas_credential_prompt import NasCredentialPrompt
from src.utils.network_drive import NetworkDrive
from tkinter import (
    Frame, Listbox, Button, Scrollbar,
    END, SINGLE,
    messagebox
)

class DriveManagerPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Result list with scrollbar
        self.drive_list = Listbox(self, selectmode=SINGLE, width=60)
        self.drive_list.pack(pady=10)
        scrollbar = Scrollbar(self)
        scrollbar.pack(side="right", fill="y")
        self.drive_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.drive_list.yview)
        # Action buttons
        Button(self, text="Map New Drive", command=self._map_new).pack(pady=2)
        Button(self, text="Unmap Selected", command=self._unmap_selected).pack(pady=2)
        Button(self, text="Reconnect Selected", command=self._reconnect_selected).pack(pady=2)
        # Refresh view
        self._refresh_drive_list()
    
    def _refresh_drive_list(self):
        self.drive_list.delete(0, END)
        drives = NetworkDrive.list_mapped()
        for d in drives:
            self.drive_list.insert(END, f"{d['drive']} -> {d['remote']}")
    
    def _map_new(self):
        cred = NasCredentialPrompt(self).result
        if cred:
            drive = NetworkDrive(drive_letter=cred['drive'], unc_path=cred['unc'])
            success = drive.map(username=cred.get('user'), password=cred.get('password'))
            if success:
                self._log(f"Mapped {drive}.")
                messagebox.showinfo("Success", f"Mapped to {drive.drive_letter}:")
                self._refresh_drive_list()
            else:
                self._log(f"Failed to map {drive}", level="error")
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
                self._log(f"Unmapped {drive}")
                self._refresh_drive_list()
            else:
                self._log(f"Failed to unmap {drive}", level="error")
                messagebox.showerror("Error", f"Failed to unmap {drive_letter}:")

    def _reconnect_selected(self):
        selected = self.drive_list.curselection()
        if not selected:
            return
        entry = self.drive_list.get(selected[0])
        drive_letter, unc = [x.strip() for x in entry.split("->")]
        drive = NetworkDrive(drive_letter=drive_letter, unc_path=unc)
        cred = NasCredentialPrompt(self).result
        if cred:
            success = drive.reconnect(username=cred.get('user'), password=cred.get('password'))
            if success:
                self._log(f"Reconnected {drive}")
                messagebox.showinfo("Success", f"Reconnected {drive}")
                self._refresh_drive_list()
            else:
                self._log(f"Reconnect failed for {drive}", level="error")
                messagebox.showerror("Error", "Reconnect failed.")

    def _log(self, msg, level="info"):
        self.controller.logger.__getattribute__(level)(msg)