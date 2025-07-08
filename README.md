# Backup Directory Utility

A standalone, GUI-based backup tool for Windows systems (Windows 95 and up). 

Supports:
- Full directory mirroring with metadata
- Compressed ZIP archives (Optional)
- Auto-archiving with timestamp folders
- NAS/UNC mapping with credential support
- Logging to local file and GUI console
- Portable: can run from NAS share

---

## Features
- Modular OOP architecture (extensible and testable)
- Tkinter GUI with:
+ Backup manager
+ Drive manager
- Intelligent backup logic:
+ Archives previous runs to `/backups/`
+ Prevents multiple same-day overwrites (keeps oldest)
- Optional ZIP compression mode
- Local logging (timestamp + hostname)
- PyInstaller-compatable for `.exe` builds

---

## Usage

### Run from source (dev mode)

```bash
python app.py
```
### Build to Windows executable

```bash
pyinstaller app.py --noconsole --windowed --onefile --icon=icon.ico --name="BackupUtility"
```
This generates a standalone `.exe` in the `dist/` folder.
You can then copy the following to a NAS or USB:

BackupUtility/
|- BackupUtility.exe
|- icon.ico
|- logs/

## Requirements
- Python 3.10+
- OS: Windows 95+
- No third-party packages required
(Tkinter, shutil, zipfile, logging, and subprocesses are all built-in.)

## Structure
app/
|- app.py   # Entry Point
|- requirements.txt
|- README.md
|- icon.ico
|- .gitignore
|- logs/
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

This project is licensed under the MIT License.
You're free to use, modify, and distribute with attribution.

## Notes
- Compatable with PyInstaller `--onefile` mode
- Logs written to `logs/` next to the executable
- Can be run directly from a NAS share (or mapped UNC)