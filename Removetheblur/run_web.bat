@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title Web Service
color 0A
cls

echo ========================================
echo Starting Web Service
echo ========================================
echo.

echo [1] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python first
    pause
    exit /b 1
)
python --version

echo.
echo [2] Checking dependencies...
python -c "import flask; import openai; import PIL; import numpy" 2>nul
if errorlevel 1 (
    echo WARNING: Some dependencies are missing
    echo.
    echo Please run install.bat first
    pause
    exit /b 1
)
echo OK: All dependencies installed

echo.
echo [3] Checking .env file...
if not exist .env (
    if exist env_example.txt (
        echo WARNING: .env file not found
        echo Creating .env from env_example.txt...
        copy env_example.txt .env >nul
        echo.
        echo Please edit .env file and add your OpenAI API Key
        echo Then run this script again
        echo.
        notepad .env
        pause
        exit /b 0
    ) else (
        echo ERROR: .env file not found and env_example.txt not found
        pause
        exit /b 1
    )
)
echo OK: .env file exists

echo.
echo [4] Starting Flask server...
echo.
echo ========================================
echo   URL: http://localhost:5000
echo   Browser will open automatically
echo   Press Ctrl+C to stop
echo ========================================
echo.

timeout /t 2 /nobreak >nul
start http://localhost:5000

python web_app.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo   Startup Failed!
    echo ========================================
    echo.
    echo Possible reasons:
    echo 1. Dependencies not installed - run install.bat
    echo 2. Python not installed or not in PATH
    echo 3. Port 5000 is in use
    echo 4. .env file configuration error
    echo.
    pause
)
