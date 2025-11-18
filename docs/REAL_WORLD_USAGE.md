# 真实场景使用指南

## 重要说明

**本指南说明如何在真实场景中使用 AstraCrawler 获取加密参数，而不是自己定义函数然后调用。**

## 核心思路

在实际场景中：
1. **目标网站已经有加密函数**（在网站的 JS 文件中）
2. **我们不知道函数的具体实现**（可能是混淆、加密的代码）
3. **我们只需要找到函数名，然后通过 JsRpc 调用**
4. **不需要理解函数内部逻辑**

## 真实场景流程

### 步骤 1: 访问目标网站

```python
from playwright.async_api import async_playwright
from astra_reverse_core.utils import load_hook_script, get_default_hooks

async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    
    # 注入 Hook 脚本（用于拦截和发现函数）
    hook_scripts = get_default_hooks()
    jsrpc_script = load_hook_script("jsrpc_client.js")
    
    for hook in hook_scripts:
        await page.add_init_script(hook)
    await page.add_init_script(jsrpc_script)
    
    # 访问真实网站
    await page.goto("https://www.target-site.com")
    await asyncio.sleep(5)  # 等待网站 JS 加载完成
```

### 步骤 2: 找到加密函数名

有几种方法：

#### 方法 1: 通过浏览器开发者工具

1. 打开开发者工具（F12）
2. 在 Network 标签中查看 API 请求
3. 查看请求参数，找到签名相关的字段
4. 在 Sources 标签中搜索函数名（如 `sign`, `encrypt`, `token` 等）

#### 方法 2: 通过 Hook 拦截

```python
# 注入 Hook 脚本后，检查拦截到的数据
intercepted = await page.evaluate("""
    () => {
        if (window.__astraGetInterceptedData) {
            return window.__astraGetInterceptedData();
        }
        return [];
    }
""")

# 分析拦截数据，找到函数调用
for data in intercepted:
    if data.get('type') == 'sign_function':
        print(f"发现签名函数: {data.get('function')}")
```

#### 方法 3: 搜索 window 对象

```python
# 查找可能的加密函数
functions = await page.evaluate("""
    () => {
        const funcs = [];
        for (let key in window) {
            if (typeof window[key] === 'function' && 
                (key.toLowerCase().includes('sign') || 
                 key.toLowerCase().includes('encrypt'))) {
                funcs.push(key);
            }
        }
        return funcs;
    }
""")
print(f"找到的函数: {functions}")
```

### 步骤 3: 通过 JsRpc 调用真实函数

```python
from astra_reverse_core.jsrpc_client import JsRpcClient

# 连接 JsRpc 服务端
client = JsRpcClient(ws_url="ws://localhost:12080")
await client.connect()

# 调用真实网站中的加密函数（函数名通过步骤 2 找到）
params = {"action": "getData", "page": 1}

# 调用网站中的签名函数（假设函数名是 window.sign）
signature = await client.call_function("window.sign", [params])

# 调用网站中的加密函数（假设函数名是 window.encrypt）
encrypted = await client.call_function("window.encrypt", [params])
```

## 实际案例

### 案例：破解得物网站

```python
async def crack_dewu():
    """破解得物网站的加密参数"""
    
    # 1. 访问得物网站
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 注入脚本
        jsrpc_script = load_hook_script("jsrpc_client.js")
        hook_scripts = get_default_hooks()
        for hook in hook_scripts:
            await page.add_init_script(hook)
        await page.add_init_script(jsrpc_script)
        
        # 访问真实网站
        await page.goto("https://www.dewu.com")
        await asyncio.sleep(5)  # 等待网站加载
        
        # 2. 通过 Hook 或开发者工具找到函数名
        # 假设找到的函数名是：window.dewuSign
        
        # 3. 通过 JsRpc 调用
        client = JsRpcClient(ws_url="ws://localhost:12080")
        await client.connect()
        
        # 调用真实网站的签名函数
        params = {
            "keyword": "Nike",
            "page": 1
        }
        
        # 调用网站中的函数（我们不知道具体实现）
        signature = await client.call_function("window.dewuSign", [params])
        
        print(f"签名: {signature}")
        
        await client.disconnect()
        await browser.close()
```

## 关键区别

### ❌ 错误做法（掩耳盗铃）

```python
# 自己定义函数然后调用
await page.evaluate("""
    window.sign = function(params) {
        // 我们自己写的逻辑
        return btoa(JSON.stringify(params));
    };
""")

# 然后调用自己定义的函数
result = await client.call_function("window.sign", [params])
```

**问题**：这不是真实场景，我们不知道网站的真实加密逻辑。

### ✅ 正确做法

```python
# 1. 访问真实网站
await page.goto("https://www.target-site.com")

# 2. 等待网站加载完成（网站会定义自己的加密函数）

# 3. 找到网站中的函数名（通过开发者工具或 Hook）

# 4. 调用网站中已有的函数（我们不知道具体实现）
result = await client.call_function("window.siteSign", [params])
```

**关键**：函数是网站定义的，我们只是调用它。

## 注意事项

1. **等待网站加载**：确保网站的 JS 文件加载完成后再调用函数
2. **函数名可能变化**：网站更新后函数名可能改变
3. **函数可能被混淆**：函数名可能是混淆后的，需要通过 Hook 拦截发现
4. **需要分析网站**：先分析网站找到函数名，再通过 JsRpc 调用

## 参考示例

- `examples/demo_real_site_crack.py` - 真实场景示例（展示如何找到并调用网站函数）
- `examples/demo_get_encrypted_params_with_server.py` - 简化示例（用于测试）

## 总结

**核心思想**：
- ✅ 访问真实网站
- ✅ 找到网站中的加密函数名
- ✅ 通过 JsRpc 调用网站的函数
- ❌ 不要自己定义函数然后调用

