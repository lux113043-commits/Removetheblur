"""
测试实际的 API 调用
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import httpx
from PIL import Image
import io

print("=" * 60)
print("测试实际 API 调用")
print("=" * 60)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY", "")

if not api_key:
    print("✗ OPENAI_API_KEY 未设置")
    exit(1)

# 创建一个小的测试图片
print("\n创建测试图片...")
test_image = Image.new('RGB', (100, 100), color='red')
image_bytes = io.BytesIO()
test_image.save(image_bytes, format='PNG')
image_bytes.seek(0)

# 测试不同的 base_url 配置
base_urls = [
    ("https://api.qidianai.xyz", "不带 /v1"),
    ("https://api.qidianai.xyz/v1", "带 /v1"),
]

for base_url, desc in base_urls:
    print(f"\n{'='*60}")
    print(f"测试配置: {base_url} ({desc})")
    print(f"{'='*60}")
    
    try:
        timeout = httpx.Timeout(60.0, connect=10.0)
        http_client = httpx.Client(
            timeout=timeout,
            verify=False,
            follow_redirects=True
        )
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            http_client=http_client,
            max_retries=0
        )
        
        print(f"✓ 客户端创建成功")
        print(f"  实际请求URL应该是: {base_url}/images/edits")
        
        # 保存图片到临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as tmp_file:
            tmp_file.write(image_bytes.getvalue())
            tmp_file_path = tmp_file.name
        
        try:
            print(f"  正在调用 images.edit API...")
            with open(tmp_file_path, 'rb') as image_file:
                response = client.images.edit(
                    model="gpt-image-1.5",
                    image=image_file,
                    prompt="test",
                    size="1024x1024",
                    n=1
                )
            print(f"  ✓ API 调用成功!")
            print(f"  响应类型: {type(response)}")
            if hasattr(response, 'data') and response.data:
                print(f"  返回数据数量: {len(response.data)}")
        except Exception as api_error:
            error_str = str(api_error)
            print(f"  ✗ API 调用失败: {type(api_error).__name__}")
            print(f"  错误信息: {api_error}")
            
            # 检查是否是 404 错误
            if "404" in error_str or "not found" in error_str.lower():
                print(f"  ⚠️  端点不存在 (404)，可能需要不同的 base_url")
            elif "401" in error_str or "authentication" in error_str.lower():
                print(f"  ✓ 端点存在，需要认证（这是正常的）")
            elif "connection" in error_str.lower():
                print(f"  ✗ 连接错误")
        
        finally:
            import os
            try:
                os.unlink(tmp_file_path)
            except:
                pass
        
        http_client.close()
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)


