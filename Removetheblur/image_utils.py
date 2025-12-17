"""
图片处理工具函数
只使用 Pillow + numpy
"""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from typing import Tuple, Optional, List
import io
import base64


def load_image(image_path: str) -> Image.Image:
    """加载图片"""
    return Image.open(image_path)


def save_image(image: Image.Image, output_path: str, quality: int = 95):
    """保存图片"""
    if image.mode == 'RGBA':
        # 如果是RGBA模式，转换为RGB
        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[3])
        rgb_image.save(output_path, quality=quality, optimize=True)
    else:
        image.save(output_path, quality=quality, optimize=True)


def resize_image_smart(image: Image.Image, target_size: Tuple[int, int], 
                       method: str = 'lanczos') -> Image.Image:
    """
    智能调整图片尺寸（类似PS智能对象放大）
    
    Args:
        image: PIL图片对象
        target_size: 目标尺寸 (width, height)
        method: 重采样方法 ('lanczos', 'bicubic', 'nearest')
    
    Returns:
        调整后的图片
    """
    resample_map = {
        'lanczos': Image.Resampling.LANCZOS,
        'bicubic': Image.Resampling.BICUBIC,
        'nearest': Image.Resampling.NEAREST
    }
    
    resample = resample_map.get(method, Image.Resampling.LANCZOS)
    return image.resize(target_size, resample=resample)


def enhance_image_sharpness(image: Image.Image, factor: float = 1.5) -> Image.Image:
    """增强图片锐度"""
    enhancer = ImageEnhance.Sharpness(image)
    return enhancer.enhance(factor)


def split_image_vertical(image: Image.Image, target_width: int = 1024) -> List[Image.Image]:
    """
    将竖图切分成两张（上/下），每张尺寸为 target_width × target_width
    
    Args:
        image: 原始图片
        target_width: 目标宽度（默认1024）
    
    Returns:
        两张图片的列表 [上半部分, 下半部分]
    """
    # 转换为RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # 调整图片宽度到target_width
    original_width, original_height = image.size
    scale = target_width / original_width
    new_height = int(original_height * scale)
    
    resized_image = resize_image_smart(image, (target_width, new_height), method='lanczos')
    
    # 如果高度小于等于target_width，只需要一张图
    if new_height <= target_width:
        # 填充到target_width高度
        padded_image = Image.new('RGB', (target_width, target_width), (255, 255, 255))
        padded_image.paste(resized_image, (0, 0))
        return [padded_image]
    
    # 切分成两张：上半部分和下半部分
    # 上半部分：从顶部开始，高度为target_width
    top_part = resized_image.crop((0, 0, target_width, target_width))
    
    # 下半部分：从底部开始，高度为target_width
    # 如果有重叠，从 new_height - target_width 开始
    bottom_start = max(0, new_height - target_width)
    bottom_part = resized_image.crop((0, bottom_start, target_width, new_height))
    
    return [top_part, bottom_part]


def merge_images_vertical(images: List[Image.Image], target_size: Tuple[int, int]) -> Image.Image:
    """
    将两张图片无缝拼接成目标尺寸（1024×1536）
    使用渐变融合实现无缝拼接
    
    Args:
        images: 图片列表（应该有两张 1024×1024 的图片）
        target_size: 目标尺寸 (width, height)，如 (1024, 1536)
    
    Returns:
        拼接后的图片
    """
    if len(images) == 1:
        # 如果只有一张图，直接调整尺寸
        return resize_image_smart(images[0], target_size, method='lanczos')
    
    if len(images) != 2:
        raise ValueError(f"需要1或2张图片，但提供了{len(images)}张")
    
    top_image, bottom_image = images[0], images[1]
    
    # 确保两张图片都是1024×1024
    if top_image.size != (1024, 1024):
        top_image = resize_image_smart(top_image, (1024, 1024), method='lanczos')
    if bottom_image.size != (1024, 1024):
        bottom_image = resize_image_smart(bottom_image, (1024, 1024), method='lanczos')
    
    # 转换为numpy数组
    top_array = np.array(top_image)
    bottom_array = np.array(bottom_image)
    
    target_width, target_height = target_size
    
    # 对于1024×1536：需要1024行 + 512行 = 1536行
    # 上半部分：使用top_image的全部1024行
    # 下半部分：使用bottom_image的后512行
    
    if target_size == (1024, 1536):
        # 创建结果数组
        result_array = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        
        # 上半部分：使用top_image的全部1024行
        result_array[:1024] = top_array[:1024]
        
        # 下半部分：使用bottom_image的后512行
        # 从bottom_image的第512行开始（1024 - 512 = 512）
        result_array[1024:] = bottom_array[512:]
        
        # 在拼接处进行渐变融合（可选，使拼接更自然）
        # 在1024行附近进行少量融合
        blend_width = 16  # 融合区域宽度
        for i in range(blend_width):
            alpha = i / blend_width  # 0到1的渐变
            y = 1024 - blend_width + i
            if 0 <= y < target_height:
                result_array[y] = (
                    top_array[y] * (1 - alpha) +
                    bottom_array[512 + i] * alpha
                ).astype(np.uint8)
        
        # 转换回PIL Image
        return Image.fromarray(result_array)
    else:
        # 其他尺寸：简单拼接
        result_array = np.vstack([top_array, bottom_array])
        result_image = Image.fromarray(result_array)
        # 调整到目标尺寸
        return resize_image_smart(result_image, target_size, method='lanczos')


def image_to_base64(image: Image.Image, format: str = 'PNG') -> str:
    """将PIL图片转换为base64字符串"""
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def base64_to_image(base64_str: str) -> Image.Image:
    """将base64字符串转换为PIL图片"""
    img_data = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(img_data))



