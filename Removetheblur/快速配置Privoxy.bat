@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo Privoxy 配置助手
echo ========================================
echo.

echo 这个脚本将帮助你配置 Privoxy
echo 将 SOCKS5 代理转换为 HTTP 代理
echo.

echo [1] 检查 Privoxy 是否已安装...
set PRIVOXY_PATH=C:\Program Files\Privoxy\config.txt
if not exist "%PRIVOXY_PATH%" (
    echo.
    echo ✗ Privoxy 未安装或不在默认位置
    echo.
    echo 请先下载并安装 Privoxy:
    echo https://www.privoxy.org/
    echo.
    echo 安装完成后，将 config.txt 的路径告诉脚本
    echo 或者手动编辑配置文件
    echo.
    pause
    exit /b 1
)

echo ✓ 找到 Privoxy 配置文件: %PRIVOXY_PATH%
echo.

echo [2] 备份原配置文件...
copy "%PRIVOXY_PATH%" "%PRIVOXY_PATH%.backup" >nul
echo ✓ 已备份到: %PRIVOXY_PATH%.backup
echo.

echo [3] 配置说明:
echo.
echo 请手动编辑配置文件: %PRIVOXY_PATH%
echo.
echo 需要修改的地方:
echo.
echo 1. 找到 listen-address 行（约第750行）
echo    确保是: listen-address  127.0.0.1:8118
echo.
echo 2. 找到 forward-socks5t 行（约第1300行）
echo    添加或修改为: forward-socks5t   /   127.0.0.1:1080 .
echo.
echo 3. 保存文件
echo.
echo 4. 重启 Privoxy 服务:
echo    - 打开 services.msc
echo    - 找到 Privoxy 服务
echo    - 右键 -^> 重启
echo.

echo [4] 配置 .env 文件...
echo.
echo 在 .env 文件中添加:
echo HTTPS_PROXY=http://127.0.0.1:8118
echo HTTP_PROXY=http://127.0.0.1:8118
echo.

echo 是否现在打开配置文件进行编辑? (Y/N)
set /p choice=
if /i "%choice%"=="Y" (
    notepad "%PRIVOXY_PATH%"
)

echo.
echo ========================================
echo 配置完成后，请:
echo 1. 重启 Privoxy 服务
echo 2. 更新 .env 文件
echo 3. 重启 Web 服务
echo ========================================
echo.
pause




