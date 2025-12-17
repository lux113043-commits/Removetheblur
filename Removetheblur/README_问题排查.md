# 问题排查指南

## 第一张图片处理失败

### 常见原因和解决方案

#### 1. 网络连接超时

**症状：** 控制台显示 `APITimeoutError` 或 `ConnectTimeout`

**可能原因：**
- 代理设置冲突（SOCKS代理不支持）
- 防火墙阻止连接
- 网络不稳定
- OpenAI服务器响应慢

**解决方案：**

1. **完全禁用代理：**
   ```cmd
   set HTTP_PROXY=
   set HTTPS_PROXY=
   set http_proxy=
   set https_proxy=
   set ALL_PROXY=
   set all_proxy=
   ```
   然后重新运行 `run_web.bat`

2. **使用无代理模式启动：**
   ```cmd
   run_without_proxy.bat
   ```

3. **检查防火墙：**
   - 确保防火墙允许Python访问网络
   - 临时关闭防火墙测试

4. **检查网络连接：**
   ```cmd
   python test_connection.py
   ```

#### 2. API Key问题

**症状：** 控制台显示 `authentication` 或 `API key` 相关错误

**解决方案：**
1. 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确
2. 确保API Key有效且有足够的配额
3. 运行诊断脚本：
   ```cmd
   python check_setup.py
   ```

#### 3. 图片处理超时

**症状：** 图片处理开始但一直不完成

**说明：**
- 图片处理通常需要30-120秒
- 如果图片很大，可能需要更长时间
- 已设置超时时间为10分钟

**解决方案：**
- 耐心等待（处理第一张图片可能需要更长时间）
- 查看控制台输出，确认处理进度
- 如果超过10分钟仍未完成，可能是网络问题

#### 4. 查看详细错误信息

**方法：**
1. 查看运行 `web_app.py` 的命令行窗口
2. 处理图片时，控制台会显示详细日志：
   - `正在加载图片...`
   - `正在切分图片...`
   - `正在调用API...`
   - 如果失败，会显示具体错误信息

3. 运行测试脚本：
   ```cmd
   python test_api.py
   ```
   这会直接测试API调用，显示详细错误

#### 5. 常见错误代码

- **10035 (WSAEWOULDBLOCK)**: 网络连接被阻塞，可能是防火墙
- **ConnectTimeout**: 连接超时，检查网络和代理
- **APITimeoutError**: API调用超时，可能需要更长时间
- **AuthenticationError**: API Key错误

### 诊断步骤

1. **运行环境诊断：**
   ```cmd
   python check_setup.py
   ```

2. **测试网络连接：**
   ```cmd
   python test_connection.py
   ```

3. **测试API调用：**
   ```cmd
   python test_api.py
   ```

4. **查看Web服务日志：**
   - 运行 `run_web.bat` 后，查看命令行窗口的输出
   - 处理图片时会有详细的进度信息

### 如果仍然无法解决

请提供以下信息：
1. 运行 `python check_setup.py` 的完整输出
2. 运行 `python test_connection.py` 的完整输出
3. 运行 `web_app.py` 时的完整错误日志
4. 第一张图片的文件名和大小




