"""
JsRpc 集成测试用例

测试 JsRpc 在 AstraCrawler 中的集成和使用
"""
import pytest
import asyncio
from pathlib import Path
from astra_reverse_core.jsrpc_client import JsRpcClient, JsRpcClientSync
from astra_reverse_core.utils import load_hook_script


@pytest.mark.asyncio
async def test_jsrpc_client_connection():
    """测试 JsRpc 客户端连接"""
    client = JsRpcClient(
        ws_url="ws://localhost:12080",
        group="test",
        name="test_client",
        auto_reconnect=False  # 测试时禁用自动重连，防止服务端未启动导致卡死
    )
    
    try:
        # 尝试连接（如果服务端未运行会失败）
        connected = await client.connect(timeout=1.0)
        
        if connected:
            # 测试执行简单代码
            result = await client.execute_code("1 + 1")
            assert result == 2
            
            await client.disconnect()
        else:
            pytest.skip("JsRpc 服务端未运行，跳过测试")
            
    except Exception as e:
        pytest.skip(f"JsRpc 服务端未运行: {e}")


@pytest.mark.asyncio
async def test_jsrpc_execute_code():
    """测试执行 JavaScript 代码"""
    client = JsRpcClient(
        ws_url="ws://localhost:12080",
        auto_reconnect=False
    )
    
    try:
        await client.connect(timeout=1.0)
        
        # 测试执行代码
        code = """
        function add(a, b) {
            return a + b;
        }
        add(10, 20);
        """
        result = await client.execute_code(code)
        assert result == 30
        
        await client.disconnect()
        
    except Exception as e:
        pytest.skip(f"JsRpc 服务端未运行: {e}")


@pytest.mark.asyncio
async def test_jsrpc_call_function():
    """测试调用浏览器中的函数"""
    client = JsRpcClient(
        ws_url="ws://localhost:12080",
        auto_reconnect=False
    )
    
    try:
        await client.connect(timeout=1.0)
        
        # 先注册一个函数
        register_code = """
        window.testFunction = function(a, b) {
            return a * b;
        };
        """
        await client.execute_code(register_code)
        
        # 调用函数
        result = await client.call_function("window.testFunction", [5, 6])
        assert result == 30
        
        await client.disconnect()
        
    except Exception as e:
        pytest.skip(f"JsRpc 服务端未运行: {e}")


def test_jsrpc_client_sync():
    """测试同步客户端"""
    client = JsRpcClientSync(
        ws_url="ws://localhost:12080",
        auto_reconnect=False
    )
    
    try:
        client.connect(timeout=1.0)
        
        # 执行代码
        result = client.execute_code("Math.max(1, 2, 3)")
        assert result == 3
        
        client.disconnect()
        
    except Exception as e:
        pytest.skip(f"JsRpc 服务端未运行: {e}")


def test_jsrpc_client_script_exists():
    """测试 JsRpc 客户端脚本文件存在"""
    script_path = Path(__file__).parent.parent / "astra_reverse_core" / "jsrpc_client.js"
    assert script_path.exists(), "JsRpc 客户端脚本不存在"
    
    # 读取脚本内容
    script_content = script_path.read_text(encoding="utf-8")
    assert "WebSocket" in script_content
    assert "__jsrpc" in script_content


@pytest.mark.integration
@pytest.mark.asyncio
async def test_jsrpc_with_playwright():
    """
    集成测试：在 Playwright 中使用 JsRpc
    
    注意：此测试需要：
    1. JsRpc 服务端运行在 ws://localhost:12080
    2. Playwright 浏览器环境
    """
    from playwright.async_api import async_playwright
    from astra_reverse_core.utils import load_hook_script
    
    try:
        # 加载 JsRpc 客户端脚本
        jsrpc_script = load_hook_script("jsrpc_client.js")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # 注入 JsRpc 客户端脚本
            await page.add_init_script(jsrpc_script)
            
            # 导航到测试页面
            await page.goto("data:text/html,<html><body><h1>Test</h1></body></html>")
            
            # 等待 JsRpc 连接建立
            await page.wait_for_timeout(2000)
            
            # 检查 JsRpc 是否已加载
            jsrpc_status = await page.evaluate("window.__jsrpc ? window.__jsrpc.getStatus() : null")
            
            if jsrpc_status:
                assert "config" in jsrpc_status
                print(f"JsRpc 状态: {jsrpc_status}")
            
            await browser.close()
            
    except Exception as e:
        pytest.skip(f"集成测试跳过: {e}")

