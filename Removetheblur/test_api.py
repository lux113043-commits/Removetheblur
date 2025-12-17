"""
测试脚本 - 直接测试API调用和图片处理
"""
import sys
import os
from pathlib import Path

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("API和图片处理测试")
print("=" * 60)
print()

# 1. 检查配置
print("[1] 检查配置...")
try:
    from config import OPENAI_API_KEY
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        print("✗ API Key未配置")
        sys.exit(1)
    print(f"✓ API Key已配置: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}")
except Exception as e:
    print(f"✗ 配置加载失败: {e}")
    sys.exit(1)

# 2. 测试OpenAI客户端初始化
print()
print("[2] 测试OpenAI客户端初始化...")
try:
    from gpt_handler import GPTHandler
    handler = GPTHandler()
    print("✓ GPTHandler初始化成功")
except Exception as e:
    print(f"✗ GPTHandler初始化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试图片加载
print()
print("[3] 测试图片加载...")
test_folder = "D:\\100_200ceshitupian\\100_110"
if not os.path.exists(test_folder):
    print(f"✗ 测试文件夹不存在: {test_folder}")
    sys.exit(1)

image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
image_files = [f for f in Path(test_folder).iterdir() 
              if f.suffix.lower() in image_extensions and f.is_file()]

if not image_files:
    print(f"✗ 测试文件夹中没有图片文件")
    sys.exit(1)

test_image = image_files[0]
print(f"✓ 找到测试图片: {test_image.name}")

try:
    from PIL import Image
    img = Image.open(test_image)
    print(f"✓ 图片加载成功，尺寸: {img.size}")
except Exception as e:
    print(f"✗ 图片加载失败: {e}")
    sys.exit(1)

# 4. 测试图片准备
print()
print("[4] 测试图片准备（调整尺寸）...")
try:
    from image_utils import resize_image_smart
    resized = resize_image_smart(img, (1024, 1024), method='lanczos')
    print(f"✓ 图片调整成功，新尺寸: {resized.size}")
except Exception as e:
    print(f"✗ 图片调整失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. 测试API调用（只测试第一张切分图片）
print()
print("[5] 测试API调用...")
print("注意: 这将实际调用OpenAI API，会产生费用")
print("正在切分图片为1024x1024...")

try:
    from image_utils import split_image_vertical
    split_images = split_image_vertical(img, target_width=1024)
    print(f"✓ 图片切分成功，得到 {len(split_images)} 张")
    
    if len(split_images) > 0:
        test_split = split_images[0]
        print(f"测试第一张切分图片，尺寸: {test_split.size}")
        
        print()
        print("正在调用OpenAI API编辑图片...")
        print("这可能需要30-60秒...")
        
        edited = handler.edit_image(test_split, target_size=(1024, 1024))
        
        if edited:
            print(f"✓ API调用成功！")
            print(f"✓ 返回图片尺寸: {edited.size}")
            
            # 保存测试结果
            output_path = Path("test_output.jpg")
            edited.save(output_path, "JPEG", quality=95)
            print(f"✓ 测试结果已保存到: {output_path.absolute()}")
        else:
            print("✗ API调用失败，返回None")
            sys.exit(1)
    else:
        print("✗ 图片切分失败，没有得到切分图片")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ API调用失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("✓ 所有测试通过！")
print("=" * 60)
print()
print("如果这个测试成功，说明API配置和调用都没问题")
print("问题可能出在Web应用的图片处理流程中")




