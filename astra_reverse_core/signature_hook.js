/**
 * 签名函数 Hook
 * 
 * 用于拦截常见的签名生成函数，如 sign、encrypt、generateToken 等
 */

(function() {
    'use strict';
    
    const signatureHooks = {
        intercepted: []
    };
    
    /**
     * Hook 指定对象的签名函数
     */
    function hookSignatureFunction(obj, funcName, context = 'global') {
        if (!obj || typeof obj[funcName] !== 'function') {
            console.warn(`[SignatureHook] 函数不存在: ${context}.${funcName}`);
            return false;
        }
        
        const original = obj[funcName];
        
        obj[funcName] = function(...args) {
            const startTime = Date.now();
            const result = original.apply(this, args);
            const endTime = Date.now();
            
            const interception = {
                context: context,
                function: funcName,
                args: JSON.stringify(args),
                result: typeof result === 'object' ? JSON.stringify(result) : result,
                executionTime: endTime - startTime,
                timestamp: Date.now(),
                stack: new Error().stack
            };
            
            signatureHooks.intercepted.push(interception);
            console.log(`[SignatureHook] 拦截到签名函数调用:`, interception);
            
            return result;
        };
        
        console.log(`[SignatureHook] 已 Hook: ${context}.${funcName}`);
        return true;
    }
    
    /**
     * 批量 Hook 常见签名函数名
     */
    function hookCommonSignFunctions() {
        const commonNames = [
            'sign', 'signature', 'generateSign', 'createSign',
            'encrypt', 'encryptData', 'encryptParams',
            'token', 'generateToken', 'createToken', 'getToken',
            'signature', 'getSignature', 'calcSignature',
            'hash', 'hashParams', 'hashData'
        ];
        
        commonNames.forEach(name => {
            // Hook window 对象
            if (window[name] && typeof window[name] === 'function') {
                hookSignatureFunction(window, name, 'window');
            }
            
            // Hook 常见对象
            const contexts = ['crypto', 'webpackJsonp', '__webpack_require__'];
            contexts.forEach(ctx => {
                if (window[ctx] && window[ctx][name]) {
                    hookSignatureFunction(window[ctx], name, ctx);
                }
            });
        });
    }
    
    /**
     * Hook 特定路径的函数（如 window.xxx.yyy.zzz）
     */
    function hookFunctionByPath(path) {
        const parts = path.split('.');
        let obj = window;
        
        for (let i = 0; i < parts.length - 1; i++) {
            if (!obj[parts[i]]) {
                console.warn(`[SignatureHook] 路径不存在: ${path}`);
                return false;
            }
            obj = obj[parts[i]];
        }
        
        const funcName = parts[parts.length - 1];
        return hookSignatureFunction(obj, funcName, path);
    }
    
    // 导出 API
    window.__astraSignatureHook = {
        hook: hookSignatureFunction,
        hookByPath: hookFunctionByPath,
        hookCommon: hookCommonSignFunctions,
        getIntercepted: function() {
            return signatureHooks.intercepted;
        },
        clear: function() {
            signatureHooks.intercepted = [];
        }
    };
    
    // 自动 Hook 常见函数
    hookCommonSignFunctions();
    
    console.log('[SignatureHook] 签名函数 Hook 已初始化');
})();

