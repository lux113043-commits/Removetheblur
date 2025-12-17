"""
测试所有可能的 Midjourney API 路径
"""
import os
from dotenv import load_dotenv
import httpx
from PIL import Image
import io
import base64
import json

print("=" * 60)
print("测试所有可能的 Midjourney API 路径")
print("=" * 60)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "")

if not api_key:
    print("✗ OPENAI_API_KEY 未设置")
    exit(1)

# 创建测试图片
test_image = Image.new('RGB', (100, 100), color='red')
image_bytes = io.BytesIO()
test_image.save(image_bytes, format='PNG')
image_base64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')

api_base = "https://api.qidianai.xyz"
timeout = httpx.Timeout(10.0, connect=5.0)

# 测试所有可能的路径组合
paths = [
    # 标准格式
    "/mj/submit/imagine",
    "/api/mj/submit/imagine",
    "/v1/mj/submit/imagine",
    
    # 可能的变体
    "/midjourney/submit/imagine",
    "/api/midjourney/submit/imagine",
    "/v1/midjourney/submit/imagine",
    
    # 其他可能的格式
    "/submit/imagine",
    "/api/submit/imagine",
    "/imagine",
    "/api/imagine",
]

request_data = {
    "action": "IMAGINE",
    "prompt": "test",
    "base64Array": [image_base64],
}

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

print(f"\n测试基础连接...")
try:
    with httpx.Client(timeout=timeout, verify=False) as client:
        r = client.get(api_base)
        print(f"✓ 根路径可访问: {r.status_code}")
except Exception as e:
    print(f"✗ 根路径访问失败: {e}")

print(f"\n测试各个端点...")
for path in paths:
    url = f"{api_base}{path}"
    print(f"\n测试: {url}")
    
    try:
        with httpx.Client(timeout=timeout, verify=False) as client:
            # 先测试 OPTIONS
            try:
                opt_resp = client.options(url)
                print(f"  OPTIONS: {opt_resp.status_code}")
            except:
                pass
            
            # 测试 POST
            response = client.post(url, json=request_data, headers=headers)
            print(f"  ✓ POST成功: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ 端点可用!")
                try:
                    data = response.json()
                    print(f"  响应: {json.dumps(data, indent=2)[:200]}")
                except:
                    print(f"  响应文本: {response.text[:200]}")
                break
            else:
                print(f"  响应: {response.text[:200]}")
    except httpx.ConnectError as e:
        print(f"  ✗ 连接被拒绝")
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            print(f"  ⚠️  HTTP {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        print(f"  ✗ 错误: {type(e).__name__}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
print("\n如果所有端点都失败，可能的原因：")
print("1. API服务器不支持 Midjourney 格式接口")
print("2. 需要联系API提供商确认正确的端点路径")
print("3. 可能需要不同的认证方式或请求格式")


