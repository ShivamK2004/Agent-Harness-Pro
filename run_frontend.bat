@echo off
setlocal
cd /d "%~dp0frontend"
if not exist node_modules (
  echo Installing frontend dependencies...
  call npm install
  if errorlevel 1 goto :error
)
if not exist .env.local copy .env.local.example .env.local >nul
call npm run dev
exit /b %errorlevel%
:error
echo Frontend setup failed. Check Node.js and npm, then run npm install in the frontend folder.
pause
exit /b 1
