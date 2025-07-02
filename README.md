# Backup Directory Utility

A lightweight, standalone backup utility for Windows systems (from Windows 95 onward). 
This app allows users to backup folders to local or networked destinations (including NAS devices), 
with optional ZIP compression. Built with Python and a Tkinter GUI for maximum compatibility.

---
## Features
* GUI-based directory selection
* Support for NAS destinations with connection validaton
* Optional .zip compression for backup
* Progress feedback and logging
* Minimal dependencies (Windows 95+ compatible)
* Easy standalone `.exe` build with PyInstaller
---

## Directory Structure
app/
|-gui/ # GUI interface components
|-utils/ # Backup logic and helpers
|-app.py # Entrypoint
|-.gitignore
|-requirements.txt
|-README.md

---
## Getting started
### 1. Clone the repo
bash
```
git clone https://github.com/Tracsom/backup_dir_util.git
cd backup_dir_util
```
### 2. Create virtual enviroment (optional but recommended)
bash
```
python -m venv venv
venv\scripts\activate # or source venv/vin/activate on UNIX
```
### 3. Install requirements
bash
```
pip install -r requirements.txt
```
### 4. Run the app
bash
```
python app.py
```
---

## Build Standalone EXE
User PyInstaller to build for Windows:
bash
```
pyinstaller --onefile app.py
```
Output will be in the dist/ folder

---
### LICENSE (MIT License)
MIT License

Copyright (c) 2025 Jonathan Wong

Permission is hereby granted, free of chage, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction.
