@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo Installing dependencies...
echo ========================================
echo.

echo [1/3] Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Warning: pip upgrade failed, continuing...
)
echo.

echo [2/3] Installing packages from requirements.txt...
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo.
    echo Mirror failed, trying official source...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ========================================
        echo Installation failed!
        echo ========================================
        echo Please check:
        echo 1. Is Python installed correctly?
        echo 2. Is network connection OK?
        echo 3. Is firewall blocking?
        echo.
        echo You can try manual installation:
        echo pip install openai pillow python-dotenv numpy flask
        echo ========================================
        pause
        exit /b 1
    )
)
echo.

echo [3/3] Verifying installation...
python -c "import openai; import PIL; import flask; import numpy; print('All dependencies installed successfully!')" 2>nul
if errorlevel 1 (
    echo Warning: Some dependencies may not be installed correctly
) else (
    echo.
    echo ========================================
    echo Installation completed!
    echo ========================================
)
echo.
pause
