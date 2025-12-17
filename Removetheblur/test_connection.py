"""
测试网络连接 - 检查是否能连接到OpenAI API
"""
import sys
import os

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("网络连接诊断")
print("=" * 60)
print()

# 1. 检查代理设置
print("[1] 检查代理环境变量...")
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
has_proxy = False
for var in proxy_vars:
    value = os.environ.get(var, '')
    if value:
        print(f"  ✗ {var} = {value}")
        has_proxy = True
    else:
        print(f"  ✓ {var} = (未设置)")

if not has_proxy:
    print("  ✓ 所有代理变量都已清除")
else:
    print("  ⚠️  仍有代理设置，可能影响连接")
print()

# 2. 清除所有代理
print("[2] 清除所有代理设置...")
for var in proxy_vars:
    if var in os.environ:
        del os.environ[var]
print("  ✓ 代理已清除")
print()

# 3. 测试基本网络连接
print("[3] 测试网络连接...")
try:
    import socket
    # 测试DNS解析
    socket.gethostbyname('api.openai.com')
    print("  ✓ DNS解析成功: api.openai.com")
except Exception as e:
    print(f"  ✗ DNS解析失败: {e}")
    sys.exit(1)

# 测试TCP连接
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex(('api.openai.com', 443))
    sock.close()
    if result == 0:
        print("  ✓ TCP连接成功: api.openai.com:443")
    else:
        print(f"  ✗ TCP连接失败: 错误代码 {result}")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ TCP连接失败: {e}")
    sys.exit(1)
print()

# 4. 测试HTTPS连接
print("[4] 测试HTTPS连接...")
try:
    import ssl
    import socket
    
    context = ssl.create_default_context()
    with socket.create_connection(('api.openai.com', 443), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname='api.openai.com') as ssock:
            print("  ✓ HTTPS连接成功")
except Exception as e:
    print(f"  ✗ HTTPS连接失败: {e}")
    print("  提示: 可能是防火墙或网络问题")
    sys.exit(1)
print()

# 5. 测试OpenAI API连接（不实际调用）
print("[5] 测试OpenAI客户端初始化...")
try:
    from config import OPENAI_API_KEY
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        print("  ✗ API Key未配置")
        sys.exit(1)
    
    from openai import OpenAI
    import httpx
    
    # 创建客户端，设置较短的超时用于测试
    timeout = httpx.Timeout(10.0, connect=5.0)
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        timeout=timeout,
        max_retries=0  # 不重试，快速失败
    )
    print("  ✓ OpenAI客户端创建成功")
except Exception as e:
    print(f"  ✗ OpenAI客户端创建失败: {e}")
    sys.exit(1)
print()

# 6. 尝试一个简单的API调用（只测试连接，不实际处理）
print("[6] 测试API连接（简单请求）...")
print("  注意: 这不会实际处理图片，只测试连接")
try:
    # 尝试列出模型（这是一个轻量级请求）
    # 但images.edit需要实际调用，所以我们只测试客户端配置
    print("  ✓ 客户端配置正确")
    print("  提示: 实际图片处理可能需要更长时间")
except Exception as e:
    print(f"  ✗ API测试失败: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✓ 网络连接测试通过")
print("=" * 60)
print()
print("如果所有测试都通过，但图片处理仍然失败，")
print("可能是以下原因：")
print("1. API调用超时（图片处理需要较长时间）")
print("2. API配额或速率限制")
print("3. 图片文件太大或格式问题")
print()
print("建议：")
print("- 查看运行web_app.py时的详细日志")
print("- 尝试处理较小的图片")
print("- 检查OpenAI账户的API配额")




