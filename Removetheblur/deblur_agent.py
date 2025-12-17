"""
背景去模糊Agent主模块 - 使用AI处理
直接使用目标尺寸处理，不再切分
"""
from PIL import Image
from typing import Optional, Tuple
from image_utils import (
    load_image, save_image, resize_image_smart
)
from gpt_handler import GPTHandler
from config import OUTPUT_QUALITY


class DeblurAgent:
    """背景去模糊Agent - 使用AI将图片变清晰"""
    
    def __init__(self):
        self.gpt_handler = GPTHandler()
    
    def process_image(self, input_path: str, output_path: str,
                     target_size: Tuple[int, int] = (1024, 1536),
                     prompt: Optional[str] = None) -> dict:
        """
        使用AI处理图片，将模糊背景变清晰
        直接使用目标尺寸处理，不再切分
        
        Args:
            input_path: 输入图片路径（必需）
            output_path: 输出图片路径
            target_size: 目标尺寸 (width, height)，默认1024×1536
            prompt: 提示词（可选），为空则使用默认提示词
        
        Returns:
            处理结果字典
        """
        try:
            if not input_path:
                return {
                    "success": False,
                    "error": "图像编辑需要提供输入图片路径"
                }
            
            # 1. 加载图片
            print(f"正在加载图片: {input_path}")
            image = load_image(input_path)
            original_size = image.size
            print(f"原始尺寸: {original_size[0]}x{original_size[1]}")
            print(f"目标尺寸: {target_size[0]}x{target_size[1]}")
            
            # 2. 直接使用目标尺寸处理（不再切分）
            print("\n" + "=" * 60)
            print("使用OpenAI Images API直接编辑图片")
            print(f"目标尺寸: {target_size[0]}×{target_size[1]}")
            if prompt and prompt.strip():
                print(f"使用提示词: {prompt.strip()}")
            else:
                print(f"使用默认提示词: {self.gpt_handler.FIXED_PROMPT}")
            print("=" * 60)
            
            clear_image = self.gpt_handler.edit_image(image, target_size=target_size, prompt=prompt)
            
            if clear_image is None:
                return {
                    "success": False,
                    "error": "AI处理失败，未能生成清晰图片"
                }
            
            # 4. 保存结果
            print(f"\n正在保存结果到: {output_path}")
            save_image(clear_image, output_path, quality=OUTPUT_QUALITY)
            
            return {
                "success": True,
                "original_size": original_size,
                "final_size": clear_image.size,
                "output_path": output_path
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

