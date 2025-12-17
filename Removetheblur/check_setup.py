"""
诊断脚本 - 检查环境配置是否正确
"""
import os
import sys
from pathlib import Path

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("环境诊断工具")
print("=" * 60)
print()

# 1. 检查Python版本
print("[1] 检查Python版本...")
print(f"    Python版本: {sys.version}")
print(f"    Python路径: {sys.executable}")
print()

# 2. 检查.env文件
print("[2] 检查.env文件...")
env_path = Path(".env")
if env_path.exists():
    print(f"    ✓ .env文件存在: {env_path.absolute()}")
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'OPENAI_API_KEY' in content:
            lines = content.split('\n')
            for line in lines:
                if line.startswith('OPENAI_API_KEY='):
                    key_value = line.split('=', 1)[1].strip()
                    if key_value and key_value != 'your_openai_api_key_here':
                        masked_key = key_value[:10] + '...' + key_value[-4:] if len(key_value) > 14 else '***'
                        print(f"    ✓ API Key已配置: {masked_key}")
                    else:
                        print(f"    ✗ API Key未正确配置（还是默认值）")
                        print(f"       请在.env文件中设置: OPENAI_API_KEY=你的实际密钥")
                    break
        else:
            print(f"    ✗ .env文件中没有找到OPENAI_API_KEY")
else:
    print(f"    ✗ .env文件不存在")
    print(f"       请创建.env文件并设置OPENAI_API_KEY")
print()

# 3. 检查依赖包
print("[3] 检查依赖包...")
required_packages = {
    'openai': 'openai',
    'PIL': 'pillow',
    'dotenv': 'python-dotenv',
    'numpy': 'numpy',
    'flask': 'flask'
}

missing_packages = []
for module_name, package_name in required_packages.items():
    try:
        __import__(module_name)
        print(f"    ✓ {package_name} 已安装")
    except ImportError:
        print(f"    ✗ {package_name} 未安装")
        missing_packages.append(package_name)

if missing_packages:
    print(f"\n    缺少以下包: {', '.join(missing_packages)}")
    print(f"    请运行: pip install {' '.join(missing_packages)}")
else:
    print(f"    ✓ 所有依赖包已安装")
print()

# 4. 检查API Key配置
print("[4] 检查API Key配置...")
try:
    from config import OPENAI_API_KEY
    if OPENAI_API_KEY:
        if OPENAI_API_KEY == "your_openai_api_key_here":
            print(f"    ✗ API Key还是默认值，请在.env文件中设置实际密钥")
        else:
            masked_key = OPENAI_API_KEY[:10] + '...' + OPENAI_API_KEY[-4:] if len(OPENAI_API_KEY) > 14 else '***'
            print(f"    ✓ API Key已加载: {masked_key}")
            
            # 尝试初始化OpenAI客户端
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)
                print(f"    ✓ OpenAI客户端初始化成功")
            except Exception as e:
                print(f"    ✗ OpenAI客户端初始化失败: {e}")
    else:
        print(f"    ✗ API Key未配置")
except Exception as e:
    print(f"    ✗ 加载配置失败: {e}")
print()

# 5. 检查测试图片文件夹
print("[5] 检查图片文件夹路径...")
test_path = "D:\\100_200ceshitupian\\100_110"
if os.path.exists(test_path):
    print(f"    ✓ 测试路径存在: {test_path}")
    if os.path.isdir(test_path):
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        image_files = [f for f in Path(test_path).iterdir() 
                      if f.suffix.lower() in image_extensions and f.is_file()]
        print(f"    ✓ 找到 {len(image_files)} 张图片")
        if image_files:
            print(f"    示例文件: {image_files[0].name}")
    else:
        print(f"    ✗ 路径不是文件夹")
else:
    print(f"    ✗ 测试路径不存在: {test_path}")
print()

# 6. 总结
print("=" * 60)
print("诊断完成")
print("=" * 60)
print()

if missing_packages:
    print("⚠️  请先安装缺失的依赖包")
    print()
    
if not env_path.exists() or not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
    print("⚠️  请配置API Key:")
    print("   1. 打开 .env 文件")
    print("   2. 设置 OPENAI_API_KEY=你的实际密钥")
    print()

print("如果所有检查都通过，但处理仍然失败，请查看运行web_app.py的控制台输出")
print("那里会有详细的错误信息。")

