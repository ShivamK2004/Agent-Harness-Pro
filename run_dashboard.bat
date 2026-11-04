@echo off
if not exist .venv\Scripts\activate.bat (
  echo Create environment first: py -3.11 -m venv .venv
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
streamlit run app\streamlit_app.py
