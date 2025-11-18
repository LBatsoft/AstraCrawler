# 获取加密参数使用指南

## 概述

本文档介绍如何使用 AstraCrawler 的 JsRpc 功能在实际场景中获取加密参数，适用于破解类似得物、淘宝等网站的加密逻辑。

## 快速开始

### 1. 启动 JsRpc 服务端

```bash
# 方式 1: 使用模拟服务端（测试用）
python tests/jsrpc_mock_server.py

# 方式 2: 使用真实 JsRpc 服务端
# 从 https://github.com/jxhczhl/JsRpc 下载并运行
```

### 2. 运行示例

```bash
# 运行完整示例
python examples/demo_get_encrypted_params.py

# 或使用启动脚本（自动启动服务端）
./examples/run_encrypt_demo.sh
```

## 使用场景

### 场景 1: 获取签名参数

```python
from astra_reverse_core.jsrpc_client import JsRpcClient
from astra_reverse_core.utils import load_hook_script
from playwright.async_api import async_playwright

async def get_signature():
    # 注入 JsRpc 客户端
    jsrpc_script = load_hook_script("jsrpc_client.js")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.add_init_script(jsrpc_script)
        await page.goto("https://target-site.com")
        await asyncio.sleep(3)
        
        # 连接 JsRpc
        client = JsRpcClient(ws_url="ws://localhost:12080")
        await client.connect()
        
        # 调用签名函数
        params = {"action": "getData", "page": 1}
        signature = await client.call_function(
            "window.generateSign",
            [params]
        )
        
        print(f"签名参数: {signature}")
        await client.disconnect()
        await browser.close()
```

### 场景 2: 批量获取多个页面的签名

```python
async def batch_get_signatures():
    client = JsRpcClient(ws_url="ws://localhost:12080")
    await client.connect()
    
    signatures = []
    for page_num in range(1, 11):  # 获取 10 页
        params = {"page": page_num, "pageSize": 20}
        sign_result = await client.call_function(
            "window.generateSign",
            [params]
        )
        signatures.append({
            "page": page_num,
            "sign": sign_result.get("sign"),
            "timestamp": sign_result.get("timestamp")
        })
    
    return signatures
```

### 场景 3: 获取 Token 和加密参数

```python
async def get_token_and_sign():
    client = JsRpcClient(ws_url="ws://localhost:12080")
    await client.connect()
    
    # 1. 获取 Token
    token_result = await client.call_function("window.getToken", [])
    token = token_result.get("token")
    
    # 2. 生成签名
    params = {"action": "getData", "page": 1}
    sign_result = await client.call_function(
        "window.generateSign",
        [params]
    )
    
    # 3. 构建请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Sign": sign_result.get("sign"),
        "X-Timestamp": str(sign_result.get("timestamp"))
    }
    
    return headers
```

## 实际案例

### 案例 1: 模拟得物网站加密

```python
# 页面中的加密函数（需要先 Hook 或找到）
# window.dewuEncrypt = function(params) { ... }

async def crack_dewu():
    client = JsRpcClient(ws_url="ws://localhost:12080")
    await client.connect()
    
    # 为搜索请求生成加密参数
    search_params = {
        "keyword": "Nike 运动鞋",
        "page": 1,
        "pageSize": 20
    }
    
    encrypted = await client.call_function(
        "window.dewuEncrypt",
        [search_params]
    )
    
    # 使用加密参数发送请求
    import httpx
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            "https://api.dewu.com/search",
            json=encrypted,
            headers={
                "X-Sign": encrypted.get("sign"),
                "X-Timestamp": str(encrypted.get("timestamp"))
            }
        )
        return response.json()
```

### 案例 2: 模拟淘宝签名

```python
async def crack_taobao():
    client = JsRpcClient(ws_url="ws://localhost:12080")
    await client.connect()
    
    # 调用淘宝的签名函数
    params = {
        "method": "taobao.item.get",
        "app_key": "your_app_key",
        "timestamp": str(int(time.time() * 1000)),
        "format": "json",
        "v": "2.0",
        "fields": "num_iid,title,price"
    }
    
    # 假设页面中有 sign 函数
    sign_result = await client.call_function(
        "window.taobaoSign",
        [params]
    )
    
    params["sign"] = sign_result.get("sign")
    
    # 发送请求
    return params
```

## 完整示例

查看 `examples/demo_get_encrypted_params.py` 获取完整的示例代码，包括：

1. **获取签名参数** - 基础签名生成
2. **拦截并获取加密参数** - Hook 加密函数
3. **真实场景破解** - 模拟得物等网站的完整流程

## 注意事项

1. **函数路径**: 确保使用正确的函数路径（如 `window.functionName`）
2. **连接时机**: 等待页面加载完成后再调用函数
3. **错误处理**: 添加适当的错误处理和重试机制
4. **服务端**: 确保 JsRpc 服务端正在运行

## 测试

运行测试用例验证功能：

```bash
pytest tests/test_get_encrypted_params.py -v
```

## 参考

- [JsRpc 集成指南](JSRPC_GUIDE.md)
- [JsRpc 测试报告](JSRPC_TEST_REPORT.md)
- [示例代码](../examples/demo_get_encrypted_params.py)

