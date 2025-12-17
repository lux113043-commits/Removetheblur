"""
配置文件
"""
import os
from dotenv import load_dotenv
import warnings

load_dotenv()

# OpenAI API配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# 图片处理配置
MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "2048"))
OUTPUT_QUALITY = int(os.getenv("OUTPUT_QUALITY", "95"))

# 验证配置（只警告，不阻止启动）
if not OPENAI_API_KEY:
    warnings.warn(
        "未配置OPENAI_API_KEY，Web服务可以启动，但无法处理图片。"
        "请在.env文件中设置OPENAI_API_KEY。",
        UserWarning
    )

