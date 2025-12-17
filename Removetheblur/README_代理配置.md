# 代理配置说明

## 重要提示

**OpenAI Python客户端支持HTTP/HTTPS代理，但不支持SOCKS代理。**

如果你在中国大陆，访问OpenAI API通常需要代理。请按以下方式配置：

## 如果你必须使用 SOCKS5 代理

如果你的代理软件（如 JamJams）只支持 SOCKS5，有两个解决方案：

### 方案1：使用 Privoxy 转换（推荐）

使用 Privoxy 将 SOCKS5 代理转换为 HTTP 代理，无需安装额外的 Python 库。

**详细步骤请查看：`使用Privoxy转换SOCKS代理.md`**

快速步骤：
1. 下载安装 Privoxy: https://www.privoxy.org/
2. 配置 Privoxy 转发到你的 SOCKS5 代理（127.0.0.1:1080）
3. 在 `.env` 中使用 Privoxy 的 HTTP 代理（127.0.0.1:8118）

### 方案2：使用代理软件的 HTTP 模式

如果你的代理软件支持 HTTP 模式（如 JamJams 可以切换），直接使用 HTTP 模式。

## 配置方法

### 方法1：在.env文件中配置（推荐）

编辑 `.env` 文件，添加代理配置：

```env
OPENAI_API_KEY=你的API密钥

# HTTP/HTTPS代理配置
HTTPS_PROXY=http://127.0.0.1:7890
HTTP_PROXY=http://127.0.0.1:7890
```

**注意：**
- 将 `127.0.0.1:7890` 替换为你的实际代理地址和端口
- 代理地址必须以 `http://` 或 `https://` 开头
- 不要使用 `socks4://` 或 `socks5://`

### 方法2：使用环境变量

在运行Web服务前，设置环境变量：

**Windows (CMD):**
```cmd
set HTTPS_PROXY=http://127.0.0.1:7890
set HTTP_PROXY=http://127.0.0.1:7890
python web_app.py
```

**Windows (PowerShell):**
```powershell
$env:HTTPS_PROXY="http://127.0.0.1:7890"
$env:HTTP_PROXY="http://127.0.0.1:7890"
python web_app.py
```

### 方法3：使用启动脚本

创建 `run_with_proxy.bat`：

```batch
@echo off
set HTTPS_PROXY=http://127.0.0.1:7890
set HTTP_PROXY=http://127.0.0.1:7890
cd /d "%~dp0"
python web_app.py
```

## 常见代理端口

- Clash: `http://127.0.0.1:7890`
- V2Ray: `http://127.0.0.1:10809` (需要HTTP模式)
- Shadowsocks: 需要转换为HTTP代理（见下方）

## 如果只有SOCKS代理

如果你只有SOCKS代理（如Shadowsocks），需要将其转换为HTTP代理：

### 使用Privoxy转换（推荐）

1. 下载并安装 [Privoxy](https://www.privoxy.org/)
2. 配置Privoxy监听HTTP代理端口（如8118）
3. 配置Privoxy转发到SOCKS代理
4. 在.env文件中使用Privoxy的HTTP代理地址：
   ```env
   HTTPS_PROXY=http://127.0.0.1:8118
   ```

### 使用其他转换工具

- **Clash**: 自带HTTP代理模式，直接使用
- **V2Ray**: 配置HTTP入站，使用HTTP代理端口

## 验证代理配置

运行测试脚本检查代理是否正常工作：

```cmd
python test_connection.py
```

如果配置正确，会显示：
```
✓ 检测到HTTP代理: HTTPS_PROXY=http://127.0.0.1:7890
使用代理: {'https://': 'http://127.0.0.1:7890'}
```

## 常见问题

### Q: 为什么不能使用SOCKS代理？

A: OpenAI的Python客户端（基于httpx）不支持SOCKS代理，只支持HTTP/HTTPS代理。

### Q: 如何知道我的代理是HTTP还是SOCKS？

A: 
- HTTP代理地址通常以 `http://` 开头
- SOCKS代理地址通常以 `socks4://` 或 `socks5://` 开头

### Q: 我的代理软件没有HTTP模式怎么办？

A: 使用Privoxy等工具将SOCKS代理转换为HTTP代理。

### Q: 配置代理后仍然连接失败？

A: 
1. 检查代理地址和端口是否正确
2. 确认代理软件正在运行
3. 测试代理是否正常工作：`curl -x http://127.0.0.1:7890 https://api.openai.com`
4. 查看详细错误信息：运行 `python test_connection.py`

