from src.utils.nas_mapper import list_mapped_drives, map_network_drive, unmap_drive
from src.gui.nas_credential_prompt import NasCredentialPrompt
from src.utils.logger import setup_logger
from tkinter import (
    Toplevel, 
    Listbox, Button, Scrollbar, 
    END, SINGLE, 
    messagebox
)

class DriveManagerWindow(Toplevel):
    def __init__(self, master=None, log_callback=None):
        super().__init__(master)
        self.title("Network Drive Manager")
        self.geometry("500x350")
        self.logger = setup_logger('backup_app', log_callback)
        # Window contents
        # Drive listbox and scollbar
        self.drive_list = Listbox(self, selectmode=SINGLE, width=60)
        self.drive_list.pack(pady=10)
        scrollbar = Scrollbar(self)
        scrollbar.pack(side="right", fill="y")
        self.drive_list.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.drive_list.yview)
        # Buttons
        Button(self, text="Map New Drive", command=self.map_new).pack(pady=2)
        Button(self, text="Unmap Selected", command=self.unmap_selected).pack(pady=2)
        Button(self, text="Reconnect Selected", command=self.reconnect_selected).pack(pady=2)
        # Refresh view
        self.refresh_drive_list()

    def refresh_drive_list(self):
        self.drive_list.delete(0, END)
        for d in list_mapped_drives():
            self.drive_list.insert(END, f"{d['drive']} -> {d['remote']}")

    def map_new(self):
        cred = NasCredentialPrompt(self).result
        if cred:
            success = map_network_drive(
                cred['drive'], cred['unc'],
                cred.get('user'), cred.get('password')
            )
            if success:
                self.logger.info(f"Mapped {cred['unc']} to {cred['drive']}:")
                messagebox.showinfo("Success", f"Mapped to {cred['drive']}:")
                self.refresh_drive_list()
            else:
                self.logger.error("Failed to map drive.")
                messagebox.showerror("Error", "Mapping failed.")

    def unmap_selected(self):
        selected = self.drive_list.curselection()
        if not selected:
            return
        entry = self.drive_list.get(selected[0])
        drive_letter = entry.split(":")[0]
        confirm = messagebox.askyesno("Confirm", f"Unmap {drive_letter}: ?")
        if confirm:
            success = unmap_drive(drive_letter)
            if success:
                self.logger.info(f"Unmapped {drive_letter}:")
                self.refresh_drive_list()
            else:
                self.logger.error(f"Failed to unmap {drive_letter}: ")
                messagebox.showerror("Error", f"Failed to unmap {drive_letter}:")

    def reconnect_selected(self):
        selected = self.drive_list.curselection()
        if not selected:
            return
        entry = self.drive_list.get(selected[0])
        parts = entry.split("->")
        drive = parts[0].strip().replace(":", "")
        unc = parts[1].strip()
        cred = NasCredentialPrompt(self).result
        if cred:
            success = map_network_drive(
                drive, unc,
                cred.get('user'), cred.get('password')
            )
            if success:
                self.logger.info(f"Reconnected {drive}: to {unc}")
                messagebox.showinfo("Success", f"Reconnected {drive}: to {unc}")
                self.refresh_drive_list()
            else:
                self.logger.error("Reconnect failed.")
                messagebox.showerror("Error", "Reconnect failed.")