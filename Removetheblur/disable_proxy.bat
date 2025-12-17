@echo off
echo ========================================
echo 禁用代理设置
echo ========================================
echo.
echo 正在清除代理环境变量...
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
set ALL_PROXY=
set all_proxy=
echo.
echo ✓ 代理已禁用
echo.
echo 注意：这个设置只在当前命令行窗口有效
echo 关闭窗口后需要重新运行此脚本
echo.
echo 现在可以运行 run_web.bat 或 python web_app.py
echo.
pause




