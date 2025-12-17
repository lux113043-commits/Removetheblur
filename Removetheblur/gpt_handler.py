"""
API处理模块 - 使用AI将图片变清晰
使用 New API OpenAI 格式接口
参考文档: https://doc.newapi.pro/api/openai-image/
"""
from PIL import Image
from typing import Optional, Tuple
from config import OPENAI_API_KEY
import io
import base64
import httpx
import json
import time
import tempfile
import os


class GPTHandler:
    """API处理器 - 使用AI编辑图片"""
    
    # 固定的系统提示词（中文）
    FIXED_PROMPT = "请把这个图变成全景深，整个画面中模糊虚化的地方变清晰，边缘锐利。"
    
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("未配置OPENAI_API_KEY，请在.env文件中设置OPENAI_API_KEY=你的密钥")
        if OPENAI_API_KEY == "your_openai_api_key_here":
            raise ValueError("请在.env文件中将OPENAI_API_KEY设置为你的实际API密钥，而不是默认值")
        
        # API 配置 - New API OpenAI 格式
        self.api_base_url = "https://api.qidianai.xyz"
        self.api_key = OPENAI_API_KEY
        
        # 设置超时：所有超时都设置为5分钟
        self.timeout = httpx.Timeout(
            timeout=300.0,        # 总超时5分钟
            connect=300.0,        # 连接超时5分钟
            read=300.0,           # 读取超时5分钟
            write=300.0           # 写入超时5分钟
        )
        
        print(f"使用API接口: {self.api_base_url}")
        print(f"API格式: New API OpenAI 格式")
        print(f"超时设置: 所有超时均为5分钟")
        print(f"SSL验证: 已禁用（避免证书问题）")
    
    def _prepare_image_for_edit(self, image: Image.Image, target_size: Tuple[int, int]) -> io.BytesIO:
        """
        准备图片用于编辑API（OpenAI 格式使用文件上传）
        
        Args:
            image: 原始图片
            target_size: 目标尺寸
        
        Returns:
            image_bytes - 图片的BytesIO对象
        """
        # 转换为RGB（如果不是）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 调整尺寸到目标尺寸
        from image_utils import resize_image_smart
        resized_image = resize_image_smart(image, target_size, method='lanczos')
        
        # 转换为PNG格式的BytesIO
        image_bytes = io.BytesIO()
        resized_image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        
        return image_bytes
    
    def edit_image(self, image: Image.Image, target_size: Tuple[int, int] = (1024, 1024)) -> Optional[Image.Image]:
        """
        使用API编辑图片，使其变清晰
        使用 New API OpenAI 格式接口
        参考文档: https://doc.newapi.pro/api/openai-image/
        
        Args:
            image: 原始图片
            target_size: 目标尺寸 (width, height)，例如 (1024, 1536)
        
        Returns:
            编辑后的清晰图片或None
        """
        # 准备图片（调整尺寸和格式）
        image_bytes = self._prepare_image_for_edit(image, target_size)
        
        # 使用固定提示词
        prompt = self.FIXED_PROMPT
        
        # 将尺寸转换为API需要的格式（如 "1024x1536"）
        size_str = f"{target_size[0]}x{target_size[1]}"
        
        try:
            image_size = len(image_bytes.getvalue())
            
            print(f"正在使用API编辑图片...")
            print(f"API地址: {self.api_base_url}")
            print(f"API格式: New API OpenAI 格式")
            print(f"目标尺寸: {target_size[0]}×{target_size[1]}")
            print(f"API尺寸参数: {size_str}")
            print(f"固定提示词: {prompt}")
            print(f"图片大小: {image_size} 字节")
            print(f"图片格式: PNG (RGB模式)")
            
            # 调用图像编辑API
            print("正在调用API...")
            print("提示: 图片处理可能需要较长时间（1-5分钟），请耐心等待...")
            
            # 记录开始时间
            start_time = time.time()
            
            # 根据正确的任务日志，使用 OpenAI 格式的图片编辑接口
            # 端点: /v1/images/edits
            # 参考: 正确的任务日志.txt
            endpoint = "/v1/images/edits"
            api_url = f"{self.api_base_url}{endpoint}"
            
            print(f"使用端点: {api_url}")
            
            # 根据正确的任务日志，需要将图片转换为 base64
            # 关键参数：
            # - image[]: base64 编码的图片（注意是 image[] 数组格式）
            # - model: gpt-image-1
            # - prompt: 提示词
            # - quality: high
            # - size: 例如 1024x1024
            # - response_format: b64_json
            
            # 根据错误信息，API需要 multipart/form-data 格式
            # 将图片保存为临时文件，然后作为文件上传
            image_bytes.seek(0)
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as tmp_file:
                tmp_file.write(image_bytes.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # 准备 multipart/form-data 请求
                # 注意：图片需要作为文件上传，参数名是 image[]
                with open(tmp_file_path, 'rb') as image_file:
                    files = {
                        'image[]': ('image.png', image_file, 'image/png'),  # 文件上传
                        'model': (None, 'gpt-image-1'),
                        'prompt': (None, prompt),
                        'quality': (None, 'high'),
                        'size': (None, size_str),
                        'response_format': (None, 'b64_json'),
                    }
                    
                    headers = {
                        'Authorization': f'Bearer {self.api_key}',
                    }
                    
                    # 发送请求
                    print(f"开始发送API请求... (时间: {time.strftime('%H:%M:%S')})")
                    print(f"请求格式: multipart/form-data (文件上传)")
                    print(f"图片参数名: image[] (文件格式)")
                    
                    with httpx.Client(
                        timeout=self.timeout,
                        verify=False,
                        follow_redirects=True
                    ) as client:
                        response = client.post(api_url, files=files, headers=headers)
                
                elapsed = time.time() - start_time
                print(f"API请求完成，耗时: {elapsed:.2f} 秒 ({elapsed/60:.1f} 分钟)")
                print(f"响应状态码: {response.status_code}")
                
                # 检查响应
                if response.status_code == 200:
                    try:
                        # 解析 JSON 响应
                        data = response.json()
                        print(f"响应数据: {json.dumps(data, indent=2)[:500]}...")
                        
                        # 根据正确的任务日志，响应格式应该是：
                        # {
                        #   "created": 1589478378,
                        #   "data": [
                        #     {
                        #       "url": "https://...",
                        #       "b64_json": "..."
                        #     }
                        #   ],
                        #   "usage": {...}  // 可选
                        # }
                        
                        if 'data' in data and len(data['data']) > 0:
                            result = data['data'][0]
                            
                            # 检查是否有 base64 编码的图片
                            if 'b64_json' in result:
                                image_base64 = result['b64_json']
                                
                                # 处理可能的 data URI 前缀（如 data:image/png;base64,）
                                if ',' in image_base64:
                                    image_base64 = image_base64.split(',', 1)[1]
                                
                                # 移除所有空白字符
                                image_base64 = image_base64.strip().replace('\n', '').replace('\r', '').replace(' ', '')
                                
                                # 确保 base64 字符串长度是 4 的倍数（添加填充）
                                missing_padding = len(image_base64) % 4
                                if missing_padding:
                                    image_base64 += '=' * (4 - missing_padding)
                                
                                try:
                                    image_bytes_decoded = base64.b64decode(image_base64)
                                    edited_image = Image.open(io.BytesIO(image_bytes_decoded))
                                    print(f"✓ 图片编辑完成，尺寸: {edited_image.size}")
                                except Exception as decode_error:
                                    print(f"✗ Base64 解码失败: {decode_error}")
                                    print(f"Base64 字符串长度: {len(image_base64)}")
                                    print(f"Base64 字符串前100字符: {image_base64[:100]}...")
                                    return None
                                
                                # 显示 token 使用情况（如果有）
                                if 'usage' in data:
                                    usage = data['usage']
                                    print(f"Token使用: 总计={usage.get('total_tokens', 'N/A')}, "
                                          f"输入={usage.get('input_tokens', 'N/A')}, "
                                          f"输出={usage.get('output_tokens', 'N/A')}")
                                
                                return edited_image
                            
                            # 检查是否有 URL
                            elif 'url' in result:
                                print(f"尝试从URL下载图片: {result['url']}")
                                with httpx.Client(timeout=30.0, verify=False) as download_client:
                                    img_response = download_client.get(result['url'])
                                    edited_image = Image.open(io.BytesIO(img_response.content))
                                    print(f"✓ 图片编辑完成（从URL下载），尺寸: {edited_image.size}")
                                    return edited_image
                            
                            else:
                                print(f"错误: 响应中未找到图片数据")
                                print(f"可用字段: {list(result.keys())}")
                                return None
                        else:
                            print(f"错误: 响应数据格式不正确")
                            print(f"响应内容: {response.text[:500]}")
                            return None
                            
                    except json.JSONDecodeError as e:
                        print(f"错误: 无法解析JSON响应: {e}")
                        print(f"响应内容: {response.text[:500]}")
                        return None
                else:
                    print(f"API返回错误状态码: {response.status_code}")
                    print(f"响应内容: {response.text[:500]}")
                    return None
                    
            finally:
                # 清理临时文件
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass
                
        except httpx.ConnectError as e:
            elapsed = time.time() - start_time
            error_msg = str(e)
            print(f"\n✗ 连接错误: {type(e).__name__}: {e}")
            print(f"已耗时: {elapsed:.2f} 秒")
            
            if "10061" in error_msg or "积极拒绝" in error_msg:
                print("\n" + "=" * 60)
                print("连接被拒绝 - 诊断信息")
                print("=" * 60)
                print(f"API地址: {self.api_base_url}")
                print(f"端点: /v1/images/generations")
                print(f"完整URL: {self.api_base_url}/v1/images/generations")
                print("\n可能的原因：")
                print("  1. API端点路径不正确")
                print("  2. API服务器不支持该接口")
                print("  3. 需要联系API提供商确认正确的端点路径")
                print("  4. API服务当前不可用或配置有问题")
                print("\n建议：")
                print("  1. 联系 API 提供商（qidianai.xyz）确认：")
                print("     - 是否支持 /v1/images/generations 接口")
                print("     - 正确的端点路径是什么")
                print("     - 是否需要不同的 base URL")
                print("  2. 检查 API 文档：")
                print("     https://doc.newapi.pro/api/openai-image/")
                print("  3. 确认 API Key 是否有权限访问该接口")
            
            return None
        except httpx.RequestError as e:
            elapsed = time.time() - start_time
            print(f"\n✗ 请求错误: {type(e).__name__}: {e}")
            print(f"已耗时: {elapsed:.2f} 秒")
            return None
        except Exception as e:
            print(f"✗ 编辑图片时出错: {type(e).__name__}: {e}")
            import traceback
            print("详细错误信息:")
            traceback.print_exc()
            
            # 提供更友好的错误信息
            error_str = str(e).lower()
            error_type = type(e).__name__
            
            # 检查是否是连接错误
            if "connection" in error_str or "connect" in error_str:
                print("\n" + "=" * 60)
                print("连接错误诊断")
                print("=" * 60)
                print(f"API地址: {self.api_base_url}")
                print("\n可能的原因：")
                print("  1. API服务器不可访问或已关闭")
                print("  2. API端点路径不正确")
                print("  3. 网络连接被阻止（防火墙/代理）")
                print("  4. DNS解析失败")
                print("\n诊断步骤：")
                print("  1. 测试基础连接:")
                print("     python test_connection_qidianai.py")
                print("  2. 检查API端点是否正确")
                print("  3. 确认API服务器是否支持图片编辑功能")
                
                # 尝试诊断连接问题
                try:
                    import socket
                    hostname = "api.qidianai.xyz"
                    ip = socket.gethostbyname(hostname)
                    print(f"\n✓ DNS解析成功: {hostname} -> {ip}")
                    
                    # 测试TCP连接
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((ip, 443))
                    sock.close()
                    if result == 0:
                        print(f"✓ TCP连接成功: {ip}:443")
                    else:
                        print(f"✗ TCP连接失败: 错误代码 {result}")
                except Exception as diag_error:
                    print(f"✗ 连接诊断失败: {diag_error}")
            
            elif "api key" in error_str or "authentication" in error_str:
                print("\n提示: 可能是API Key配置错误，请检查.env文件")
            elif "rate limit" in error_str or "quota" in error_str:
                print("\n提示: 可能是API配额或速率限制，请稍后再试")
            elif "timeout" in error_str:
                print("\n提示: 网络连接超时，可能的原因：")
                print("  1. 网络连接不稳定")
                print("  2. API服务器响应慢（图片处理是同步的，需要较长时间）")
                print("  3. 防火墙阻止连接")
                print("  4. DNS解析问题")
                print("\n当前超时设置:")
                print("  - 总超时: 5分钟")
                print("  - 连接超时: 5分钟")
                print("  - 读取超时: 5分钟")
                print("\n建议：")
                print("  - 检查网络连接: python test_connection_qidianai.py")
                print("  - 确认API服务器是否可访问")
                print("  - 如果超时时间不够，可以进一步增加")
            elif "model" in error_str:
                print("\n提示: 可能是模型名称错误，当前使用: gpt-image-1")
            
            return None
    
    def enhance_image_with_ai(self, image: Image.Image, 
                              target_size: Tuple[int, int] = None) -> Optional[Image.Image]:
        """
        使用AI将图片变清晰
        直接调用API编辑现有图片
        
        Args:
            image: 原始图片
            target_size: 目标尺寸，None则使用原图尺寸
        
        Returns:
            编辑后的清晰图片或None
        """
        if target_size is None:
            target_size = image.size
        
        # 使用API编辑图片
        print("正在使用API编辑图片...")
        print(f"固定提示词: {self.FIXED_PROMPT}")
        clear_image = self.edit_image(image, target_size)
        
        return clear_image

