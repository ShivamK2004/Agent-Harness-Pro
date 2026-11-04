@echo off
call .venv\Scripts\activate.bat
uvicorn harness.api.main:app --reload --host 127.0.0.1 --port 8000
