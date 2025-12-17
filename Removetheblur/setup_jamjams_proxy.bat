@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo JamJams 代理配置助手
echo ========================================
echo.

echo JamJams 默认使用 SOCKS5 代理 (socks5://127.0.0.1:1080)
echo 但 OpenAI 客户端不支持 SOCKS 代理，需要 HTTP 代理
echo.

echo 解决方案：
echo.
echo [方案1] 如果 JamJams 支持 HTTP 代理模式：
echo   1. 在 JamJams 中查找 HTTP 代理设置
echo   2. 启用 HTTP 代理模式
echo   3. 记下 HTTP 代理端口（通常是 7890 或其他）
echo   4. 在 .env 文件中配置：
echo      HTTPS_PROXY=http://127.0.0.1:7890
echo      HTTP_PROXY=http://127.0.0.1:7890
echo.

echo [方案2] 使用 Privoxy 转换 SOCKS 为 HTTP（推荐）：
echo   1. 下载 Privoxy: https://www.privoxy.org/
echo   2. 安装并配置 Privoxy 监听 HTTP 端口（如 8118）
echo   3. 配置 Privoxy 转发到 SOCKS5://127.0.0.1:1080
echo   4. 在 .env 文件中配置：
echo      HTTPS_PROXY=http://127.0.0.1:8118
echo      HTTP_PROXY=http://127.0.0.1:8118
echo.

echo [方案3] 使用 Python 的 requests 库（临时方案）：
echo   需要修改代码以支持 SOCKS 代理
echo.

echo ========================================
echo 当前代理设置检查
echo ========================================
echo.

if defined HTTPS_PROXY (
    echo HTTPS_PROXY = %HTTPS_PROXY%
) else (
    echo HTTPS_PROXY = (未设置)
)

if defined HTTP_PROXY (
    echo HTTP_PROXY = %HTTP_PROXY%
) else (
    echo HTTP_PROXY = (未设置)
)

echo.
echo ========================================
echo 建议操作步骤
echo ========================================
echo.
echo 1. 检查 JamJams 是否有 HTTP 代理模式
echo 2. 如果有，启用并配置 HTTP 代理端口
echo 3. 在 .env 文件中添加代理配置
echo 4. 重启 Web 服务
echo.
echo 如果 JamJams 不支持 HTTP 模式，请使用 Privoxy 转换
echo.
pause




