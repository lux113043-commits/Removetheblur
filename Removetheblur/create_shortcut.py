"""
创建桌面快捷方式
"""
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path

# 设置控制台编码
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

try:
    import win32com.client  # type: ignore
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

def create_shortcut():
    """创建桌面快捷方式"""
    script_dir = Path(__file__).parent.absolute()
    desktop = Path.home() / "Desktop"
    shortcut_name = "图片背景修复工具.lnk"
    shortcut_path = desktop / shortcut_name
    
    target_bat = script_dir / "启动Web服务.bat"
    
    if not target_bat.exists():
        print(f"[ERROR] 找不到 {target_bat}")
        return False
    
    try:
        if HAS_WIN32:
            # 使用win32com
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(target_bat)
            shortcut.WorkingDirectory = str(script_dir)
            shortcut.Description = "图片背景修复工具 - Web服务"
            shortcut.IconLocation = "shell32.dll,137"
            shortcut.save()
            print(f"[OK] 快捷方式已创建: {shortcut_path}")
            return True
        else:
            # 使用VBS脚本
            vbs_script = f'''
Set WshShell = CreateObject("WScript.Shell")
Set oShellLink = WshShell.CreateShortcut("{shortcut_path}")
oShellLink.TargetPath = "{target_bat}"
oShellLink.WorkingDirectory = "{script_dir}"
oShellLink.Description = "图片背景修复工具"
oShellLink.IconLocation = "shell32.dll,137"
oShellLink.Save
'''
            vbs_file = script_dir / "temp_create_shortcut.vbs"
            vbs_file.write_text(vbs_script, encoding='utf-8')
            
            os.system(f'cscript //nologo "{vbs_file}"')
            vbs_file.unlink()
            
            if shortcut_path.exists():
                print(f"[OK] 快捷方式已创建: {shortcut_path}")
                return True
            else:
                print("[ERROR] 快捷方式创建失败")
                return False
    except Exception as e:
        print(f"[ERROR] 创建快捷方式时出错: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("创建桌面快捷方式")
    print("=" * 60)
    print()
    
    if create_shortcut():
        print()
        print("=" * 60)
        print("完成！现在可以在桌面找到快捷方式")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("创建失败，请手动创建快捷方式")
        print("=" * 60)
        print(f"目标文件: {Path(__file__).parent / '启动Web服务.bat'}")
        print("=" * 60)
    
    input("\n按Enter键退出...")

