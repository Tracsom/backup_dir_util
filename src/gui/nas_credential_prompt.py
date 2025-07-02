from tkinter import Label, Entry
from tkinter.simpledialog import Dialog

class NasCredentialPrompt(Dialog):
    def body(self, master):
        # Labels
        Label(master, text="UNC Path:").grid(row=0, sticky="w", padx=5, pady=2)
        Label(master, text="Drive Letter:").grid(row=1, sticky="w", padx=5, pady=2)
        Label(master, text="Username:").grid(row=2, sticky="w", padx=5, pady=2)
        Label(master, text="Password:").grid(row=3, sticky="w", padx=5, pady=2)
        # Entry boxes
        self.unc = Entry(master, width=40)
        self.drive = Entry(master, width=5)
        self.user = Entry(master, width=25)
        self.password = Entry(master, show="*", width=25)
        # Set Entries to grid
        self.unc.grid(row=0, column=1, padx=5, pady=2)
        self.drive.grid(row=1, column=1, padx=5, pady=2)
        self.user.grid(row=2, column=1, padx=5, pady=2)
        self.password.grid(row=3, column=1, padx=5, pady=2)
        # Default values
        self.drive.insert(0, "B")
        return self.unc # Initial focus

    def validate(self):
        unc = self.unc.get().strip()
        drive = self.drive.get().strip().upper()
        return (
            unc.startswith("\\\\") and
            len(drive) == 1 and drive.isalpha()
        )
    
    def apply(self):
        self.result = {
            "unc": self.unc.get().strip(),
            "drive": self.drive.get().strip().upper(),
            "user": self.user.get().strip(),
            "password": self.password.get()
        }