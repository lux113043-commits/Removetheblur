@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"
title 创建 .env 文件

echo ========================================
echo 创建 .env 配置文件
echo ========================================
echo.

if exist .env (
    echo .env 文件已存在
    echo.
    choice /C YN /M "是否要覆盖现有的 .env 文件"
    if errorlevel 2 (
        echo 已取消
        pause
        exit /b 0
    )
)

if exist env_example.txt (
    echo 正在从 env_example.txt 创建 .env 文件...
    copy env_example.txt .env >nul
    echo.
    echo ✓ .env 文件已创建
    echo.
    echo 请编辑 .env 文件并填入你的 OpenAI API Key
    echo.
    echo 按任意键打开 .env 文件进行编辑...
    pause >nul
    notepad .env
    echo.
    echo 完成！现在可以运行 run_web.bat 启动服务了
) else (
    echo ✗ 错误：找不到 env_example.txt 文件
    echo 请确保 env_example.txt 文件存在
)

echo.
pause


