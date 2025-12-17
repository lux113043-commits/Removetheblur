"""
检查 API Key 配置
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("API Key 配置检查")
print("=" * 60)

# 检查 .env 文件是否存在
env_path = ".env"
if os.path.exists(env_path):
    print(f"✓ .env 文件存在: {os.path.abspath(env_path)}")
    print(f"  文件大小: {os.path.getsize(env_path)} 字节")
else:
    print(f"✗ .env 文件不存在: {os.path.abspath(env_path)}")
    print("  请创建 .env 文件并添加 OPENAI_API_KEY=你的密钥")
    exit(1)

# 加载环境变量
load_dotenv()

# 检查 API Key
api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key:
    print("\n✗ OPENAI_API_KEY 未设置或为空")
    print("  请在 .env 文件中添加: OPENAI_API_KEY=你的密钥")
    exit(1)

# 显示 API Key 信息（部分隐藏）
if len(api_key) > 10:
    masked_key = api_key[:7] + "*" * (len(api_key) - 10) + api_key[-3:]
else:
    masked_key = "*" * len(api_key)

print(f"\n✓ OPENAI_API_KEY 已设置")
print(f"  密钥长度: {len(api_key)} 字符")
print(f"  密钥预览: {masked_key}")

# 检查常见问题
print("\n" + "=" * 60)
print("检查常见问题")
print("=" * 60)

# 检查是否有空格
if api_key != api_key.strip():
    print("⚠️  警告: API Key 前后可能有空格")
    print(f"  原始长度: {len(api_key)}")
    print(f"  去除空格后长度: {len(api_key.strip())}")

# 检查是否以 sk- 开头
if not api_key.startswith("sk-"):
    print("⚠️  警告: API Key 通常以 'sk-' 开头")
    print(f"  当前开头: {api_key[:5]}")

# 检查是否包含引号
if api_key.startswith('"') or api_key.startswith("'"):
    print("⚠️  警告: API Key 不应该包含引号")
    print("  正确格式: OPENAI_API_KEY=sk-...")
    print("  错误格式: OPENAI_API_KEY=\"sk-...\"")

# 检查长度
if len(api_key) < 20:
    print("⚠️  警告: API Key 长度似乎过短（通常 > 40 字符）")

# 读取 .env 文件内容（用于检查格式）
print("\n" + "=" * 60)
print(".env 文件内容（隐藏敏感信息）")
print("=" * 60)
try:
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            line = line.rstrip()
            if 'OPENAI_API_KEY' in line:
                # 隐藏 API Key
                if '=' in line:
                    key_part, value_part = line.split('=', 1)
                    if len(value_part) > 10:
                        masked_value = value_part[:7] + "*" * (len(value_part) - 10) + value_part[-3:]
                    else:
                        masked_value = "*" * len(value_part)
                    print(f"第 {i} 行: {key_part}={masked_value}")
                else:
                    print(f"第 {i} 行: {line}")
            else:
                print(f"第 {i} 行: {line}")
except Exception as e:
    print(f"读取 .env 文件时出错: {e}")

print("\n" + "=" * 60)
print("建议")
print("=" * 60)
print("1. 确保 .env 文件格式正确:")
print("   OPENAI_API_KEY=sk-你的完整密钥")
print("   不要加引号，不要有前后空格")
print("\n2. 如果修改了 .env 文件，需要重启 Web 服务")
print("\n3. 验证 API Key 是否有效:")
print("   访问 https://platform.openai.com/account/api-keys")
print("   确认密钥状态为 'Active'")


