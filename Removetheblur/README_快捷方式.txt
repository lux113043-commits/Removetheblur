========================================
创建桌面快捷方式 - 手动方法
========================================

如果自动创建失败，请按以下步骤手动创建：

【方法1：拖拽创建（最简单）】

1. 找到项目文件夹中的 "快速启动.bat" 文件
2. 右键点击该文件
3. 选择"发送到" -> "桌面快捷方式"
4. 完成！

【方法2：右键创建】

1. 在桌面空白处右键
2. 选择"新建" -> "快捷方式"
3. 在"位置"中输入：
   D:\Removetheblur\快速启动.bat
   （请替换为你的实际路径）
4. 点击"下一步"
5. 输入名称：图片背景修复工具
6. 点击"完成"

【方法3：使用PowerShell命令】

打开PowerShell，执行：
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\图片背景修复工具.lnk")
$Shortcut.TargetPath = "D:\Removetheblur\快速启动.bat"
$Shortcut.WorkingDirectory = "D:\Removetheblur"
$Shortcut.Description = "图片背景修复工具"
$Shortcut.Save()

（请将路径替换为你的实际路径）

========================================
使用说明
========================================

1. 双击桌面快捷方式启动服务
2. 浏览器会自动打开 http://localhost:5000
3. 如果浏览器没有自动打开，请手动访问该地址

========================================





