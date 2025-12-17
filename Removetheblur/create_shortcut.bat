@echo off
chcp 65001 >nul
echo ========================================
echo Creating Desktop Shortcut
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set DESKTOP=%USERPROFILE%\Desktop
set SHORTCUT_NAME=Image Background Fix Tool.lnk

echo Creating shortcut on desktop...
echo.

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\%SHORTCUT_NAME%'); $Shortcut.TargetPath = '%SCRIPT_DIR%启动Web服务.bat'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'Image Background Fix Tool - Web Service'; $Shortcut.IconLocation = 'shell32.dll,137'; $Shortcut.Save(); Write-Host 'Shortcut created successfully!'"

if errorlevel 1 (
    echo.
    echo Trying VBS method...
    echo Set WshShell = CreateObject("WScript.Shell") > "%TEMP%\create_shortcut.vbs"
    echo Set oShellLink = WshShell.CreateShortcut("%DESKTOP%\%SHORTCUT_NAME%") >> "%TEMP%\create_shortcut.vbs"
    echo oShellLink.TargetPath = "%SCRIPT_DIR%启动Web服务.bat" >> "%TEMP%\create_shortcut.vbs"
    echo oShellLink.WorkingDirectory = "%SCRIPT_DIR%" >> "%TEMP%\create_shortcut.vbs"
    echo oShellLink.Description = "Image Background Fix Tool" >> "%TEMP%\create_shortcut.vbs"
    echo oShellLink.Save >> "%TEMP%\create_shortcut.vbs"
    cscript //nologo "%TEMP%\create_shortcut.vbs"
    del "%TEMP%\create_shortcut.vbs"
)

echo.
echo ========================================
echo Shortcut created on desktop!
echo File name: %SHORTCUT_NAME%
echo ========================================
echo.
pause





