"""
测试所有可能的API端点
"""
import os
from dotenv import load_dotenv
import httpx
from PIL import Image
import io

print("=" * 60)
print("测试所有可能的API端点")
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

# 测试所有可能的端点
endpoints = [
    "/images/edits",
    "/v1/images/edits",
    "/api/images/edits",
    "/api/v1/images/edits",
    "/image/edit",
    "/v1/image/edit",
    "/edit",
    "/v1/edit",
]

api_base = "https://api.qidianai.xyz"
timeout = httpx.Timeout(10.0, connect=5.0)

print(f"\n测试基础连接...")
try:
    with httpx.Client(timeout=timeout, verify=False) as client:
        # 先测试根路径
        response = client.get(api_base)
        print(f"✓ 根路径可访问: {response.status_code}")
        print(f"  响应内容: {response.text[:200]}")
except Exception as e:
    print(f"✗ 根路径访问失败: {e}")

print(f"\n测试各个端点...")
for endpoint in endpoints:
    url = f"{api_base}{endpoint}"
    print(f"\n测试: {url}")
    
    try:
        image_bytes.seek(0)
        with httpx.Client(timeout=timeout, verify=False) as client:
            # 先测试OPTIONS请求
            try:
                options_response = client.options(url)
                print(f"  OPTIONS: {options_response.status_code}")
            except:
                pass
            
            # 测试POST请求
            files = {
                'image': ('image.png', image_bytes, 'image/png'),
                'model': (None, 'gpt-image-1'),
                'prompt': (None, 'test'),
                'size': (None, '1024x1024'),
            }
            headers = {
                'Authorization': f'Bearer {api_key}',
            }
            
            response = client.post(url, files=files, headers=headers)
            print(f"  ✓ POST请求成功: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ 端点可用!")
                print(f"  响应: {response.text[:200]}")
                break
            else:
                print(f"  响应: {response.text[:200]}")
    except httpx.ConnectError as e:
        print(f"  ✗ 连接被拒绝")
    except httpx.HTTPStatusError as e:
        print(f"  ⚠️  HTTP错误: {e.response.status_code}")
        if e.response.status_code != 404:
            print(f"  响应: {e.response.text[:200]}")
    except Exception as e:
        print(f"  ✗ 错误: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)


