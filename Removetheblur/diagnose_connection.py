"""
详细诊断网络连接问题
"""
import os
import socket
import ssl
import httpx
import time

print("=" * 60)
print("详细网络连接诊断")
print("=" * 60)

hostname = "api.qidianai.xyz"
port = 443

# 1. DNS 解析
print("\n[1] DNS 解析测试")
try:
    ip = socket.gethostbyname(hostname)
    print(f"  ✓ DNS 解析成功: {hostname} -> {ip}")
except Exception as e:
    print(f"  ✗ DNS 解析失败: {e}")
    exit(1)

# 2. TCP 连接测试
print(f"\n[2] TCP 连接测试 ({ip}:{port})")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    start = time.time()
    result = sock.connect_ex((ip, port))
    elapsed = time.time() - start
    sock.close()
    
    if result == 0:
        print(f"  ✓ TCP 连接成功 (耗时: {elapsed:.2f} 秒)")
    else:
        print(f"  ✗ TCP 连接失败: 错误代码 {result}")
        print("  可能的原因:")
        print("    - 端口被防火墙阻止")
        print("    - 服务器未运行")
        print("    - 网络路由问题")
        exit(1)
except Exception as e:
    print(f"  ✗ TCP 连接测试失败: {e}")
    exit(1)

# 3. SSL/TLS 握手测试
print(f"\n[3] SSL/TLS 握手测试")
try:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    with socket.create_connection((ip, port), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            print(f"  ✓ SSL/TLS 握手成功")
            print(f"  协议版本: {ssock.version()}")
            print(f"  加密套件: {ssock.cipher()[0]}")
except Exception as e:
    print(f"  ✗ SSL/TLS 握手失败: {e}")
    print("  注意: 即使SSL握手失败，我们也会禁用SSL验证继续测试")

# 4. HTTP 连接测试（使用 httpx）
print(f"\n[4] HTTP 连接测试 (httpx)")
try:
    timeout = httpx.Timeout(30.0, connect=10.0)
    client = httpx.Client(
        timeout=timeout,
        verify=False,  # 禁用SSL验证
        follow_redirects=True
    )
    
    # 测试基础连接
    print(f"  正在测试: https://{hostname}/")
    start = time.time()
    try:
        response = client.head(f"https://{hostname}/", follow_redirects=True)
        elapsed = time.time() - start
        print(f"  ✓ HTTP 连接成功")
        print(f"  状态码: {response.status_code}")
        print(f"  耗时: {elapsed:.2f} 秒")
    except httpx.HTTPStatusError as e:
        elapsed = time.time() - start
        print(f"  ✓ HTTP 连接成功（服务器返回状态码: {e.response.status_code}）")
        print(f"  耗时: {elapsed:.2f} 秒")
    except httpx.RequestError as e:
        elapsed = time.time() - start
        print(f"  ✗ HTTP 连接失败: {type(e).__name__}: {e}")
        print(f"  耗时: {elapsed:.2f} 秒")
        if elapsed < 1:
            print("  说明: 连接立即失败，可能是服务器拒绝连接或网络问题")
        elif elapsed >= 10:
            print("  说明: 连接超时，可能是网络慢或服务器无响应")
    
    client.close()
except Exception as e:
    print(f"  ✗ HTTP 测试失败: {e}")

# 5. 测试 OpenAI API 端点
print(f"\n[5] OpenAI API 端点测试")
endpoints = [
    "/v1/models",
    "/v1/images/edits",
    "/models",
    "/images/edits",
]

for endpoint in endpoints:
    try:
        timeout = httpx.Timeout(10.0, connect=5.0)
        client = httpx.Client(
            timeout=timeout,
            verify=False,
            follow_redirects=True
        )
        
        url = f"https://{hostname}{endpoint}"
        print(f"  测试: {url}")
        
        try:
            # 使用 OPTIONS 方法测试端点是否存在（不实际调用）
            response = client.options(url, timeout=5.0)
            print(f"    ✓ 端点可访问 (状态码: {response.status_code})")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"    ⚠️  端点不存在 (404)")
            elif e.response.status_code == 405:
                print(f"    ✓ 端点存在但不支持 OPTIONS 方法 (405)")
            elif e.response.status_code == 401:
                print(f"    ✓ 端点存在，需要认证 (401)")
            else:
                print(f"    ⚠️  状态码: {e.response.status_code}")
        except httpx.RequestError as e:
            print(f"    ✗ 连接失败: {type(e).__name__}")
        
        client.close()
    except Exception as e:
        print(f"    ✗ 测试失败: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)
print("\n如果所有测试都失败，可能的原因：")
print("1. API 服务器当前不可用")
print("2. 需要特定的请求头或认证方式")
print("3. 网络环境限制（防火墙/代理）")
print("4. API 提供商的服务配置问题")


