"""
测试到 qidianai.xyz API 的网络连接
"""
import os
import httpx
import time

print("=" * 60)
print("网络连接测试 - qidianai.xyz API")
print("=" * 60)

# 检查当前代理环境变量
print("\n1. 检查代理环境变量:")
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
has_proxy = False
for var in proxy_vars:
    value = os.environ.get(var, '')
    if value:
        print(f"  {var} = {value}")
        has_proxy = True

if not has_proxy:
    print("  ✓ 未检测到代理环境变量")

# 测试连接
print("\n2. 测试连接到 https://api.qidianai.xyz")
print("   (不使用代理，直接连接)")

api_url = "https://api.qidianai.xyz"
timeout = httpx.Timeout(30.0, connect=10.0)

try:
    print(f"  正在连接: {api_url}")
    start_time = time.time()
    
    # 创建一个不使用代理的客户端
    client = httpx.Client(
        timeout=timeout,
        verify=True
    )
    
    # 尝试连接（使用 HEAD 请求，更快）
    try:
        response = client.head(api_url, follow_redirects=True)
        elapsed = time.time() - start_time
        print(f"  ✓ 连接成功!")
        print(f"  状态码: {response.status_code}")
        print(f"  响应时间: {elapsed:.2f} 秒")
    except httpx.HTTPStatusError as e:
        # 即使返回错误状态码，也说明连接成功了
        elapsed = time.time() - start_time
        print(f"  ✓ 连接成功（服务器返回状态码: {e.response.status_code}）")
        print(f"  响应时间: {elapsed:.2f} 秒")
        print(f"  说明: 服务器可访问，但可能需要认证或特定端点")
    except httpx.RequestError as e:
        elapsed = time.time() - start_time
        print(f"  ✗ 连接失败: {type(e).__name__}")
        print(f"  错误信息: {e}")
        print(f"  尝试时间: {elapsed:.2f} 秒")
        raise
    
    client.close()
    
except httpx.ConnectTimeout:
    print("  ✗ 连接超时")
    print("  可能的原因:")
    print("    1. 网络连接不稳定")
    print("    2. 防火墙阻止连接")
    print("    3. DNS 解析失败")
    print("    4. 服务器不可访问")
except httpx.ConnectError as e:
    print(f"  ✗ 连接错误: {e}")
    print("  可能的原因:")
    print("    1. 网络连接问题")
    print("    2. DNS 无法解析 api.qidianai.xyz")
    print("    3. 防火墙或代理阻止连接")
except Exception as e:
    print(f"  ✗ 未知错误: {type(e).__name__}: {e}")

# 测试 DNS 解析
print("\n3. 测试 DNS 解析:")
try:
    import socket
    hostname = "api.qidianai.xyz"
    ip = socket.gethostbyname(hostname)
    print(f"  ✓ DNS 解析成功: {hostname} -> {ip}")
except socket.gaierror as e:
    print(f"  ✗ DNS 解析失败: {e}")
    print("  可能的原因:")
    print("    1. DNS 服务器配置问题")
    print("    2. 网络连接问题")
    print("    3. 域名不存在")

print("\n" + "=" * 60)
print("建议")
print("=" * 60)
if has_proxy:
    print("检测到代理环境变量，但代码已配置为不使用代理")
    print("如果连接失败，可以临时清除代理环境变量:")
    print("  set HTTP_PROXY=")
    print("  set HTTPS_PROXY=")
    print("  set http_proxy=")
    print("  set https_proxy=")
    print("  set ALL_PROXY=")
    print("  set all_proxy=")
else:
    print("未检测到代理环境变量，连接应该正常")
print("\n如果连接测试成功，可以重启 Web 服务并重试图片处理")

