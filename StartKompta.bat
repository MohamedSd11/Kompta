@echo off
cd /d "%~dp0"
start "Kompta backend" cmd /k ".venv\Scripts\python.exe run.py"
timeout /t 2 /nobreak >nul
start "" index.html