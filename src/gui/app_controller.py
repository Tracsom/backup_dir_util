from src.gui.backup_manager_page import BackupManagerPage
from src.gui.drive_manager_page import DriveManagerPage
from src.gui.landing_page import LandingPage
from src.utils.logger import setup_logger
from tkinter import Tk, Menu, Frame
import sys
import os

class AppController(Tk):
    def __init__(self):
        super().__init__()
        self.title("Backup Utility Suite")
        self.logger = setup_logger("backup_app")
        self.geometry("700x550")
        self.resizable(False, False)
        self.logger = setup_logger("backup_app", log_callback=self.gui_log_callback)
        # Set Icon from executable directory if present
        exe_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
        icon_path = os.path.join(exe_dir, "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                self.logger.warning(f"Could not set icon: {e}")
        # Page container
        self.container = Frame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        self.pages = {} # Page cache
        self._init_pages()
        self._init_menu()
        self.show_frame("LandingPage")

    def _init_pages(self):
        for PageClass in (LandingPage, BackupManagerPage, DriveManagerPage):
            page = PageClass(parent=self.container, controller=self)
            page_name = PageClass.__name__
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")

    def _init_menu(self):
        menubar = Menu(self)
        # Home
        home_menu = Menu(menubar, tearoff=0)
        home_menu.add_command(label="Landing Page", command=lambda: self.show_frame("LandingPage"))
        menubar.add_cascade(label="Home", menu=home_menu)
        # Tools
        tools_menu = Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Backup Manager", command=lambda: self.show_frame("BackupManagerPage"))
        tools_menu.add_command(label="Drive Manager", command=lambda: self.show_frame("DriveManagerPage"))
        menubar.add_cascade(label="Tools", menu=tools_menu)
        # Exit
        menubar.add_command(label="Exit", command=self.quit)

        self.config(menu=menubar)

    def show_frame(self, page_name):
        if page_name in self.pages:
            frame = self.pages[page_name]
            frame.tkraise()
        else:
            self.logger.warning(f"Unknown page: {page_name}")

    def gui_log_callback(self, msg):
        """Override this if pages implement their own log displays."""
        print(msg)