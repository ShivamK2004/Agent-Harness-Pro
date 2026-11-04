@echo off
setlocal
if not exist "%~dp0.venv\Scripts\activate.bat" (
  echo Create the Python environment first: py -3.13 -m venv .venv
  pause
  exit /b 1
)
start "Agent Harness Pro API" /D "%~dp0" cmd /k "call .venv\Scripts\activate.bat ^&^& uvicorn harness.api.main:app --reload --host 127.0.0.1 --port 8000"
start "Agent Harness Pro Web" /D "%~dp0frontend" cmd /k "if not exist .env.local copy .env.local.example .env.local ^&^& if not exist node_modules npm install ^&^& npm run dev"
echo Backend: http://127.0.0.1:8000/docs
echo Frontend: http://localhost:3000
