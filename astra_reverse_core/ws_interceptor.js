/**
 * WebSocket 拦截器
 * 
 * 专门用于拦截和记录 WebSocket 通信
 */

(function() {
    'use strict';
    
    const wsInterceptor = {
        connections: [],
        messages: []
    };
    
    const OriginalWebSocket = window.WebSocket;
    
    window.WebSocket = function(url, protocols) {
        const ws = new OriginalWebSocket(url, protocols);
        const connectionId = Date.now() + Math.random();
        
        const connection = {
            id: connectionId,
            url: url,
            protocols: protocols,
            readyState: ws.readyState,
            messages: []
        };
        
        wsInterceptor.connections.push(connection);
        
        // Hook send
        const originalSend = ws.send;
        ws.send = function(data) {
            const message = {
                type: 'send',
                data: data,
                timestamp: Date.now()
            };
            connection.messages.push(message);
            wsInterceptor.messages.push({
                connectionId: connectionId,
                ...message
            });
            console.log('[WSInterceptor] Send:', message);
            return originalSend.call(this, data);
        };
        
        // Hook message events
        ws.addEventListener('message', function(event) {
            const message = {
                type: 'receive',
                data: event.data,
                timestamp: Date.now()
            };
            connection.messages.push(message);
            wsInterceptor.messages.push({
                connectionId: connectionId,
                ...message
            });
            console.log('[WSInterceptor] Receive:', message);
        });
        
        // Hook open event
        ws.addEventListener('open', function(event) {
            connection.readyState = WebSocket.OPEN;
            console.log('[WSInterceptor] Connection opened:', connectionId);
        });
        
        // Hook close event
        ws.addEventListener('close', function(event) {
            connection.readyState = WebSocket.CLOSED;
            connection.closeCode = event.code;
            connection.closeReason = event.reason;
            console.log('[WSInterceptor] Connection closed:', connectionId);
        });
        
        // Hook error event
        ws.addEventListener('error', function(event) {
            connection.error = true;
            console.error('[WSInterceptor] Connection error:', connectionId, event);
        });
        
        return ws;
    };
    
    // 保持原型链
    window.WebSocket.prototype = OriginalWebSocket.prototype;
    
    // 导出 API
    window.__astraWSInterceptor = {
        getConnections: function() {
            return wsInterceptor.connections;
        },
        getMessages: function() {
            return wsInterceptor.messages;
        },
        getConnectionMessages: function(connectionId) {
            const connection = wsInterceptor.connections.find(c => c.id === connectionId);
            return connection ? connection.messages : [];
        },
        clear: function() {
            wsInterceptor.connections = [];
            wsInterceptor.messages = [];
        }
    };
    
    console.log('[WSInterceptor] WebSocket 拦截器已安装');
})();

