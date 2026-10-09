@echo off
setlocal
if not exist "%~dp0.venv\Scripts\python.exe" (
  echo Kompta Python environment not found at:
  echo "%~dp0.venv\Scripts\python.exe"
  echo Install the project dependencies before launching Kompta.
  pause
  exit /b 1
)
start "Kompta backend" /D "%~dp0" "%~dp0.venv\Scripts\python.exe" "%~dp0run.py"
timeout /t 2 /nobreak >nul
start "" "%~dp0index.html"
endlocal