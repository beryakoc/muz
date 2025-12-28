@echo off
REM Helper script to run the Django server with virtual environment activated (Windows)

cd /d "%~dp0"
call venv\Scripts\activate.bat
python manage.py runserver


