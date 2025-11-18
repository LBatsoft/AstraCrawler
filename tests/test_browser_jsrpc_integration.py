"""
浏览器环境 + JsRpc 集成测试

完整测试浏览器环境和 JsRpc 的集成功能
"""
import asyncio
import logging
import sys
import pytest
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.async_api import async_playwright
from astra_reverse_core.utils import load_hook_script
from tests.jsrpc_mock_server import JsRpcMockServer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_browser_jsrpc_basic():
    """测试 1: 基础浏览器环境 + JsRpc 连接"""
    print("\n" + "=" * 60)
    print("测试 1: 基础浏览器环境 + JsRpc 连接")
    print("=" * 60)
    
    # 启动模拟服务端
    server = JsRpcMockServer(host="localhost", port=12080)
    server_task = asyncio.create_task(server.start())
    
    # 等待服务端启动
    await asyncio.sleep(1)
    
    try:
        # 加载 JsRpc 客户端脚本
        jsrpc_script = load_hook_script("jsrpc_client.js")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            # 注入 JsRpc 客户端脚本
            await page.add_init_script(jsrpc_script)
            
            # 导航到测试页面
            test_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>JsRpc 测试页面</title>
            </head>
            <body>
                <h1>JsRpc 集成测试</h1>
                <p>这是一个测试页面，用于验证 JsRpc 功能。</p>
            </body>
            </html>
            """
            await page.goto(f"data:text/html,{test_html}")
            
            # 等待 JsRpc 连接建立
            print("等待 JsRpc 连接建立...")
            await asyncio.sleep(3)
            
            # 检查 JsRpc 状态
            status = await page.evaluate("""
                () => {
                    if (window.__jsrpc) {
                        return window.__jsrpc.getStatus();
                    }
                    return null;
                }
            """)
            
            if status:
                print(f"✅ JsRpc 状态: {status}")
                assert status.get("connected") == True, "JsRpc 未连接"
            else:
                print("❌ JsRpc 未加载")
                assert False, "JsRpc 客户端未加载"
            
            # 检查服务端是否有客户端连接
            clients = server.get_client_list()
            print(f"✅ 服务端已连接的客户端: {clients}")
            assert len(clients) > 0, "服务端未检测到客户端连接"
            
            await browser.close()
            print("✅ 测试 1 通过")
            
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_jsrpc_execute_code():
    """测试 2: 通过 JsRpc 执行 JavaScript 代码"""
    print("\n" + "=" * 60)
    print("测试 2: 通过 JsRpc 执行 JavaScript 代码")
    print("=" * 60)
    
    server = JsRpcMockServer(host="localhost", port=12080)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(1)
    
    try:
        jsrpc_script = load_hook_script("jsrpc_client.js")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.add_init_script(jsrpc_script)
            await page.goto("data:text/html,<html><body><h1>Test</h1></body></html>")
            await asyncio.sleep(3)
            
            # 获取客户端 ID
            clients = server.get_client_list()
            assert len(clients) > 0, "没有客户端连接"
            client_id = clients[0]
            
            # 测试执行简单代码
            print("测试执行: 1 + 1")
            result = await server.execute_code(client_id, "1 + 1")
            print(f"结果: {result}")
            assert result == 2, f"期望 2，得到 {result}"
            
            # 测试执行复杂代码
            print("测试执行: Math.max(1, 5, 3, 9, 2)")
            result = await server.execute_code(client_id, "Math.max(1, 5, 3, 9, 2)")
            print(f"结果: {result}")
            assert result == 9, f"期望 9，得到 {result}"
            
            # 测试执行函数定义和调用
            code = """
            function add(a, b) {
                return a + b;
            }
            add(10, 20);
            """
            print("测试执行函数: add(10, 20)")
            result = await server.execute_code(client_id, code)
            print(f"结果: {result}")
            assert result == 30, f"期望 30，得到 {result}"
            
            await browser.close()
            print("✅ 测试 2 通过")
            
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_jsrpc_call_function():
    """测试 3: 通过 JsRpc 调用页面中的函数"""
    print("\n" + "=" * 60)
    print("测试 3: 通过 JsRpc 调用页面中的函数")
    print("=" * 60)
    
    server = JsRpcMockServer(host="localhost", port=12080)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(1)
    
    try:
        jsrpc_script = load_hook_script("jsrpc_client.js")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.add_init_script(jsrpc_script)
            
            # 创建测试页面，包含一个签名函数
            test_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>函数调用测试</title>
            </head>
            <body>
                <h1>函数调用测试</h1>
                <script>
                    // 模拟签名函数
                    window.testSignFunction = function(params) {
                        const timestamp = Date.now();
                        const data = JSON.stringify(params) + timestamp;
                        return btoa(data);
                    };
                    
                    // 模拟加密函数
                    window.testEncryptFunction = function(text) {
                        return btoa(text).split('').reverse().join('');
                    };
                </script>
            </body>
            </html>
            """
            await page.goto(f"data:text/html,{test_html}")
            await asyncio.sleep(3)
            
            # 确保函数已定义（通过 evaluate 检查）
            func_defined = await page.evaluate("() => typeof window.testSignFunction === 'function'")
            if not func_defined:
                # 如果函数未定义，直接定义它
                await page.evaluate("""
                    window.testSignFunction = function(params) {
                        const timestamp = Date.now();
                        const data = JSON.stringify(params) + timestamp;
                        return btoa(data);
                    };
                    window.testEncryptFunction = function(text) {
                        return btoa(text).split('').reverse().join('');
                    };
                """)
            
            clients = server.get_client_list()
            assert len(clients) > 0, "没有客户端连接"
            client_id = clients[0]
            
            # 测试调用签名函数
            print("测试调用: testSignFunction({a: 1, b: 2})")
            result = await server.call_function(
                client_id,
                "window.testSignFunction",
                [{"a": 1, "b": 2}]
            )
            print(f"签名结果: {result}")
            assert result is not None, "签名结果为空"
            assert isinstance(result, str), "签名结果应该是字符串"
            
            # 测试调用加密函数
            print("测试调用: testEncryptFunction('hello')")
            result = await server.call_function(
                client_id,
                "window.testEncryptFunction",
                ["hello"]
            )
            print(f"加密结果: {result}")
            assert result is not None, "加密结果为空"
            
            await browser.close()
            print("✅ 测试 3 通过")
            
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_real_world_scenario():
    """测试 4: 真实场景 - 模拟破解签名参数"""
    print("\n" + "=" * 60)
    print("测试 4: 真实场景 - 模拟破解签名参数")
    print("=" * 60)
    
    server = JsRpcMockServer(host="localhost", port=12080)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(1)
    
    try:
        jsrpc_script = load_hook_script("jsrpc_client.js")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.add_init_script(jsrpc_script)
            
            # 模拟真实网站的签名函数
            test_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>真实场景测试</title>
            </head>
            <body>
                <h1>真实场景测试</h1>
                <script>
                    // 模拟真实网站的复杂签名函数
                    window.generateSign = function(params) {
                        // 模拟复杂的签名逻辑
                        const timestamp = Date.now();
                        const nonce = Math.random().toString(36).substring(7);
                        const data = {
                            ...params,
                            timestamp: timestamp,
                            nonce: nonce
                        };
                        const dataStr = JSON.stringify(data);
                        // 简单的 Base64 编码作为签名
                        return btoa(dataStr);
                    };
                    
                    // 模拟获取 Token
                    window.getToken = function() {
                        return 'test_token_' + Date.now();
                    };
                </script>
            </body>
            </html>
            """
            await page.goto(f"data:text/html,{test_html}")
            await asyncio.sleep(3)
            
            # 确保函数已定义
            funcs_defined = await page.evaluate("""
                () => typeof window.getToken === 'function' && 
                      typeof window.generateSign === 'function'
            """)
            if not funcs_defined:
                # 如果函数未定义，直接定义它们
                await page.evaluate("""
                    window.generateSign = function(params) {
                        const timestamp = Date.now();
                        const nonce = Math.random().toString(36).substring(7);
                        const data = {
                            ...params,
                            timestamp: timestamp,
                            nonce: nonce
                        };
                        const dataStr = JSON.stringify(data);
                        return btoa(dataStr);
                    };
                    window.getToken = function() {
                        return 'test_token_' + Date.now();
                    };
                """)
            
            clients = server.get_client_list()
            assert len(clients) > 0, "没有客户端连接"
            client_id = clients[0]
            
            # 场景 1: 获取 Token
            print("\n场景 1: 获取 Token")
            token = await server.call_function(client_id, "window.getToken", [])
            print(f"Token: {token}")
            assert token is not None, "Token 为空"
            
            # 场景 2: 生成签名
            print("\n场景 2: 生成签名")
            test_params = [
                {"action": "getData", "page": 1},
                {"action": "getData", "page": 2},
                {"action": "submit", "data": "test data"}
            ]
            
            for i, params in enumerate(test_params, 1):
                signature = await server.call_function(
                    client_id,
                    "window.generateSign",
                    [params]
                )
                print(f"  参数 {i}: {params}")
                print(f"  签名: {signature}")
                assert signature is not None, f"签名 {i} 为空"
            
            # 场景 3: 批量调用
            print("\n场景 3: 批量调用")
            results = []
            for i in range(5):
                result = await server.execute_code(
                    client_id,
                    f"Math.random() * 100"
                )
                results.append(result)
                print(f"  随机数 {i+1}: {result}")
            
            assert len(results) == 5, "批量调用结果不完整"
            
            await browser.close()
            print("\n✅ 测试 4 通过")
            
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始运行浏览器环境 + JsRpc 集成测试")
    print("=" * 60)
    
    tests = [
        test_browser_jsrpc_basic,
        test_jsrpc_execute_code,
        test_jsrpc_call_function,
        test_real_world_scenario,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ 测试失败: {test_func.__name__}")
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {len(tests)}")
    
    if failed == 0:
        print("\n✅ 所有测试通过！")
    else:
        print(f"\n❌ {failed} 个测试失败")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

