# 逆向与加密破解指南

本文档介绍如何使用 AstraCrawler 的逆向模块进行前端加密破解和数据拦截。

## 概述

AstraCrawler 的 `astra_reverse_core` 模块提供了 JavaScript 钩子脚本，可以在页面加载前注入到浏览器中，用于：

- 拦截和记录 WebSocket 通信
- 拦截 HTTP 请求（Fetch、XHR）
- Hook 签名生成函数
- 捕获加密参数和算法

## 核心脚本

### 1. hook_engine.js

通用钩子引擎，提供基础的拦截功能：

- **WebSocket 拦截**：自动拦截所有 WebSocket 连接的消息发送和接收
- **Fetch API 拦截**：拦截所有 fetch 请求和响应
- **XMLHttpRequest 拦截**：拦截所有 XHR 请求和响应

### 2. ws_interceptor.js

专门的 WebSocket 拦截器，提供更详细的 WebSocket 通信记录。

### 3. signature_hook.js

签名函数 Hook，用于拦截常见的签名生成函数。

## 使用方法

### 基本使用

```python
from astra_scheduler.dispatcher import schedule_task
from astra_reverse_core.utils import get_default_hooks

# 获取默认钩子脚本
hooks = get_default_hooks()

# 提交带钩子的任务
task = schedule_task(
    url="https://target-site.com",
    priority="high",
    hook_scripts=hooks
)
```

### 自定义钩子脚本

```python
from astra_reverse_core.utils import get_custom_hook

# 加载自定义脚本
custom_script = get_custom_hook("path/to/custom_hook.js")

# 使用自定义脚本
task = schedule_task(
    url="https://target-site.com",
    hook_scripts=[custom_script]
)
```

## 编写自定义钩子脚本

### Hook 特定函数

```javascript
// 在页面加载前注入
(function() {
    // Hook window.sign 函数
    const originalSign = window.sign;
    window.sign = function(params) {
        console.log('签名参数:', params);
        const result = originalSign.call(this, params);
        console.log('签名结果:', result);
        return result;
    };
})();
```

### Hook 对象方法

```javascript
(function() {
    // Hook window.crypto.sign 方法
    const originalSign = window.crypto.sign;
    window.crypto.sign = function(algorithm, key, data) {
        console.log('Crypto sign called:', { algorithm, key, data });
        return originalSign.call(this, algorithm, key, data);
    };
})();
```

### 拦截 WebSocket

```javascript
(function() {
    const OriginalWebSocket = window.WebSocket;
    window.WebSocket = function(url, protocols) {
        const ws = new OriginalWebSocket(url, protocols);
        
        ws.send = function(data) {
            console.log('WS Send:', data);
            return OriginalWebSocket.prototype.send.call(this, data);
        };
        
        ws.addEventListener('message', function(event) {
            console.log('WS Receive:', event.data);
        });
        
        return ws;
    };
})();
```

## 获取拦截数据

钩子脚本会在页面中设置全局变量来存储拦截的数据：

```javascript
// 获取所有拦截的数据
const interceptedData = window.__astraGetInterceptedData();

// 获取 WebSocket 拦截数据
const wsData = window.__astraWSInterceptor.getMessages();

// 获取签名函数拦截数据
const signData = window.__astraSignatureHook.getIntercepted();
```

在爬取任务中，可以通过 `page.evaluate()` 获取这些数据：

```python
# 在 worker 中
intercepted_data = await page.evaluate("() => window.__astraGetInterceptedData()")
```

## 常见场景

### 场景 1：破解签名参数

如果目标站点使用签名验证，需要 Hook 签名生成函数：

```javascript
// Hook 签名函数
window.__astraSignatureHook.hookByPath('window.sign');
// 或
window.__astraSignatureHook.hook(window, 'generateSign', 'window');
```

### 场景 2：拦截 WebSocket 数据

如果目标站点使用 WebSocket 通信：

```javascript
// ws_interceptor.js 已自动安装
// 获取数据：
const messages = window.__astraWSInterceptor.getMessages();
```

### 场景 3：修改请求参数

在发送请求前修改参数：

```javascript
const originalFetch = window.fetch;
window.fetch = function(url, options) {
    // 修改 options
    if (options) {
        options.headers = {
            ...options.headers,
            'X-Custom-Header': 'value'
        };
    }
    return originalFetch.call(this, url, options);
};
```

## 注意事项

1. **执行时机**：钩子脚本在页面加载前注入，确保在目标代码执行前完成 Hook
2. **作用域**：钩子脚本在页面上下文中执行，可以访问页面的所有对象
3. **兼容性**：某些站点可能会检测函数被 Hook，需要更高级的伪装技术
4. **性能**：大量拦截可能影响页面性能，建议根据需要选择性启用

## 进阶技巧

### 绕过检测

某些站点会检测函数是否被修改：

```javascript
// 使用 Object.defineProperty 更隐蔽地 Hook
Object.defineProperty(window, 'sign', {
    get: function() {
        return function(params) {
            // Hook 逻辑
        };
    }
});
```

### 延迟 Hook

如果目标函数在页面加载后才定义：

```javascript
// 使用 MutationObserver 监听 DOM 变化
const observer = new MutationObserver(function(mutations) {
    if (window.targetFunction) {
        // Hook 函数
        hookFunction(window, 'targetFunction');
        observer.disconnect();
    }
});
observer.observe(document, { childList: true, subtree: true });
```

## 示例

完整示例请参考 `examples/demo_with_hooks.py`。

