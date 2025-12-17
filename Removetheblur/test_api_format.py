"""
测试不同的API请求格式
"""
import os
from dotenv import load_dotenv
import httpx
from PIL import Image
import io
import base64
import json

print("=" * 60)
print("测试不同的API请求格式")
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

# 测试不同的请求格式
test_configs = [
    {
        "name": "multipart/form-data (当前方式)",
        "endpoint": "/images/edits",
        "method": "POST",
        "files": {
            'image': ('image.png', image_bytes, 'image/png'),
            'model': (None, 'gpt-image-1'),
            'prompt': (None, 'test'),
            'size': (None, '1024x1024'),
            'n': (None, '1'),
        },
        "headers": {
            'Authorization': f'Bearer {api_key}',
        }
    },
    {
        "name": "JSON格式 (base64编码图片)",
        "endpoint": "/images/edits",
        "method": "POST",
        "json": {
            'model': 'gpt-image-1',
            'prompt': 'test',
            'size': '1024x1024',
            'n': 1,
            'image': base64.b64encode(image_bytes.getvalue()).decode('utf-8')
        },
        "headers": {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
    },
    {
        "name": "multipart/form-data (v1端点)",
        "endpoint": "/v1/images/edits",
        "method": "POST",
        "files": {
            'image': ('image.png', image_bytes, 'image/png'),
            'model': (None, 'gpt-image-1'),
            'prompt': (None, 'test'),
            'size': (None, '1024x1024'),
            'n': (None, '1'),
        },
        "headers": {
            'Authorization': f'Bearer {api_key}',
        }
    },
]

api_base = "https://api.qidianai.xyz"
timeout = httpx.Timeout(30.0, connect=10.0)

for config in test_configs:
    print(f"\n{'='*60}")
    print(f"测试: {config['name']}")
    print(f"端点: {api_base}{config['endpoint']}")
    print(f"{'='*60}")
    
    try:
        image_bytes.seek(0)  # 重置图片流
        
        with httpx.Client(
            timeout=timeout,
            verify=False,
            follow_redirects=True
        ) as client:
            url = f"{api_base}{config['endpoint']}"
            
            # 根据配置发送请求
            if 'files' in config:
                print(f"  发送 multipart/form-data 请求...")
                response = client.post(url, files=config['files'], headers=config['headers'])
            elif 'json' in config:
                print(f"  发送 JSON 请求...")
                response = client.post(url, json=config['json'], headers=config['headers'])
            else:
                print(f"  未知的请求格式")
                continue
            
            print(f"  ✓ 请求成功")
            print(f"  状态码: {response.status_code}")
            print(f"  响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                print(f"  ✓ API调用成功!")
                try:
                    data = response.json()
                    print(f"  响应数据: {json.dumps(data, indent=2)[:300]}...")
                except:
                    print(f"  响应内容: {response.text[:300]}...")
            else:
                print(f"  ⚠️  状态码: {response.status_code}")
                print(f"  响应内容: {response.text[:300]}")
                
    except httpx.ConnectError as e:
        print(f"  ✗ 连接错误: {e}")
        print(f"  说明: 服务器拒绝连接，可能是端点不存在或请求格式不对")
    except httpx.RequestError as e:
        print(f"  ✗ 请求错误: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"  ✗ 其他错误: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
print("\n如果所有测试都失败，可能需要：")
print("1. 确认API文档，了解正确的请求格式")
print("2. 检查API是否需要不同的认证方式")
print("3. 确认API端点路径是否正确")


