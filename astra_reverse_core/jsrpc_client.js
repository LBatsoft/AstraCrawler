/**
 * JsRpc 客户端脚本
 * 
 * 用于在浏览器中建立 WebSocket 连接，接收远程 JavaScript 代码并执行
 * 基于 https://github.com/jxhczhl/JsRpc
 */
(function() {
    'use strict';
    
    // JsRpc 客户端配置
    const jsrpcConfig = {
        wsUrl: 'ws://localhost:12080',  // JsRpc 服务端地址
        group: 'default',               // 分组名称
        name: 'astracrawler',           // 客户端名称
        reconnectInterval: 3000,        // 重连间隔（毫秒）
        maxReconnectAttempts: 10        // 最大重连次数
    };
    
    let ws = null;
    let reconnectAttempts = 0;
    let reconnectTimer = null;
    
    // 暴露 ws 到全局，方便调试
    window.__jsrpcWs = null;
    
    /**
     * 连接 WebSocket
     */
    function connect() {
        try {
            ws = new WebSocket(jsrpcConfig.wsUrl);
            window.__jsrpcWs = ws;  // 暴露到全局
            
            ws.onopen = function() {
                console.log('[JsRpc] WebSocket 连接已建立');
                reconnectAttempts = 0;
                
                // 发送注册消息
                const registerMsg = {
                    type: 'register',
                    group: jsrpcConfig.group,
                    name: jsrpcConfig.name
                };
                ws.send(JSON.stringify(registerMsg));
                console.log('[JsRpc] 已发送注册消息:', registerMsg);
            };
            
            ws.onmessage = function(event) {
                try {
                    const message = JSON.parse(event.data);
                    handleMessage(message);
                } catch (e) {
                    console.error('[JsRpc] 消息解析失败:', e);
                }
            };
            
            ws.onerror = function(error) {
                console.error('[JsRpc] WebSocket 错误:', error);
            };
            
            ws.onclose = function() {
                console.log('[JsRpc] WebSocket 连接已关闭');
                ws = null;
                window.__jsrpcWs = null;
                
                // 自动重连
                if (reconnectAttempts < jsrpcConfig.maxReconnectAttempts) {
                    reconnectAttempts++;
                    console.log(`[JsRpc] 尝试重连 (${reconnectAttempts}/${jsrpcConfig.maxReconnectAttempts})...`);
                    reconnectTimer = setTimeout(connect, jsrpcConfig.reconnectInterval);
                } else {
                    console.error('[JsRpc] 达到最大重连次数，停止重连');
                }
            };
            
        } catch (e) {
            console.error('[JsRpc] 连接失败:', e);
        }
    }
    
    /**
     * 处理接收到的消息
     */
    function handleMessage(message) {
        const { type, id, code, functionName, args } = message;
        
        if (type === 'call') {
            // 执行远程调用的 JavaScript 代码
            try {
                let result;
                
                if (functionName) {
                    // 调用指定函数
                    const func = getFunctionByPath(functionName);
                    if (typeof func === 'function') {
                        result = func.apply(window, args || []);
                    } else {
                        throw new Error(`函数不存在: ${functionName}`);
                    }
                } else if (code) {
                    // 执行代码
                    result = eval(code);
                } else {
                    throw new Error('缺少 code 或 functionName 参数');
                }
                
                // 发送执行结果
                sendResponse(id, {
                    success: true,
                    result: result
                });
                
            } catch (error) {
                // 发送错误信息
                sendResponse(id, {
                    success: false,
                    error: error.message,
                    stack: error.stack
                });
            }
        }
    }
    
    /**
     * 根据路径获取函数
     * 例如: "window.sign" -> window.sign
     */
    function getFunctionByPath(path) {
        const parts = path.split('.');
        let obj = window;
        
        for (let i = 0; i < parts.length; i++) {
            if (obj && typeof obj === 'object' && parts[i] in obj) {
                obj = obj[parts[i]];
            } else {
                return null;
            }
        }
        
        return typeof obj === 'function' ? obj : null;
    }
    
    /**
     * 发送响应消息
     */
    function sendResponse(id, data) {
        if (ws && ws.readyState === WebSocket.OPEN) {
            const response = {
                type: 'response',
                id: id,
                ...data
            };
            ws.send(JSON.stringify(response));
        } else {
            console.warn('[JsRpc] WebSocket 未连接，无法发送响应');
        }
    }
    
    /**
     * 手动注册函数到 JsRpc
     */
    window.__jsrpcRegister = function(functionName, func) {
        if (typeof func !== 'function') {
            console.error('[JsRpc] 只能注册函数');
            return;
        }
        
        // 将函数挂载到 window 对象上
        const parts = functionName.split('.');
        let obj = window;
        
        for (let i = 0; i < parts.length - 1; i++) {
            if (!obj[parts[i]]) {
                obj[parts[i]] = {};
            }
            obj = obj[parts[i]];
        }
        
        obj[parts[parts.length - 1]] = func;
        console.log(`[JsRpc] 函数已注册: ${functionName}`);
    };
    
    /**
     * 更新配置
     */
    window.__jsrpcUpdateConfig = function(config) {
        Object.assign(jsrpcConfig, config);
        console.log('[JsRpc] 配置已更新:', jsrpcConfig);
    };
    
    /**
     * 手动连接
     */
    window.__jsrpcConnect = function(url) {
        if (url) {
            jsrpcConfig.wsUrl = url;
        }
        if (ws) {
            ws.close();
        }
        connect();
    };
    
    /**
     * 断开连接
     */
    window.__jsrpcDisconnect = function() {
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
        if (ws) {
            ws.close();
            ws = null;
        }
    };
    
    /**
     * 获取连接状态
     */
    window.__jsrpcGetStatus = function() {
        return {
            connected: ws && ws.readyState === WebSocket.OPEN,
            readyState: ws ? ws.readyState : WebSocket.CLOSED,
            config: jsrpcConfig,
            reconnectAttempts: reconnectAttempts
        };
    };
    
    // 自动连接（延迟一下确保服务端已启动）
    console.log('[JsRpc] 客户端脚本已加载，准备连接...');
    // 使用 setTimeout 延迟连接，确保服务端已启动
    setTimeout(function() {
        console.log('[JsRpc] 开始连接 WebSocket...');
        connect();
    }, 500);
    
    // 导出到全局
    window.__jsrpc = {
        connect: window.__jsrpcConnect,
        disconnect: window.__jsrpcDisconnect,
        register: window.__jsrpcRegister,
        updateConfig: window.__jsrpcUpdateConfig,
        getStatus: window.__jsrpcGetStatus
    };
    
})();

