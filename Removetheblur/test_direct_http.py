"""
直接使用 httpx 测试 API 调用
"""
import os
from dotenv import load_dotenv
import httpx
from PIL import Image
import io
import json

print("=" * 60)
print("直接 HTTP 请求测试")
print("=" * 60)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "")

if not api_key:
    print("✗ OPENAI_API_KEY 未设置")
    exit(1)

# 创建测试图片
print("\n创建测试图片...")
test_image = Image.new('RGB', (100, 100), color='red')
image_bytes = io.BytesIO()
test_image.save(image_bytes, format='PNG')
image_bytes.seek(0)

# 测试不同的端点
endpoints = [
    "https://api.qidianai.xyz/images/edits",
    "https://api.qidianai.xyz/v1/images/edits",
]

for endpoint in endpoints:
    print(f"\n{'='*60}")
    print(f"测试端点: {endpoint}")
    print(f"{'='*60}")
    
    try:
        timeout = httpx.Timeout(60.0, connect=10.0)
        client = httpx.Client(
            timeout=timeout,
            verify=False,
            follow_redirects=True
        )
        
        # 准备 multipart/form-data 请求
        image_bytes.seek(0)
        files = {
            'image': ('test.png', image_bytes, 'image/png'),
            'model': (None, 'gpt-image-1.5'),
            'prompt': (None, 'test'),
            'size': (None, '1024x1024'),
            'n': (None, '1'),
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'OpenAI/Python',
            'Content-Type': 'multipart/form-data',
        }
        
        print(f"  发送 POST 请求...")
        print(f"  Headers: Authorization: Bearer {api_key[:10]}...")
        
        try:
            response = client.post(endpoint, files=files, headers=headers, timeout=30.0)
            print(f"  ✓ 请求成功")
            print(f"  状态码: {response.status_code}")
            print(f"  响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  响应数据: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"  响应内容: {response.text[:200]}...")
            else:
                print(f"  响应内容: {response.text[:500]}")
                
        except httpx.RequestError as e:
            print(f"  ✗ 请求失败: {type(e).__name__}: {e}")
        except Exception as e:
            print(f"  ✗ 其他错误: {type(e).__name__}: {e}")
        
        client.close()
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

