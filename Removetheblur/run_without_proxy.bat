@echo off
echo ========================================
echo 启动Web服务（无代理模式）
echo ========================================
echo.

echo [1] 禁用代理设置...
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
set ALL_PROXY=
set all_proxy=
echo ✓ 代理已禁用

echo.
echo [2] 启动Web服务...
echo.

cd /d "%~dp0"
python web_app.py




