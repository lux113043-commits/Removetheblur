"""
测试 API 端点配置
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import httpx

print("=" * 60)
print("测试 API 端点配置")
print("=" * 60)

# 加载环境变量
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "")

if not api_key:
    print("✗ OPENAI_API_KEY 未设置")
    exit(1)

# 测试不同的 base_url 配置
base_urls = [
    "https://api.qidianai.xyz",
    "https://api.qidianai.xyz/v1",
    "https://api.qidianai.xyz/v1/",
]

print(f"\nAPI Key: {api_key[:10]}...{api_key[-4:]}")
print(f"\n测试不同的 base_url 配置:")
print("=" * 60)

for base_url in base_urls:
    print(f"\n测试 base_url: {base_url}")
    try:
        # 创建超时配置
        timeout = httpx.Timeout(30.0, connect=10.0)
        http_client = httpx.Client(
            timeout=timeout,
            verify=False,
            follow_redirects=True
        )
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client,
            max_retries=0  # 不重试，快速失败
        )
        
        print(f"  ✓ 客户端创建成功")
        
        # 尝试列出模型（轻量级请求，测试端点是否可用）
        try:
            print(f"  正在测试端点连接...")
            # 注意：这个调用可能会失败，但我们可以从错误信息中判断端点是否正确
            models = client.models.list()
            print(f"  ✓ 端点可用，可以列出模型")
        except Exception as e:
            error_str = str(e).lower()
            if "404" in str(e) or "not found" in error_str:
                print(f"  ⚠️  端点返回 404，可能路径不正确")
            elif "401" in str(e) or "authentication" in error_str:
                print(f"  ✓ 端点可访问（需要认证，这是正常的）")
            elif "connection" in error_str:
                print(f"  ✗ 连接失败: {e}")
            else:
                print(f"  ⚠️  其他错误: {type(e).__name__}: {e}")
        
        http_client.close()
        
    except Exception as e:
        print(f"  ✗ 客户端创建失败: {e}")

print("\n" + "=" * 60)
print("建议")
print("=" * 60)
print("如果所有 base_url 都失败，可能的原因：")
print("1. API 服务器不可访问")
print("2. API 端点路径与 OpenAI 标准不同")
print("3. 需要联系 API 提供商确认正确的端点配置")


