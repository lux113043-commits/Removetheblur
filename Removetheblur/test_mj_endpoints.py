"""
测试 Midjourney API 端点
"""
import os
from dotenv import load_dotenv
import httpx
from PIL import Image
import io
import base64
import json

print("=" * 60)
print("测试 Midjourney API 端点")
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
image_bytes.seek(0)

# 转换为 base64
image_base64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')

api_base = "https://api.qidianai.xyz"
timeout = httpx.Timeout(30.0, connect=10.0)

# 测试不同的端点
endpoints = [
    "/mj/submit/imagine",
    "/api/mj/submit/imagine",
    "/v1/mj/submit/imagine",
    "/midjourney/submit/imagine",
]

request_data = {
    "action": "IMAGINE",
    "prompt": "test prompt",
    "base64Array": [image_base64],
}

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

for endpoint in endpoints:
    url = f"{api_base}{endpoint}"
    print(f"\n{'='*60}")
    print(f"测试端点: {url}")
    print(f"{'='*60}")
    
    try:
        with httpx.Client(
            timeout=timeout,
            verify=False,
            follow_redirects=True
        ) as client:
            print(f"  发送 POST 请求...")
            response = client.post(url, json=request_data, headers=headers)
            
            print(f"  ✓ 请求成功")
            print(f"  状态码: {response.status_code}")
            print(f"  响应: {response.text[:300]}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  ✓ API调用成功!")
                    print(f"  响应数据: {json.dumps(data, indent=2)[:300]}")
                    break
                except:
                    pass
    except httpx.ConnectError as e:
        print(f"  ✗ 连接被拒绝: {e}")
    except httpx.RequestError as e:
        print(f"  ✗ 请求错误: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"  ✗ 其他错误: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)


