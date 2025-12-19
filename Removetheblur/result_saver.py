"""
结果保存模块 - Phase 5: 原子性结果保存
"""
import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image


class ResultSaver:
    """原子性结果保存器"""
    
    @staticmethod
    def save_image_atomic(
        image: Image.Image,
        output_path: str,
        quality: int = 95
    ) -> Tuple[bool, Optional[str], Optional[int], Optional[str]]:
        """
        Phase 5: 原子性保存图片（使用临时文件+验证+重命名）
        
        Args:
            image: PIL图片对象
            output_path: 最终输出路径
            quality: 图片质量
        
        Returns:
            (success, output_path, output_size, output_sha256)
        """
        try:
            output_file = Path(output_path)
            temp_path = output_file.with_suffix(output_file.suffix + '.tmp')
            
            # 1. 保存到临时文件
            if image.mode == 'RGBA':
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3])
                rgb_image.save(str(temp_path), quality=quality, optimize=True)
            else:
                image.save(str(temp_path), quality=quality, optimize=True)
            
            # 2. 验证文件存在且大小>0
            if not temp_path.exists():
                return False, None, None, None
            
            file_size = temp_path.stat().st_size
            if file_size <= 0:
                temp_path.unlink()  # 删除无效文件
                return False, None, None, None
            
            # 3. 计算output_sha256
            output_sha256 = ResultSaver._calculate_file_sha256(str(temp_path))
            
            # 4. 原子性重命名（.tmp -> 正式文件）
            try:
                temp_path.rename(output_path)
            except Exception as e:
                print(f"重命名失败: {e}")
                temp_path.unlink()  # 清理临时文件
                return False, None, None, None
            
            # 5. 验证最终文件
            final_path = Path(output_path)
            if not final_path.exists() or final_path.stat().st_size != file_size:
                return False, None, None, None
            
            return True, output_path, file_size, output_sha256
            
        except Exception as e:
            print(f"保存图片失败: {e}")
            # 清理可能的临时文件
            try:
                temp_path = Path(output_path).with_suffix(Path(output_path).suffix + '.tmp')
                if temp_path.exists():
                    temp_path.unlink()
            except:
                pass
            return False, None, None, None
    
    @staticmethod
    def _calculate_file_sha256(file_path: str) -> Optional[str]:
        """计算文件的SHA256哈希值"""
        try:
            if not os.path.exists(file_path):
                return None
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None

