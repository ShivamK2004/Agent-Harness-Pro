@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\activate.bat (
  echo Create the Python environment first: py -3.13 -m venv .venv
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
uvicorn harness.api.main:app --reload --host 127.0.0.1 --port 8000
