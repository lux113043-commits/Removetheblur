# PowerShell 安装脚本
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装依赖包" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 升级pip
Write-Host "[1/3] 升级pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --no-warn-script-location
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: pip升级失败，继续安装依赖..." -ForegroundColor Yellow
}
Write-Host ""

# 安装依赖（使用清华镜像）
Write-Host "[2/3] 安装依赖包（使用清华镜像源）..." -ForegroundColor Yellow
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-warn-script-location

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "使用镜像源失败，尝试使用官方源..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt --no-warn-script-location
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "安装失败！" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "请检查：" -ForegroundColor Yellow
        Write-Host "1. Python是否正确安装" -ForegroundColor Yellow
        Write-Host "2. 网络连接是否正常" -ForegroundColor Yellow
        Write-Host "3. 是否有防火墙阻止" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "可以尝试手动安装：" -ForegroundColor Yellow
        Write-Host "pip install openai pillow python-dotenv numpy flask" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
}
Write-Host ""

# 验证安装
Write-Host "[3/3] 验证安装..." -ForegroundColor Yellow
python -c "import openai; import PIL; import flask; import numpy; print('所有依赖安装成功！')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 部分依赖可能未正确安装" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "安装完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}
Write-Host ""
Read-Host "按Enter键退出"





