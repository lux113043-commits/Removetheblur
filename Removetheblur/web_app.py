"""
Web应用 - 批量图片背景修复
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from pathlib import Path
from deblur_agent import DeblurAgent
from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter
import threading
import time
from gpt_handler import GPTHandler
from image_utils import resize_image_smart

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['TEMP_FOLDER'] = 'temp_processed'  # 临时文件夹
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# 确保文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)

# 处理状态
processing_status = {
    'is_processing': False,
    'current_file': '',
    'total_files': 0,
    'processed_files': 0,
    'errors': [],
    'session_id': '',
    'input_folder': '',
    'temp_folder': '',
    'prompt': '',
    'latest_processed': []  # 最新处理的图片列表，用于实时更新
}

# 尺寸通道处理状态（压缩问题/原图问题）
resize_status = {
    'is_processing': False,
    'mode': '',  # 'compressed' or 'original'
    'current_file': '',
    'total_files': 0,
    'processed_files': 0,
    'errors': [],
    'logs': [],  # 任务日志（字符串数组）
    'sharpen': True,
    'sharpen_strength': 0.0,
    'session_id': '',
    'input_folder': '',
    'output_folder': '',
    'target_size': None
}

def _append_resize_log(message: str):
    """追加尺寸通道日志（限制长度，避免无限增长）"""
    global resize_status
    try:
        ts = time.strftime('%H:%M:%S')
        resize_status.setdefault('logs', [])
        resize_status['logs'].append(f"[{ts}] {message}")
        # 最多保留 300 条
        if len(resize_status['logs']) > 300:
            resize_status['logs'] = resize_status['logs'][-300:]
    except Exception:
        pass


def process_resize_batch(
    input_folder: str,
    output_folder: str,
    target_size: tuple,
    mode: str,
    session_id: str = None,
    sharpen: bool = True,
    sharpen_strength: float = 0.0
):
    """批量缩放图片（高质量重采样），用于“尺寸通道”页"""
    global resize_status

    try:
        print(f"\n{'='*60}")
        print(f"[线程启动] 开始批量缩放图片（尺寸通道）")
        print(f"模式: {mode}")
        print(f"输入文件夹: {input_folder}")
        print(f"输出文件夹: {output_folder}")
        print(f"目标尺寸: {target_size}")
        print(f"会话ID: {session_id}")
        print(f"{'='*60}\n")

        resize_status['is_processing'] = True
        resize_status['mode'] = mode
        resize_status['errors'] = []
        resize_status['logs'] = []
        resize_status['processed_files'] = 0
        resize_status['current_file'] = ''
        resize_status['session_id'] = session_id or ''
        resize_status['input_folder'] = input_folder
        resize_status['output_folder'] = output_folder
        resize_status['target_size'] = list(target_size) if target_size else None
        resize_status['sharpen'] = bool(sharpen)
        try:
            sharpen_strength = float(sharpen_strength)
        except Exception:
            sharpen_strength = 0.0
        # 允许更强的锐化（0.0 ~ 1.5）
        sharpen_strength = max(0.0, min(1.5, sharpen_strength))
        resize_status['sharpen_strength'] = sharpen_strength
        _append_resize_log(
            f"任务开始：mode={mode} target={target_size[0]}x{target_size[1]} "
            f"sharpen={'on' if sharpen else 'off'} strength={sharpen_strength:.2f}"
        )

        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        input_path = Path(input_folder)
        image_files = [
            f for f in input_path.iterdir()
            if f.suffix.lower() in image_extensions and f.is_file()
        ]

        if not image_files:
            error_msg = f'在文件夹 {input_folder} 中未找到图片文件（支持格式: .jpg, .jpeg, .png, .bmp, .tiff, .webp）'
            print(f"✗ 错误: {error_msg}")
            resize_status['errors'].append(error_msg)
            _append_resize_log(f"未找到图片：{error_msg}")
            resize_status['total_files'] = 0
            return

        resize_status['total_files'] = len(image_files)

        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        for idx, image_file in enumerate(image_files, 1):
            try:
                resize_status['current_file'] = image_file.name
                resize_status['processed_files'] = idx - 1

                # 统一输出 PNG（无损）
                output_file = output_path / f"{image_file.stem}.png"

                with Image.open(image_file) as im:
                    # 处理 EXIF 方向，避免横竖颠倒
                    try:
                        im = ImageOps.exif_transpose(im)
                    except Exception:
                        pass

                    # PNG 支持透明通道：尽量保留 alpha；P 模式转 RGBA 更稳
                    if im.mode == 'P':
                        im = im.convert('RGBA')

                    # 计算缩放倍数（用于锐化强度调节）
                    try:
                        sx = target_size[0] / max(1, im.size[0])
                        sy = target_size[1] / max(1, im.size[1])
                        scale = (sx + sy) / 2.0
                    except Exception:
                        scale = 1.0

                    # 渐进式缩放：大幅放大时分多步，更接近“智能对象”观感
                    def progressive_resize(src_img: Image.Image, dst_size: tuple) -> Image.Image:
                        tw, th = dst_size
                        cw, ch = src_img.size
                        # 仅在明显放大时启用（避免浪费时间）
                        if cw <= 0 or ch <= 0:
                            return resize_image_smart(src_img, dst_size, method='lanczos')
                        if tw <= cw * 1.15 and th <= ch * 1.15:
                            return resize_image_smart(src_img, dst_size, method='lanczos')

                        cur = src_img
                        # 每次放大 1.5x，直到接近目标
                        while True:
                            cw2, ch2 = cur.size
                            nw = min(tw, int(cw2 * 1.5))
                            nh = min(th, int(ch2 * 1.5))
                            if nw == tw and nh == th:
                                break
                            cur = resize_image_smart(cur, (nw, nh), method='lanczos')
                            if nw == tw and nh == th:
                                break
                        if cur.size != dst_size:
                            cur = resize_image_smart(cur, dst_size, method='lanczos')
                        return cur

                    resized = progressive_resize(im, target_size)

                    # 额外锐化（提高观感清晰度；不会“创造”细节）
                    if sharpen and sharpen_strength > 0:
                        base = 1.0 if scale <= 1.0 else 1.35  # 放大更积极
                        # 双重锐化：微细节 + 轮廓（强度越大越明显）
                        s = sharpen_strength
                        s1 = min(s, 1.0)  # 用于 radius 的强度（避免半径过大）
                        # 微细节（小半径高百分比）
                        r_micro = 0.55 + 0.25 * s1 * base
                        p_micro = int(160 + 320 * s * base)
                        t_micro = 1
                        # 轮廓（中半径中百分比）
                        r_edge = 1.05 + 0.55 * s1 * base
                        p_edge = int(80 + 220 * s * base)
                        t_edge = 2

                        if resized.mode in ('RGBA', 'LA'):
                            alpha = resized.getchannel('A')
                            rgb = resized.convert('RGB')
                            rgb = rgb.filter(ImageFilter.UnsharpMask(radius=r_micro, percent=p_micro, threshold=t_micro))
                            rgb = rgb.filter(ImageFilter.UnsharpMask(radius=r_edge, percent=p_edge, threshold=t_edge))
                            resized = rgb.convert('RGBA')
                            resized.putalpha(alpha)
                        else:
                            if resized.mode != 'RGB':
                                resized = resized.convert('RGB')
                            resized = resized.filter(ImageFilter.UnsharpMask(radius=r_micro, percent=p_micro, threshold=t_micro))
                            resized = resized.filter(ImageFilter.UnsharpMask(radius=r_edge, percent=p_edge, threshold=t_edge))
                    # PNG 保存（无损），适度压缩不影响清晰度
                    resized.save(str(output_file), format='PNG', optimize=True, compress_level=6)

                resize_status['processed_files'] = idx
                _append_resize_log(f"✓ 完成：{image_file.name} -> {output_file.name}")
                # 轻微延迟，给前端轮询更平滑
                time.sleep(0.02)

            except Exception as e:
                err = f"{image_file.name}: {str(e)}"
                print(f"✗ 缩放失败: {err}")
                resize_status['errors'].append(err)
                _append_resize_log(f"✗ 失败：{err}")
                resize_status['processed_files'] = idx

    except Exception as e:
        import traceback
        error_msg = f"批量缩放错误: {str(e)}"
        print(f"严重错误: {error_msg}")
        traceback.print_exc()
        resize_status['errors'].append(error_msg)
    finally:
        resize_status['is_processing'] = False
        resize_status['current_file'] = ''
        _append_resize_log("任务结束")
        if resize_status.get('total_files', 0) == 0 and resize_status.get('errors'):
            resize_status['total_files'] = 1


def process_images_batch(input_folder, output_folder, session_id=None, prompt: str = None):
    """批量处理图片"""
    global processing_status
    
    try:
        print(f"\n{'='*60}")
        print(f"[线程启动] 开始批量处理图片")
        print(f"输入文件夹: {input_folder}")
        print(f"输出文件夹: {output_folder}")
        print(f"会话ID: {session_id}")
        if prompt:
            print(f"提示词: {prompt}")
        print(f"{'='*60}\n")
        
        processing_status['is_processing'] = True
        processing_status['errors'] = []
        processing_status['processed_files'] = 0
        processing_status['latest_processed'] = []
        if session_id:
            processing_status['session_id'] = session_id
            processing_status['input_folder'] = input_folder
            processing_status['temp_folder'] = output_folder
            processing_status['prompt'] = prompt or ''
        
        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        
        # 获取所有图片文件
        input_path = Path(input_folder)
        image_files = [
            f for f in input_path.iterdir()
            if f.suffix.lower() in image_extensions and f.is_file()
        ]
        
        if not image_files:
            error_msg = f'在文件夹 {input_folder} 中未找到图片文件（支持格式: .jpg, .jpeg, .png, .bmp, .tiff, .webp）'
            print(f"✗ 错误: {error_msg}")
            print(f"请检查文件夹路径是否正确，以及文件夹中是否包含支持的图片格式")
            processing_status['errors'].append(error_msg)
            processing_status['is_processing'] = False
            processing_status['total_files'] = 0
            return
        
        print(f"✓ 找到 {len(image_files)} 张图片文件")
        processing_status['total_files'] = len(image_files)
        processing_status['current_file'] = ''
        
        # 创建输出文件夹
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 初始化agent，捕获初始化错误
        try:
            print("=" * 60)
            print("正在初始化AI处理器...")
            print("=" * 60)
            agent = DeblurAgent()
            print("✓ AI处理器初始化成功")
            print("=" * 60)
        except Exception as e:
            error_msg = f"初始化AI处理器失败: {str(e)}"
            print(f"✗ 错误: {error_msg}")
            import traceback
            traceback.print_exc()
            processing_status['errors'].append(error_msg)
            processing_status['is_processing'] = False
            processing_status['total_files'] = len(image_files) if image_files else 0
            return
        
        # 处理每张图片
        processing_status['latest_processed'] = []  # 清空之前的数据
        for idx, image_file in enumerate(image_files, 1):
            try:
                processing_status['current_file'] = image_file.name
                processing_status['processed_files'] = idx - 1
                
                # 输出文件路径
                output_file = output_path / f"{image_file.stem}_clear.jpg"
                
                # 处理图片
                print(f"\n{'='*60}")
                print(f"开始处理第 {idx}/{len(image_files)} 张图片: {image_file.name}")
                print(f"{'='*60}")
                result = agent.process_image(
                    input_path=str(image_file),
                    output_path=str(output_file),
                    target_size=(1024, 1536),
                    prompt=prompt
                )
                
                if result['success']:
                    # 处理成功，添加到最新处理列表（只包含当前处理的这一张）
                    processing_status['processed_files'] = idx
                    processing_status['latest_processed'] = [{
                        'original': str(image_file),
                        'fixed': str(output_file),
                        'name': output_file.name,
                        'original_name': image_file.name
                    }]
                    print(f"✓ 成功处理: {image_file.name}")
                    # 短暂延迟，确保前端能获取到更新
                    time.sleep(0.1)
                else:
                    error_msg = f"{image_file.name}: {result.get('error', '处理失败')}"
                    print(f"✗ 处理失败: {error_msg}")
                    processing_status['errors'].append(error_msg)
                    # 即使失败也更新处理计数，避免卡在"处理中"
                    processing_status['processed_files'] = idx
                
            except Exception as e:
                error_msg = f"{image_file.name}: {str(e)}"
                print(f"✗ 处理异常: {error_msg}")
                import traceback
                traceback.print_exc()
                processing_status['errors'].append(error_msg)
        
        # 最终更新处理文件数
        if processing_status['processed_files'] < len(image_files):
            processing_status['processed_files'] = len(image_files)
        
    except Exception as e:
        import traceback
        error_msg = f"批量处理错误: {str(e)}"
        print(f"严重错误: {error_msg}")
        traceback.print_exc()
        processing_status['errors'].append(error_msg)
    finally:
        processing_status['is_processing'] = False
        processing_status['current_file'] = ''
        # 确保total_files被设置
        if processing_status.get('total_files', 0) == 0 and processing_status.get('errors'):
            processing_status['total_files'] = 1  # 至少显示有错误


@app.route('/')
def index():
    """主页"""
    return render_template('index.html', default_prompt=GPTHandler.FIXED_PROMPT)


@app.route('/api/process', methods=['POST', 'OPTIONS'])
def api_process():
    """处理图片API"""
    global processing_status
    
    # 处理CORS预检请求
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    
    print(f"\n{'='*60}")
    print(f"[API请求] /api/process")
    print(f"请求方法: {request.method}")
    print(f"请求头: {dict(request.headers)}")
    print(f"请求数据: {request.json}")
    print(f"当前处理状态: {processing_status.get('is_processing', False)}")
    print(f"{'='*60}\n")
    
    # 强制刷新输出
    import sys
    sys.stdout.flush()
    
    if processing_status['is_processing']:
        print("⚠️ 已有任务在处理中，拒绝新请求")
        return jsonify({
            'success': False,
            'message': '正在处理中，请等待完成'
        }), 400
    
    data = request.json
    if not data:
        print("✗ 错误: 请求数据为空")
        return jsonify({
            'success': False,
            'message': '请求数据无效'
        }), 400
    
    input_folder = data.get('input_folder', '').strip()
    print(f"输入文件夹路径: {input_folder}")
    prompt = data.get('prompt', None)
    if isinstance(prompt, str):
        prompt = prompt.strip()
        if not prompt:
            prompt = None
    else:
        prompt = None
    print(f"提示词: {prompt or '(使用默认提示词)'}")
    
    if not input_folder:
        return jsonify({
            'success': False,
            'message': '请输入图片文件夹路径'
        }), 400
    
    if not os.path.exists(input_folder):
        return jsonify({
            'success': False,
            'message': '文件夹路径不存在'
        }), 400
    
    if not os.path.isdir(input_folder):
        return jsonify({
            'success': False,
            'message': '路径不是文件夹'
        }), 400
    
    # 使用临时文件夹存储处理后的图片
    import uuid
    session_id = str(uuid.uuid4())[:8]
    temp_folder = os.path.join(app.config['TEMP_FOLDER'], session_id)
    os.makedirs(temp_folder, exist_ok=True)
    
    # 保存会话信息
    processing_status['session_id'] = session_id
    processing_status['input_folder'] = input_folder
    processing_status['temp_folder'] = temp_folder
    processing_status['prompt'] = prompt or ''
    
    # 立即更新状态，让前端知道处理已开始
    processing_status['is_processing'] = True
    processing_status['current_file'] = '正在初始化...'
    processing_status['errors'] = []
    processing_status['processed_files'] = 0
    processing_status['latest_processed'] = []
    
    # 在后台线程中处理
    print(f"\n{'='*60}")
    print(f"[API] 收到处理请求")
    print(f"输入文件夹: {input_folder}")
    print(f"临时文件夹: {temp_folder}")
    print(f"会话ID: {session_id}")
    print(f"处理状态已设置为: is_processing=True")
    print(f"{'='*60}\n")
    
    thread = threading.Thread(
        target=process_images_batch,
        args=(input_folder, temp_folder, session_id, prompt),
        name=f"ProcessThread-{session_id}"
    )
    thread.daemon = True
    thread.start()
    
    print(f"✓ 处理线程已启动 (线程名: {thread.name})")
    print(f"线程是否存活: {thread.is_alive()}")
    
    # 等待一小段时间，确保线程真的启动了
    import time
    time.sleep(0.1)
    print(f"线程启动后状态: 存活={thread.is_alive()}, 处理状态={processing_status['is_processing']}")
    
    return jsonify({
        'success': True,
        'message': '开始处理',
        'session_id': session_id,
        'temp_folder': temp_folder
    })


@app.route('/api/status', methods=['GET'])
def api_status():
    """获取处理状态"""
    return jsonify(processing_status)

@app.route('/api/resize', methods=['POST'])
def api_resize():
    """尺寸通道：批量缩放图片"""
    global processing_status, resize_status

    # 如果 AI 修复或尺寸通道正在运行，拒绝并发
    if processing_status.get('is_processing'):
        return jsonify({'success': False, 'message': 'AI修复正在处理中，请等待完成后再进行尺寸通道处理'}), 400
    if resize_status.get('is_processing'):
        return jsonify({'success': False, 'message': '尺寸通道正在处理中，请等待完成'}), 400

    data = request.json or {}
    input_folder = (data.get('input_folder') or '').strip()
    mode = (data.get('mode') or '').strip().lower()
    sharpen = data.get('sharpen', True)
    sharpen_strength = data.get('sharpen_strength', None)

    if not input_folder:
        return jsonify({'success': False, 'message': '请输入图片文件夹路径'}), 400
    if not os.path.exists(input_folder):
        return jsonify({'success': False, 'message': '文件夹路径不存在'}), 400
    if not os.path.isdir(input_folder):
        return jsonify({'success': False, 'message': '路径不是文件夹'}), 400

    if mode not in {'compressed', 'original'}:
        return jsonify({'success': False, 'message': 'mode 参数无效（compressed/original）'}), 400

    # 目标尺寸
    if mode == 'compressed':
        target_size = (1026, 1539)
        out_name = '压缩问题_1026x1539'
        default_strength = 0.30
    else:
        target_size = (2160, 3240)
        out_name = '原图问题_2160x3240'
        default_strength = 0.75

    # 解析锐化参数
    if isinstance(sharpen, str):
        sharpen = sharpen.strip().lower() in {'1', 'true', 'yes', 'y', 'on'}
    else:
        sharpen = bool(sharpen)
    if sharpen_strength is None or sharpen_strength == '':
        sharpen_strength = default_strength
    try:
        sharpen_strength = float(sharpen_strength)
    except Exception:
        sharpen_strength = default_strength
    sharpen_strength = max(0.0, min(1.5, sharpen_strength))

    import uuid
    session_id = str(uuid.uuid4())[:8]
    output_folder = os.path.join(input_folder, out_name)
    os.makedirs(output_folder, exist_ok=True)

    # 立即更新状态（给前端）
    resize_status.update({
        'is_processing': True,
        'mode': mode,
        'current_file': '正在初始化...',
        'total_files': 0,
        'processed_files': 0,
        'errors': [],
        'logs': [],
        'session_id': session_id,
        'input_folder': input_folder,
        'output_folder': output_folder,
        'target_size': list(target_size),
        'sharpen': sharpen,
        'sharpen_strength': sharpen_strength
    })

    thread = threading.Thread(
        target=process_resize_batch,
        args=(input_folder, output_folder, target_size, mode, session_id, sharpen, sharpen_strength),
        name=f"ResizeThread-{session_id}"
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': '开始缩放',
        'session_id': session_id,
        'mode': mode,
        'target_size': list(target_size),
        'output_folder': output_folder
    })


@app.route('/api/resize_status', methods=['GET'])
def api_resize_status():
    """尺寸通道：获取缩放任务状态"""
    return jsonify(resize_status)

@app.route('/api/resize_images', methods=['GET'])
def api_resize_images():
    """尺寸通道：输出文件夹预览（列出输出图片 + 对应原图路径）"""
    global resize_status

    folder = request.args.get('folder', '').strip()
    # 默认使用当前任务输出文件夹
    if not folder:
        folder = (resize_status.get('output_folder') or '').strip()
    # 只允许预览当前 output_folder，避免任意目录浏览
    if not folder or folder != (resize_status.get('output_folder') or ''):
        return jsonify({'images': [], 'message': 'output_folder 无效或不匹配'}), 400

    if not os.path.exists(folder) or not os.path.isdir(folder):
        return jsonify({'images': [], 'message': '输出文件夹不存在'}), 404

    output_path = Path(folder)
    input_folder = (resize_status.get('input_folder') or '').strip()
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

    images = []
    for file in output_path.iterdir():
        if file.is_file() and file.suffix.lower() in image_extensions:
            original_path = None
            if input_folder:
                stem = file.stem
                for ext in image_extensions:
                    test_path = Path(input_folder) / f"{stem}{ext}"
                    if test_path.exists():
                        original_path = test_path
                        break
            images.append({
                'original': str(original_path) if original_path and original_path.exists() else None,
                'resized': str(file),
                'name': file.name,
            })

    # 排序：按文件名
    images.sort(key=lambda x: x.get('name', ''))
    return jsonify({'images': images, 'count': len(images)})


@app.route('/api/task_report', methods=['GET'])
def api_task_report():
    """获取详细的任务报告"""
    global processing_status
    
    report = {
        'is_processing': processing_status.get('is_processing', False),
        'current_file': processing_status.get('current_file', ''),
        'total_files': processing_status.get('total_files', 0),
        'processed_files': processing_status.get('processed_files', 0),
        'errors': processing_status.get('errors', []),
        'session_id': processing_status.get('session_id', ''),
        'input_folder': processing_status.get('input_folder', ''),
        'temp_folder': processing_status.get('temp_folder', ''),
        'progress_percent': 0,
        'status_summary': ''
    }
    
    # 计算进度百分比
    if report['total_files'] > 0:
        report['progress_percent'] = int((report['processed_files'] / report['total_files']) * 100)
    
    # 生成状态摘要
    if report['is_processing']:
        report['status_summary'] = f"正在处理中... ({report['processed_files']}/{report['total_files']})"
    elif report['processed_files'] > 0:
        if report['errors']:
            report['status_summary'] = f"处理完成，但有 {len(report['errors'])} 个错误"
        else:
            report['status_summary'] = "全部处理完成！"
    elif report['errors']:
        report['status_summary'] = f"处理失败: {len(report['errors'])} 个错误"
    else:
        report['status_summary'] = "等待开始处理"
    
    return jsonify(report)


@app.route('/api/images', methods=['GET'])
def api_images():
    """获取处理后的图片列表"""
    session_id = request.args.get('session_id', '')
    temp_folder = request.args.get('folder', '')
    
    # 优先使用session_id
    if session_id:
        temp_folder = os.path.join(app.config['TEMP_FOLDER'], session_id)
    
    if not temp_folder or not os.path.exists(temp_folder):
        return jsonify({'images': []})
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    images = []
    
    # 获取输入文件夹路径
    input_folder = processing_status.get('input_folder', '')
    if not input_folder and session_id:
        # 尝试从临时文件夹推断
        input_folder = str(Path(temp_folder).parent.parent)
    
    for file in Path(temp_folder).iterdir():
        if file.suffix.lower() in image_extensions and file.is_file():
            # 查找对应的原图
            original_name = file.stem.replace('_clear', '')
            
            # 尝试多个可能的原图路径
            original_path = None
            if input_folder:
                # 尝试原始扩展名
                for ext in image_extensions:
                    test_path = Path(input_folder) / f"{original_name}{ext}"
                    if test_path.exists():
                        original_path = test_path
                        break
            
            images.append({
                'original': str(original_path) if original_path and original_path.exists() else None,
                'fixed': str(file),
                'name': file.name,
                'original_name': original_name
            })
    
    return jsonify({'images': images})


@app.route('/api/image')
def serve_image():
    """提供图片访问"""
    filepath = request.args.get('path', '')
    
    if not filepath:
        return 'No file path provided', 400
    
    # 安全检查：确保路径在允许的范围内
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            return 'File not found', 404
        
        # 确保是文件而不是目录
        if not file_path.is_file():
            return 'Not a file', 400
        
        # 返回文件
        folder = str(file_path.parent)
        filename = file_path.name
        return send_from_directory(folder, filename)
    except Exception as e:
        return f'Error: {str(e)}', 500


@app.route('/api/save', methods=['POST'])
def api_save():
    """保存选中的图片到最终位置"""
    data = request.json
    session_id = data.get('session_id', '')
    selected_images = data.get('selected_images', [])  # 选中的图片文件名列表
    output_folder = data.get('output_folder', '')  # 最终保存位置
    folder_type = data.get('folder_type', 'ready')  # 'ready' 或 'reprocess'
    
    if not session_id:
        return jsonify({
            'success': False,
            'message': '缺少session_id'
        }), 400
    
    temp_folder = os.path.join(app.config['TEMP_FOLDER'], session_id)
    if not os.path.exists(temp_folder):
        return jsonify({
            'success': False,
            'message': '临时文件夹不存在'
        }), 400
    
    # 如果没有指定输出文件夹，使用输入文件夹下的相应子文件夹
    if not output_folder:
        input_folder = processing_status.get('input_folder', '')
        if not input_folder:
            return jsonify({
                'success': False,
                'message': '无法确定输出文件夹'
            }), 400
        # 根据folder_type选择不同的文件夹
        if folder_type == 'reprocess':
            output_folder = os.path.join(input_folder, '需要再次处理')
        else:
            output_folder = os.path.join(input_folder, '直接投入使用')
    
    # 创建输出文件夹
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)
    
    saved_count = 0
    errors = []
    
    # 保存选中的图片
    if selected_images:
        # 只保存选中的图片
        for img_name in selected_images:
            try:
                src_file = Path(temp_folder) / img_name
                if src_file.exists():
                    dst_file = output_path / img_name
                    import shutil
                    shutil.copy2(src_file, dst_file)
                    saved_count += 1
            except Exception as e:
                errors.append(f"{img_name}: {str(e)}")
    else:
        # 如果没有选择，保存所有图片
        for file in Path(temp_folder).iterdir():
            if file.is_file() and file.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
                try:
                    dst_file = output_path / file.name
                    import shutil
                    shutil.copy2(file, dst_file)
                    saved_count += 1
                except Exception as e:
                    errors.append(f"{file.name}: {str(e)}")
    
    return jsonify({
        'success': True,
        'message': f'已保存 {saved_count} 张图片',
        'saved_count': saved_count,
        'output_folder': output_folder,
        'errors': errors
    })


@app.route('/api/cleanup', methods=['POST'])
def api_cleanup():
    """清理临时文件夹"""
    data = request.json
    session_id = data.get('session_id', '')
    
    if not session_id:
        return jsonify({
            'success': False,
            'message': '缺少session_id'
        }), 400
    
    temp_folder = os.path.join(app.config['TEMP_FOLDER'], session_id)
    
    try:
        if os.path.exists(temp_folder):
            import shutil
            shutil.rmtree(temp_folder)
            return jsonify({
                'success': True,
                'message': '临时文件夹已清理'
            })
        else:
            return jsonify({
                'success': True,
                'message': '临时文件夹不存在'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'清理失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    import webbrowser
    import time
    
    port = 5000
    url = f'http://localhost:{port}'
    
    print("=" * 60)
    print("图片背景修复Web服务")
    print("=" * 60)
    print(f"访问地址: {url}")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    
    # 延迟2秒后自动打开浏览器
    def open_browser():
        time.sleep(2)
        webbrowser.open(url)
    
    # 在后台线程中打开浏览器
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        app.run(debug=False, host='127.0.0.1', port=port, use_reloader=False)
    except OSError as e:
        if 'Address already in use' in str(e) or 'address is already in use' in str(e):
            print(f"\n错误: 端口 {port} 已被占用")
            print("请关闭占用该端口的程序，或修改 web_app.py 中的端口号")
        else:
            print(f"\n错误: {e}")
        input("\n按Enter键退出...")

