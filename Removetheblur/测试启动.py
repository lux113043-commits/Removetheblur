"""
测试Web服务是否能正常启动
"""
import sys

print("=" * 60)
print("检查依赖...")
print("=" * 60)

# 检查依赖
dependencies = {
    'flask': 'Flask',
    'openai': 'OpenAI',
    'PIL': 'Pillow',
    'numpy': 'NumPy',
    'dotenv': 'python-dotenv'
}

missing = []
for module, name in dependencies.items():
    try:
        __import__(module)
        print(f"✓ {name} - 已安装")
    except ImportError:
        print(f"✗ {name} - 未安装")
        missing.append(name)

if missing:
    print("\n" + "=" * 60)
    print("缺少以下依赖:")
    for dep in missing:
        print(f"  - {dep}")
    print("\n请运行 install.bat 安装依赖")
    print("=" * 60)
    sys.exit(1)

print("\n" + "=" * 60)
print("检查配置文件...")
print("=" * 60)

import os
from pathlib import Path

env_file = Path('.env')
if env_file.exists():
    print("✓ .env 文件存在")
    # 检查是否有API Key
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'OPENAI_API_KEY' in content and 'your_api_key' not in content:
            print("✓ API Key 已配置")
        else:
            print("⚠ API Key 未配置（不影响启动，但无法处理图片）")
else:
    print("⚠ .env 文件不存在（不影响启动，但无法处理图片）")
    if Path('env_example.txt').exists():
        print("  提示: 可以复制 env_example.txt 为 .env 并配置API Key")

print("\n" + "=" * 60)
print("测试导入Web应用...")
print("=" * 60)

try:
    from web_app import app
    print("✓ Web应用导入成功")
    print("\n" + "=" * 60)
    print("所有检查通过！")
    print("可以运行 启动Web服务.bat 启动服务")
    print("=" * 60)
except Exception as e:
    print(f"✗ Web应用导入失败: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("请检查错误信息并修复")
    print("=" * 60)
    sys.exit(1)





