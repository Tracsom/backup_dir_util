# PSEUDOCODE:
"""
Create Tkinter window
Allow user to:
* Browse for source directory
* Browse for backup destination
* When user selects destination:
* - Call `validate_destination_path(path)`
* - If invalid:
* - - Show error popup ("Cannot access destination. Check NAS connection.")
* - - Disable Start button
* - Else:
* - - Enable Start button
* Checkbox: enable zip compression
* Start backup button
* Display progress bar and log area
* Call utils.backup_handler on start
"""

from tkinter import Tk

class MainWindow(Tk):
    def __init__(self):
        super().__init__()

    def run(self):
        self.mainloop()