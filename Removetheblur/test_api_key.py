"""
直接测试 OpenAI API Key 是否有效
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

print("=" * 60)
print("测试 OpenAI API Key")
print("=" * 60)

# 加载环境变量
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY", "")
if not api_key:
    print("✗ OPENAI_API_KEY 未设置")
    exit(1)

# 显示部分密钥
masked_key = api_key[:7] + "*" * (len(api_key) - 10) + api_key[-3:]
print(f"API Key: {masked_key}")
print(f"长度: {len(api_key)} 字符")
print()

# 创建 OpenAI 客户端
print("正在创建 OpenAI 客户端...")
try:
    client = OpenAI(api_key=api_key)
    print("✓ 客户端创建成功")
except Exception as e:
    print(f"✗ 客户端创建失败: {e}")
    exit(1)

# 测试 1: 检查 API Key 权限（使用简单的 API 调用）
print("\n" + "=" * 60)
print("测试 1: 检查 API Key 权限")
print("=" * 60)

try:
    # 尝试列出模型（这是一个简单的权限检查）
    print("正在检查 API Key 权限...")
    models = client.models.list()
    print("✓ API Key 有效，可以访问 OpenAI API")
    print(f"  可用模型数量: {len(list(models.data))}")
except Exception as e:
    error_str = str(e).lower()
    if "401" in str(e) or "authentication" in error_str or "api key" in error_str:
        print(f"✗ API Key 无效或已过期")
        print(f"  错误: {e}")
        print("\n建议:")
        print("1. 访问 https://platform.openai.com/account/api-keys")
        print("2. 检查密钥状态是否为 'Active'")
        print("3. 如果密钥已删除，请创建新密钥")
        print("4. 确保密钥有足够的余额")
    else:
        print(f"⚠️  其他错误: {e}")
    exit(1)

# 测试 2: 检查是否可以访问 gpt-image-1.5 模型
print("\n" + "=" * 60)
print("测试 2: 检查 gpt-image-1.5 模型访问权限")
print("=" * 60)

try:
    # 尝试获取模型信息
    print("正在检查 gpt-image-1.5 模型...")
    model = client.models.retrieve("gpt-image-1.5")
    print(f"✓ 可以访问 gpt-image-1.5 模型")
    print(f"  模型ID: {model.id}")
    if hasattr(model, 'owned_by'):
        print(f"  所有者: {model.owned_by}")
except Exception as e:
    error_str = str(e).lower()
    if "404" in str(e) or "not found" in error_str:
        print(f"⚠️  gpt-image-1.5 模型未找到")
        print("  这可能意味着:")
        print("  1. 模型名称不正确")
        print("  2. 您的账户没有访问该模型的权限")
        print("  3. 需要验证组织（Organization Verification）")
    elif "401" in str(e) or "authentication" in error_str:
        print(f"✗ 认证失败: {e}")
    elif "403" in str(e) or "permission" in error_str:
        print(f"⚠️  权限不足: {e}")
        print("  可能需要:")
        print("  1. 验证组织: https://platform.openai.com/settings/organization/general")
        print("  2. 检查账户是否有访问该模型的权限")
    else:
        print(f"⚠️  其他错误: {e}")

# 测试 3: 尝试一个简单的图片编辑请求（使用测试图片）
print("\n" + "=" * 60)
print("测试 3: 测试图片编辑 API（需要实际图片）")
print("=" * 60)
print("跳过此测试（需要实际图片文件）")
print("如果前两个测试通过，API Key 应该是有效的")

print("\n" + "=" * 60)
print("总结")
print("=" * 60)
print("如果所有测试通过，API Key 配置正确")
print("如果出现 401 错误，请检查:")
print("  1. API Key 是否正确复制（没有多余空格）")
print("  2. API Key 是否在 OpenAI 平台上是 'Active' 状态")
print("  3. 账户是否有足够的余额")
print("  4. 是否重启了 Web 服务（修改 .env 后需要重启）")


