# 图片背景修复工具 - Web版本

## 快速开始

### 1. 安装依赖

**Windows用户：**
双击运行 `install.bat`，或在命令行中执行：
```bash
install.bat
```

**手动安装：**
```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

1. 复制 `env_example.txt` 为 `.env`
2. 在 `.env` 文件中填入你的 OpenAI API Key：
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### 3. 启动Web服务

**Windows用户：**
双击运行 `run_web.bat`，或在命令行中执行：
```bash
run_web.bat
```

**手动启动：**
```bash
python web_app.py
```

### 4. 访问Web界面

打开浏览器访问：http://localhost:5000

## 使用说明

1. **输入文件夹路径**
   - 在输入框中填入包含图片的文件夹路径
   - 例如：`D:\Photos\input_images`

2. **开始处理**
   - 点击"开始处理"按钮
   - 系统会自动处理文件夹中的所有图片
   - 处理后的图片会保存在原文件夹的 `fixed_images` 子文件夹中

3. **查看结果**
   - 处理完成后，页面会自动显示处理结果
   - 可以对比每张图片的修复前后效果
   - 原图和修复后的图片并排显示

## 功能特点

- ✅ **批量处理**：自动处理文件夹中的所有图片
- ✅ **实时进度**：显示当前处理进度和状态
- ✅ **前后对比**：并排显示原图和修复后的图片
- ✅ **自动输出**：输出尺寸精确为 1024×1536
- ✅ **智能切分**：自动将竖图切分成两张 1024×1024 分别修复后无缝拼接

## 支持的图片格式

- JPG / JPEG
- PNG
- BMP
- TIFF
- WEBP

## 输出说明

- 所有处理后的图片保存在：`输入文件夹/fixed_images/`
- 文件命名格式：`原文件名_clear.jpg`
- 输出尺寸：1024×1536

## 注意事项

1. **API要求**：
   - 需要有效的OpenAI API Key
   - 需要Images API的访问权限
   - API调用会产生费用

2. **处理时间**：
   - 每张图片约需 20-60 秒
   - 批量处理时间 = 图片数量 × 单张处理时间

3. **文件夹路径**：
   - 请使用完整路径，例如：`D:\Photos\input_images`
   - 不要使用相对路径

4. **网络连接**：
   - 需要稳定的网络连接访问OpenAI API

## 故障排除

### 问题：无法启动Web服务
- 检查是否已安装所有依赖：`pip install -r requirements.txt`
- 检查Python版本（需要Python 3.8+）
- 检查端口5000是否被占用

### 问题：处理失败
- 检查API密钥是否正确配置
- 检查网络连接
- 查看控制台错误信息

### 问题：图片无法显示
- 检查图片路径是否正确
- 检查文件权限
- 查看浏览器控制台错误信息

## 技术栈

- **后端**：Flask (Python Web框架)
- **AI处理**：OpenAI Images API
- **图像处理**：Pillow + NumPy
- **前端**：HTML + CSS + JavaScript

## 许可证

MIT License





