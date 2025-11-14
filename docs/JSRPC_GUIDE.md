# JsRpc 集成指南

## 概述

JsRpc 是一个用于远程调用浏览器方法的工具，通过 WebSocket 连接，可以在浏览器环境中远程执行 JavaScript 代码。AstraCrawler 集成了 JsRpc，用于前端加密破解和数据采集。

## JsRpc 简介

JsRpc 的核心思想是：
1. 在浏览器中注入客户端脚本，建立 WebSocket 连接
2. 通过 WebSocket 发送 JavaScript 代码到浏览器执行
3. 获取执行结果并返回

这样可以避免手动提取和分析前端代码，直接在浏览器环境中执行加密函数。

## 安装 JsRpc 服务端

### 方式一：从 GitHub 下载

1. 访问 https://github.com/jxhczhl/JsRpc
2. 下载对应平台的可执行文件（Windows/Linux）
3. 解压并运行服务端

### 方式二：使用 Docker（如果提供）

```bash
docker run -d -p 12080:12080 jsrpc/server
```

## 快速开始

### 1. 启动 JsRpc 服务端

```bash
# Windows
JsRpc.exe

# Linux
./JsRpc
```

服务端默认监听 `ws://localhost:12080`

### 2. 在 AstraCrawler 中使用

#### 方式一：通过 Playwright Worker 自动注入

```python
from astra_scheduler.dispatcher import schedule_task
from astra_reverse_core.utils import load_hook_script

# 加载 JsRpc 客户端脚本
jsrpc_script = load_hook_script("jsrpc_client.js")

# 提交任务，自动注入 JsRpc
task = schedule_task(
    url="https://target-site.com",
    priority="high",
    hook_scripts=[jsrpc_script]
)
```

#### 方式二：使用 Python 客户端直接调用

```python
from astra_reverse_core.jsrpc_client import JsRpcClient
import asyncio

async def main():
    # 创建客户端
    client = JsRpcClient(
        ws_url="ws://localhost:12080",
        group="default",
        name="my_client"
    )
    
    # 连接
    await client.connect()
    
    # 执行代码
    result = await client.execute_code("1 + 1")
    print(f"结果: {result}")
    
    # 调用函数
    result = await client.call_function("window.sign", [{"data": "test"}])
    print(f"签名: {result}")
    
    # 断开连接
    await client.disconnect()

asyncio.run(main())
```

## 使用场景

### 场景 1: 破解签名函数

```python
from astra_reverse_core.jsrpc_client import JsRpcClient

async def crack_signature():
    client = JsRpcClient()
    await client.connect()
    
    # 调用目标网站的签名函数
    params = {"action": "getData", "page": 1}
    signature = await client.call_function("window.targetSignFunction", [params])
    
    print(f"签名结果: {signature}")
    await client.disconnect()
```

### 场景 2: 获取动态 Token

```python
async def get_token():
    client = JsRpcClient()
    await client.connect()
    
    # 执行代码获取 Token
    code = """
    function getToken() {
        return document.cookie.match(/token=([^;]+)/)?.[1] || '';
    }
    getToken();
    """
    
    token = await client.execute_code(code)
    print(f"Token: {token}")
    await client.disconnect()
```

### 场景 3: 拦截并修改请求参数

```python
async def modify_request():
    client = JsRpcClient()
    await client.connect()
    
    # 在页面中注册函数，修改请求参数
    code = """
    window.modifyRequest = function(params) {
        // 添加签名
        params.sign = window.sign(params);
        // 添加时间戳
        params.timestamp = Date.now();
        return params;
    };
    """
    
    await client.execute_code(code)
    
    # 调用函数修改参数
    original_params = {"action": "getData"}
    modified_params = await client.call_function("window.modifyRequest", [original_params])
    
    print(f"修改后的参数: {modified_params}")
    await client.disconnect()
```

## 与 Playwright 集成

### 完整示例

```python
from playwright.async_api import async_playwright
from astra_reverse_core.jsrpc_client import JsRpcClient
from astra_reverse_core.utils import load_hook_script

async def crawl_with_jsrpc():
    # 加载 JsRpc 客户端脚本
    jsrpc_script = load_hook_script("jsrpc_client.js")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 注入 JsRpc 客户端
        await page.add_init_script(jsrpc_script)
        
        # 导航到目标页面
        await page.goto("https://target-site.com")
        
        # 等待 JsRpc 连接建立
        await page.wait_for_timeout(2000)
        
        # 创建 JsRpc 客户端
        client = JsRpcClient(ws_url="ws://localhost:12080")
        await client.connect()
        
        # 调用页面中的函数
        result = await client.call_function("window.sign", [{"data": "test"}])
        
        print(f"签名结果: {result}")
        
        await client.disconnect()
        await browser.close()
```

## 配置选项

### JavaScript 客户端配置

在 `jsrpc_client.js` 中可以配置：

```javascript
const jsrpcConfig = {
    wsUrl: 'ws://localhost:12080',  // WebSocket 地址
    group: 'default',                 // 分组名称
    name: 'astracrawler',            // 客户端名称
    reconnectInterval: 3000,         // 重连间隔（毫秒）
    maxReconnectAttempts: 10         // 最大重连次数
};
```

### Python 客户端配置

```python
client = JsRpcClient(
    ws_url="ws://localhost:12080",  # WebSocket 地址
    group="default",                  # 分组名称
    name="my_client"                 # 客户端名称
)
```

## API 参考

### JsRpcClient

#### `connect()`
连接到 JsRpc 服务端

#### `disconnect()`
断开连接

#### `execute_code(code: str, timeout: float = 30.0) -> Any`
执行 JavaScript 代码

#### `call_function(function_name: str, args: list = None, timeout: float = 30.0) -> Any`
调用浏览器中的函数

### JavaScript API

在浏览器控制台中可以使用：

- `window.__jsrpc.connect(url)` - 手动连接
- `window.__jsrpc.disconnect()` - 断开连接
- `window.__jsrpc.register(name, func)` - 注册函数
- `window.__jsrpc.getStatus()` - 获取连接状态

## 最佳实践

1. **错误处理**: 始终使用 try-except 处理连接和调用错误
2. **超时设置**: 为长时间运行的代码设置合适的超时时间
3. **连接管理**: 使用异步上下文管理器确保连接正确关闭
4. **函数注册**: 在页面加载后注册需要调用的函数
5. **日志记录**: 启用日志记录以便调试

## 故障排除

### 问题 1: 无法连接到服务端

**解决方案**:
- 检查 JsRpc 服务端是否运行
- 检查端口是否正确（默认 12080）
- 检查防火墙设置

### 问题 2: 函数调用失败

**解决方案**:
- 确保函数已注册到 window 对象
- 检查函数路径是否正确（如 `window.sign`）
- 查看浏览器控制台的错误信息

### 问题 3: 执行超时

**解决方案**:
- 增加超时时间
- 检查代码是否有死循环
- 优化代码执行效率

## 参考资源

- [JsRpc GitHub 仓库](https://github.com/jxhczhl/JsRpc)
- [JsRpc 使用教程](https://9763.org/scz/web/202408281708/)
- [AstraCrawler 示例代码](../examples/demo_jsrpc.py)

## 示例代码

完整示例请参考：
- `examples/demo_jsrpc.py` - 基础使用示例
- `tests/test_jsrpc.py` - 测试用例

