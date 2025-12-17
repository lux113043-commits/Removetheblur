# 使用 Privoxy 将 SOCKS5 代理转换为 HTTP 代理

由于 `httpx-socks` 安装遇到系统依赖问题，推荐使用 **Privoxy** 将 SOCKS5 代理转换为 HTTP 代理。

## 为什么需要 Privoxy？

- OpenAI 客户端支持 HTTP/HTTPS 代理
- 你的 JamJams 使用 SOCKS5 代理
- Privoxy 可以将 SOCKS5 转换为 HTTP，无需安装额外的 Python 库

## 安装和配置步骤

### 1. 下载 Privoxy

访问：https://www.privoxy.org/
- Windows 版本：下载 `privoxy_setup_3.0.34.exe`（或最新版本）

### 2. 安装 Privoxy

1. 运行安装程序
2. 安装到默认位置（通常是 `C:\Program Files\Privoxy\`）
3. 安装完成后，Privoxy 会自动启动

### 3. 配置 Privoxy

1. 打开配置文件：`C:\Program Files\Privoxy\config.txt`

2. 找到 `listen-address` 行（大约在第 750 行），确保是：
   ```
   listen-address  127.0.0.1:8118
   ```
   这表示 Privoxy 监听本地 8118 端口（HTTP 代理）

3. 找到 `forward-socks5` 或 `forward-socks5t` 行（大约在第 1300 行），添加或修改为：
   ```
   forward-socks5t   /               127.0.0.1:1080 .
   ```
   这表示将所有请求转发到 SOCKS5 代理 `127.0.0.1:1080`（你的 JamJams）

4. 保存文件

5. 重启 Privoxy 服务：
   - 打开"服务"管理器（services.msc）
   - 找到 "Privoxy" 服务
   - 右键 -> 重启

### 4. 配置 .env 文件

编辑 `.env` 文件，使用 Privoxy 的 HTTP 代理：

```env
OPENAI_API_KEY=你的API密钥

# 使用 Privoxy 转换的 HTTP 代理
HTTPS_PROXY=http://127.0.0.1:8118
HTTP_PROXY=http://127.0.0.1:8118

# 可选：图片处理配置
MAX_IMAGE_SIZE=2048
OUTPUT_QUALITY=95
```

### 5. 测试配置

运行测试脚本：

```cmd
python check_proxy_config.py
```

应该看到：
```
✓ 检测到HTTP代理: HTTPS_PROXY=http://127.0.0.1:8118
使用HTTP代理: {'https://': 'http://127.0.0.1:8118', 'http://': 'http://127.0.0.1:8118'}
```

## 工作原理

```
你的程序 → HTTP代理(8118) → Privoxy → SOCKS5代理(1080) → JamJams → 互联网
```

## 注意事项

1. **Privoxy 必须运行**：确保 Privoxy 服务正在运行
2. **JamJams 必须运行**：确保 JamJams 的 SOCKS5 代理正在运行
3. **端口冲突**：如果 8118 端口被占用，可以在 Privoxy 配置中修改为其他端口

## 如果 Privoxy 安装有问题

可以尝试其他代理转换工具：
- **Clash for Windows**：支持同时提供 HTTP 和 SOCKS 代理
- **V2Ray**：可以配置 HTTP 入站

## 快速验证

1. 确保 JamJams 运行在 SOCKS5 模式（127.0.0.1:1080）
2. 确保 Privoxy 服务正在运行
3. 在 `.env` 中配置 `HTTP_PROXY=http://127.0.0.1:8118`
4. 重启 Web 服务
5. 尝试处理图片




