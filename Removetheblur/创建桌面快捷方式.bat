@echo off
chcp 65001 >nul
echo ========================================
echo 创建桌面快捷方式
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_NAME=图片背景修复工具.lnk

echo 正在创建快捷方式到桌面...
echo.

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\%SHORTCUT_NAME%'); $Shortcut.TargetPath = '%SCRIPT_DIR%启动Web服务.bat'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = '图片背景修复工具 - Web服务'; $Shortcut.IconLocation = 'shell32.dll,137'; $Shortcut.Save(); Write-Host '快捷方式创建成功！'"

if errorlevel 1 (
    echo.
    echo 创建失败，尝试使用VBS方式...
    echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\create_shortcut.vbs"
    echo Set oShellLink = WshShell.CreateShortcut("%DESKTOP%\%SHORTCUT_NAME%") >> "%TEMP%\create_shortcut.vbs"
    echo oShellLink.TargetPath = "%SCRIPT_DIR%启动Web服务.bat" >> "%TEMP%\create_shortcut.vbs"
    echo oShellLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\create_shortcut.vbs"
    echo oShellLink.Description = "图片背景修复工具" >> "%TEMP%\create_shortcut.vbs"
    echo oShellLink.Save >> "%TEMP%\create_shortcut.vbs"
    cscript //nologo "%TEMP%\create_shortcut.vbs"
    del "%TEMP%\create_shortcut.vbs"
)

echo.
echo ========================================
echo 快捷方式已创建到桌面！
echo 文件名: %SHORTCUT_NAME%
echo ========================================
echo.
pause





