@echo off
chcp 65001 >nul
echo ========================================
echo 手动安装依赖包（逐个安装）
echo ========================================
echo.
echo 如果自动安装失败，请使用此脚本逐个安装
echo.

echo [1/5] 安装 openai...
python -m pip install openai>=1.12.0 --no-warn-script-location
if errorlevel 1 (
    echo openai 安装失败
    pause
    exit /b 1
)

echo [2/5] 安装 pillow...
python -m pip install pillow>=10.2.0 --no-warn-script-location
if errorlevel 1 (
    echo pillow 安装失败
    pause
    exit /b 1
)

echo [3/5] 安装 python-dotenv...
python -m pip install python-dotenv>=1.0.0 --no-warn-script-location
if errorlevel 1 (
    echo python-dotenv 安装失败
    pause
    exit /b 1
)

echo [4/5] 安装 numpy...
python -m pip install numpy>=1.26.0 --no-warn-script-location
if errorlevel 1 (
    echo numpy 安装失败
    pause
    exit /b 1
)

echo [5/5] 安装 flask...
python -m pip install flask>=3.0.0 --no-warn-script-location
if errorlevel 1 (
    echo flask 安装失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 所有依赖安装完成！
echo ========================================
pause





