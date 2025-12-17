@echo off
chcp 65001 >nul
title Image Background Fix Web Service
color 0A
cls
echo.
echo ========================================
echo   图片背景修复工具 - Web服务启动器
echo ========================================
echo.
echo [检查依赖...]
python -c "import flask; import openai; import PIL; import numpy" 2>nul
if errorlevel 1 (
    echo.
    echo ⚠ 警告: 检测到依赖未安装或安装不完整
    echo.
    echo 是否现在安装依赖？(Y/N)
    set /p install_choice=
    if /i "%install_choice%"=="Y" (
        echo.
        echo 正在安装依赖...
        call install.bat
        if errorlevel 1 (
            echo.
            echo 依赖安装失败，请手动运行 install.bat
            pause
            exit /b 1
        )
    ) else (
        echo.
        echo 请先运行 install.bat 安装依赖
        pause
        exit /b 1
    )
)

echo.
echo [检查配置文件...]
if not exist .env (
    if exist env_example.txt (
        echo.
        echo ⚠ 警告: 未找到 .env 配置文件
        echo 正在从 env_example.txt 创建 .env 文件...
        copy env_example.txt .env >nul
        echo.
        echo 请编辑 .env 文件，填入你的 OpenAI API Key
        echo 然后重新运行此脚本
        echo.
        notepad .env
        pause
        exit /b 0
    )
)

echo.
echo [启动Web服务...]
echo.
echo ========================================
echo  服务地址: http://localhost:5000
echo  浏览器将自动打开
echo  按 Ctrl+C 停止服务
echo ========================================
echo.

echo [检查端口5000是否被占用...]
netstat -ano | findstr :5000 >nul
if not errorlevel 1 (
    echo 警告: 端口5000已被占用
    echo 请关闭占用该端口的程序，或按任意键继续尝试启动...
    pause >nul
)

echo [启动Flask服务器...]
python web_app.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo  启动失败！
    echo ========================================
    echo.
    echo 可能的原因：
    echo 1. 依赖未安装 - 请运行 install.bat
    echo 2. Python未安装或未添加到PATH
    echo 3. 端口5000被占用
    echo 4. .env 文件配置错误（不影响启动，只影响API调用）
    echo.
    echo 正在检查详细错误信息...
    echo.
    python -c "import flask; print('Flask: OK')" 2>&1
    python -c "import openai; print('OpenAI: OK')" 2>&1
    python -c "import PIL; print('Pillow: OK')" 2>&1
    python -c "import numpy; print('NumPy: OK')" 2>&1
    echo.
    pause
)

