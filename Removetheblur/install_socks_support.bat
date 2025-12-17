@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo 安装SOCKS代理支持
echo ========================================
echo.
echo 正在安装必要的依赖...
echo.

echo [1/3] 安装基础依赖 pysocks...
python -m pip install pysocks -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo 使用官方源重试...
    python -m pip install pysocks
    if errorlevel 1 (
        echo.
        echo ========================================
        echo 安装 pysocks 失败！
        echo ========================================
        pause
        exit /b 1
    )
)

echo.
echo [2/3] 安装 python-socks...
python -m pip install python-socks -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo 使用官方源重试...
    python -m pip install python-socks
    if errorlevel 1 (
        echo.
        echo ========================================
        echo 安装 python-socks 失败！
        echo ========================================
        pause
        exit /b 1
    )
)

echo.
echo [3/3] 安装 httpx-socks...
python -m pip install httpx-socks -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo 使用官方源重试...
    python -m pip install httpx-socks
    if errorlevel 1 (
        echo.
        echo ========================================
        echo 安装 httpx-socks 失败！
        echo ========================================
        echo 请检查网络连接，或手动运行：
        echo pip install python-socks[asyncio]
        echo pip install httpx-socks
        echo ========================================
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 安装成功！
echo ========================================
echo.
echo 现在可以在 .env 文件中配置SOCKS5代理：
echo ALL_PROXY=socks5://127.0.0.1:1080
echo.
pause

