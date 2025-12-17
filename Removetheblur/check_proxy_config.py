"""
检查代理配置和连接
"""
import sys
import os

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("代理配置检查")
print("=" * 60)
print()

# 1. 检查环境变量中的代理
print("[1] 检查环境变量代理设置...")
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
for var in proxy_vars:
    value = os.environ.get(var, '')
    if value:
        print(f"  {var} = {value}")
    else:
        print(f"  {var} = (未设置)")
print()

# 2. 检查.env文件中的代理配置
print("[2] 检查.env文件中的代理配置...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    https_proxy = os.getenv('HTTPS_PROXY', '')
    http_proxy = os.getenv('HTTP_PROXY', '')
    
    if https_proxy:
        print(f"  ✓ HTTPS_PROXY = {https_proxy}")
    else:
        print(f"  ✗ HTTPS_PROXY = (未设置)")
    
    if http_proxy:
        print(f"  ✓ HTTP_PROXY = {http_proxy}")
    else:
        print(f"  ✗ HTTP_PROXY = (未设置)")
    
    if not https_proxy and not http_proxy:
        print()
        print("  ⚠️  未在.env文件中配置代理")
        print("  请在.env文件中添加：")
        print("  HTTPS_PROXY=http://127.0.0.1:1080")
        print("  HTTP_PROXY=http://127.0.0.1:1080")
except Exception as e:
    print(f"  ✗ 检查.env文件失败: {e}")
print()

# 3. 测试OpenAI客户端初始化
print("[3] 测试OpenAI客户端初始化...")
try:
    from config import OPENAI_API_KEY
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        print("  ✗ API Key未配置")
    else:
        print(f"  ✓ API Key已配置: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}")
        
        # 尝试初始化GPTHandler
        from gpt_handler import GPTHandler
        handler = GPTHandler()
        print("  ✓ GPTHandler初始化成功")
        
        # 检查客户端配置
        if hasattr(handler, 'client'):
            print("  ✓ OpenAI客户端已创建")
            # 检查是否有代理配置
            if hasattr(handler.client, '_client'):
                http_client = handler.client._client
                if hasattr(http_client, '_proxies'):
                    proxies = http_client._proxies
                    if proxies:
                        print(f"  ✓ 代理配置: {proxies}")
                    else:
                        print("  ⚠️  客户端未配置代理")
except Exception as e:
    print(f"  ✗ 初始化失败: {e}")
    import traceback
    traceback.print_exc()
print()

# 4. 测试网络连接
print("[4] 测试网络连接...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex(('api.openai.com', 443))
    sock.close()
    if result == 0:
        print("  ✓ 可以连接到 api.openai.com:443")
    else:
        print(f"  ✗ 无法连接到 api.openai.com:443 (错误代码: {result})")
        print("  提示: 可能需要通过代理连接")
except Exception as e:
    print(f"  ✗ 连接测试失败: {e}")
print()

print("=" * 60)
print("检查完成")
print("=" * 60)




