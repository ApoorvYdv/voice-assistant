@echo off
REM Navigate to the backend directory
cd /d "%~dp0\..\backend" || exit /b 1

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    pip install uv
    uv venv
)

REM Activate the virtual environment
call .venv\bin\activate

REM 
uv sync