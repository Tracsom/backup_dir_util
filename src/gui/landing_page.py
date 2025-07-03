from tkinter import Frame, Label, Button

class LandingPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self._build_layout()

    def _build_layout(self):
        Label(self, text="Backup Utility Suite", font=("Helvetica", 20, "bold")).pack(pady=20)
        Label(self, text="A lightweight utility for backups and drive mapping", font=("Helvetica", 12)).pack(pady=5)
        Button(
            self, 
            text="Launch Backup Manager", 
            width=30, 
            command=lambda:self.controller.show_frame()
        ).pack(pady=15)
        Button(
            self, 
            text="Launch Drive Manager", 
            width=30, 
            command=lambda:self.controller.show_frame()
        ).pack(pady=10)
        Button(
            self, 
            text="Exit Application", 
            width=20, 
            command=lambda:self.controller.quit
        ).pack(pady=40)