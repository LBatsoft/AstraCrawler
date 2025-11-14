/**
 * AstraCrawler Hook Engine
 * 
 * 通用的 JavaScript 钩子引擎，用于拦截和修改页面行为
 */

(function() {
    'use strict';
    
    // 存储原始函数和拦截数据
    const hooks = {
        originalFunctions: {},
        interceptedData: []
    };
    
    /**
     * 通用函数 Hook 工具
     */
    function hookFunction(obj, funcName, hookCallback) {
        if (!obj || !obj[funcName]) {
            console.warn(`[AstraHook] 函数不存在: ${funcName}`);
            return;
        }
        
        const original = obj[funcName];
        hooks.originalFunctions[funcName] = original;
        
        obj[funcName] = function(...args) {
            const result = hookCallback.call(this, original, ...args);
            return result !== undefined ? result : original.apply(this, args);
        };
        
        console.log(`[AstraHook] 已 Hook: ${funcName}`);
    }
    
    /**
     * Hook WebSocket 构造函数
     */
    function hookWebSocket() {
        const OriginalWebSocket = window.WebSocket;
        
        window.WebSocket = function(url, protocols) {
            const ws = new OriginalWebSocket(url, protocols);
            
            // Hook send 方法
            const originalSend = ws.send;
            ws.send = function(data) {
                hooks.interceptedData.push({
                    type: 'websocket_send',
                    url: url,
                    data: data,
                    timestamp: Date.now()
                });
                console.log('[AstraHook] WebSocket Send:', { url, data });
                return originalSend.call(this, data);
            };
            
            // Hook onmessage
            const originalOnMessage = ws.onmessage;
            Object.defineProperty(ws, 'onmessage', {
                set: function(handler) {
                    ws._onmessage = handler;
                    ws.addEventListener('message', function(event) {
                        hooks.interceptedData.push({
                            type: 'websocket_message',
                            url: url,
                            data: event.data,
                            timestamp: Date.now()
                        });
                        console.log('[AstraHook] WebSocket Message:', { url, data: event.data });
                        if (handler) handler(event);
                    });
                },
                get: function() {
                    return ws._onmessage;
                }
            });
            
            return ws;
        };
        
        // 保持原型链
        window.WebSocket.prototype = OriginalWebSocket.prototype;
        console.log('[AstraHook] WebSocket Hook 已安装');
    }
    
    /**
     * Hook Fetch API
     */
    function hookFetch() {
        hookFunction(window, 'fetch', function(original, ...args) {
            const [url, options] = args;
            hooks.interceptedData.push({
                type: 'fetch_request',
                url: url,
                options: options,
                timestamp: Date.now()
            });
            console.log('[AstraHook] Fetch Request:', { url, options });
            
            return original.apply(this, args).then(response => {
                response.clone().text().then(text => {
                    hooks.interceptedData.push({
                        type: 'fetch_response',
                        url: url,
                        status: response.status,
                        data: text,
                        timestamp: Date.now()
                    });
                    console.log('[AstraHook] Fetch Response:', { url, status: response.status });
                });
                return response;
            });
        });
    }
    
    /**
     * Hook XMLHttpRequest
     */
    function hookXHR() {
        const OriginalXHR = window.XMLHttpRequest;
        
        window.XMLHttpRequest = function() {
            const xhr = new OriginalXHR();
            
            const originalOpen = xhr.open;
            xhr.open = function(method, url, ...rest) {
                xhr._url = url;
                xhr._method = method;
                return originalOpen.call(this, method, url, ...rest);
            };
            
            const originalSend = xhr.send;
            xhr.send = function(data) {
                hooks.interceptedData.push({
                    type: 'xhr_request',
                    method: xhr._method,
                    url: xhr._url,
                    data: data,
                    timestamp: Date.now()
                });
                console.log('[AstraHook] XHR Request:', { method: xhr._method, url: xhr._url, data });
                
                xhr.addEventListener('load', function() {
                    hooks.interceptedData.push({
                        type: 'xhr_response',
                        method: xhr._method,
                        url: xhr._url,
                        status: xhr.status,
                        response: xhr.responseText,
                        timestamp: Date.now()
                    });
                    console.log('[AstraHook] XHR Response:', { url: xhr._url, status: xhr.status });
                });
                
                return originalSend.call(this, data);
            };
            
            return xhr;
        };
        
        window.XMLHttpRequest.prototype = OriginalXHR.prototype;
        console.log('[AstraHook] XMLHttpRequest Hook 已安装');
    }
    
    /**
     * 通用签名函数 Hook
     * 用于拦截常见的签名生成函数
     */
    function hookSignFunction(functionName, context = window) {
        if (!context[functionName]) {
            console.warn(`[AstraHook] 签名函数不存在: ${functionName}`);
            return;
        }
        
        hookFunction(context, functionName, function(original, ...args) {
            const result = original.apply(this, args);
            hooks.interceptedData.push({
                type: 'sign_function',
                function: functionName,
                args: args,
                result: result,
                timestamp: Date.now()
            });
            console.log(`[AstraHook] 签名函数调用: ${functionName}`, { args, result });
            return result;
        });
    }
    
    /**
     * 获取拦截的数据
     */
    window.__astraGetInterceptedData = function() {
        return hooks.interceptedData;
    };
    
    /**
     * 清除拦截的数据
     */
    window.__astraClearInterceptedData = function() {
        hooks.interceptedData = [];
    };
    
    /**
     * 恢复原始函数
     */
    window.__astraRestoreFunction = function(funcName) {
        if (hooks.originalFunctions[funcName]) {
            window[funcName] = hooks.originalFunctions[funcName];
            console.log(`[AstraHook] 已恢复函数: ${funcName}`);
        }
    };
    
    // 自动安装基础 Hooks
    hookWebSocket();
    hookFetch();
    hookXHR();
    
    console.log('[AstraHook] Hook Engine 已初始化');
    
    // 导出 Hook 函数供外部调用
    window.__astraHook = {
        hookFunction: hookFunction,
        hookSignFunction: hookSignFunction,
        hookWebSocket: hookWebSocket,
        hookFetch: hookFetch,
        hookXHR: hookXHR
    };
})();

