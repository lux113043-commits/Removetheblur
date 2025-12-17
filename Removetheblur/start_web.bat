@echo off
chcp 65001 >nul
title Web Service
color 0A
cls
cd /d "%~dp0"

echo.
echo ========================================
echo   Image Background Fix Web Service
echo ========================================
echo.

echo [Checking dependencies...]
python -c "import flask; import openai; import PIL; import numpy" 2>nul
if errorlevel 1 (
    echo.
    echo WARNING: Dependencies not installed
    echo.
    echo Install now? (Y/N)
    set /p install_choice=
    if /i "%install_choice%"=="Y" (
        echo.
        echo Installing dependencies...
        call install.bat
        if errorlevel 1 (
            echo.
            echo Installation failed, please run install.bat manually
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo Please run install.bat first
        pause
        exit /b 1
    )
)

echo.
echo [Checking config file...]
if not exist .env (
    if exist env_example.txt (
        echo.
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
    )
)

echo.
echo [Starting Web Service...]
echo.
echo ========================================
echo   URL: http://localhost:5000
echo   Browser will open automatically
echo   Press Ctrl+C to stop
echo ========================================
echo.

echo [Checking port 5000...]
netstat -ano | findstr :5000 >nul
if not errorlevel 1 (
    echo WARNING: Port 5000 is in use
    echo Press any key to continue anyway...
    pause >nul
)

echo [Starting Flask server...]
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





