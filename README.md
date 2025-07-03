# Backup Directory Utility

A standalone, GUI-based backup tool for Windows systems (Windows 95 and up). Supports:
- Full directory backups
- Compressed ZIP archives
- Daily archival with timestamp
- Network drive mapping (UNC/NAS support)
- Clean GUI with logging and status feedback

## Features
- Modular OOP design
- Tkinter GUI with Backup + Drive manager pages
- Backup progress and logs
- Auto-archiving to backups/ folder
- Optional compression
- Cross-system portable (Works from NAS)

## Usage
```bash
python app.py
```
Or build to .exe using:
```bash
pyinstaller app.py --noconsole --windowed --onefile --name="BackupUtility"
```

## Requirements
- Python 3.8+
- Works best on Windows, supports older systems with zip fallback

## Structure
app/
|- app.py   # Entry Point
|- requirements.txt
|- README.md
|- .gitignore
|- src/
    |- gui/
    |   |- app_controller.py
    |   |- backup_manager_page.py
    |   |- drive_manager_page.py
    |   |- nas_credential_prompt.py
    |   |- landing_page.py
    |
    |- utils/
        |- backup_job.py
        |- network_drive.py
        |- logger.py

## License
MIT--free to modify and use.