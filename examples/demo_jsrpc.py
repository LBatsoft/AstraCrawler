"""
JsRpc 使用示例

演示如何在 AstraCrawler 中使用 JsRpc 进行前端加密破解
"""
import asyncio
import time
from playwright.async_api import async_playwright
from astra_reverse_core.jsrpc_client import JsRpcClient
from astra_reverse_core.utils import load_hook_script


async def demo_jsrpc_basic():
    """基础示例：使用 JsRpc 执行 JavaScript 代码"""
    print("=" * 60)
    print("示例 1: JsRpc 基础使用")
    print("=" * 60)
    
    # 注意：此示例需要 JsRpc 服务端运行在 ws://localhost:12080
    # 可以从 https://github.com/jxhczhl/JsRpc 下载并启动服务端
    
    client = JsRpcClient(
        ws_url="ws://localhost:12080",
        group="demo",
        name="demo_client"
    )
    
    try:
        # 连接服务端
        print("正在连接 JsRpc 服务端...")
        connected = await client.connect()
        
        if not connected:
            print("❌ 无法连接到 JsRpc 服务端")
            print("请确保 JsRpc 服务端运行在 ws://localhost:12080")
            return
        
        print("✅ JsRpc 连接成功")
        
        # 执行简单代码
        print("\n执行代码: 1 + 1")
        result = await client.execute_code("1 + 1")
        print(f"结果: {result}")
        
        # 执行复杂代码
        print("\n执行代码: Math.max(1, 5, 3, 9, 2)")
        result = await client.execute_code("Math.max(1, 5, 3, 9, 2)")
        print(f"结果: {result}")
        
        await client.disconnect()
        print("\n✅ 示例完成")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print("\n提示: 请先启动 JsRpc 服务端")


async def demo_jsrpc_with_playwright():
    """示例：在 Playwright 中使用 JsRpc"""
    print("\n" + "=" * 60)
    print("示例 2: Playwright + JsRpc 集成")
    print("=" * 60)
    
    # 加载 JsRpc 客户端脚本
    try:
        jsrpc_script = load_hook_script("jsrpc_client.js")
    except FileNotFoundError:
        print("❌ 找不到 JsRpc 客户端脚本")
        return
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 注入 JsRpc 客户端脚本
        await page.add_init_script(jsrpc_script)
        
        # 导航到测试页面
        print("\n加载测试页面...")
        await page.goto("https://example.com")
        
        # 等待 JsRpc 连接建立
        print("等待 JsRpc 连接建立...")
        await page.wait_for_timeout(3000)
        
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
        else:
            print("⚠️  JsRpc 未加载或未连接")
        
        # 在页面中注册一个测试函数
        await page.evaluate("""
            window.testSignFunction = function(params) {
                // 模拟签名函数
                return btoa(JSON.stringify(params));
            };
        """)
        
        print("\n✅ 测试函数已注册")
        
        # 使用 JsRpc 客户端调用函数
        client = JsRpcClient(ws_url="ws://localhost:12080", group="demo", name="playwright_client")
        
        try:
            await client.connect()
            
            # 调用页面中的函数
            print("\n调用页面函数: testSignFunction({a: 1, b: 2})")
            result = await client.call_function("window.testSignFunction", [{"a": 1, "b": 2}])
            print(f"结果: {result}")
            
            await client.disconnect()
            
        except Exception as e:
            print(f"⚠️  JsRpc 客户端连接失败: {e}")
            print("提示: 请确保 JsRpc 服务端正在运行")
        
        await browser.close()
        print("\n✅ 示例完成")


async def demo_jsrpc_crack_signature():
    """示例：使用 JsRpc 破解签名函数"""
    print("\n" + "=" * 60)
    print("示例 3: 使用 JsRpc 破解签名函数")
    print("=" * 60)
    
    # 模拟场景：目标网站有一个签名函数需要破解
    
    # 1. 启动浏览器并注入 JsRpc
    jsrpc_script = load_hook_script("jsrpc_client.js")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # 注入 JsRpc 和 Hook 脚本
        await page.add_init_script(jsrpc_script)
        
        # 模拟目标网站的签名函数（实际场景中这个函数在目标网站中）
        await page.evaluate("""
            // 模拟目标网站的签名函数
            window.targetSignFunction = function(params) {
                // 模拟复杂的签名逻辑
                const timestamp = Date.now();
                const data = JSON.stringify(params) + timestamp;
                // 简单的 Base64 编码作为示例
                return btoa(data);
            };
        """)
        
        print("✅ 目标页面已加载，签名函数已模拟")
        
        # 导航到目标页面（实际场景中这里是真实的目标网站）
        await page.goto("data:text/html,<html><body><h1>Target Site</h1></body></html>")
        await page.wait_for_timeout(2000)
        
        # 2. 使用 JsRpc 调用签名函数
        client = JsRpcClient(ws_url="ws://localhost:12080", group="crack", name="crack_client")
        
        try:
            await client.connect()
            
            # 测试不同的参数
            test_params = [
                {"action": "getData", "page": 1},
                {"action": "getData", "page": 2},
                {"action": "submit", "data": "test"}
            ]
            
            print("\n测试签名函数:")
            for i, params in enumerate(test_params, 1):
                print(f"\n测试 {i}: {params}")
                signature = await client.call_function("window.targetSignFunction", [params])
                print(f"  签名结果: {signature}")
            
            # 3. 分析签名规律（示例）
            print("\n✅ 签名函数调用成功，可以分析签名规律")
            
            await client.disconnect()
            
        except Exception as e:
            print(f"⚠️  JsRpc 客户端连接失败: {e}")
            print("提示: 请确保 JsRpc 服务端正在运行")
        
        await browser.close()
        print("\n✅ 示例完成")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("AstraCrawler JsRpc 使用示例")
    print("=" * 60)
    print("\n注意: 运行这些示例需要:")
    print("1. JsRpc 服务端运行在 ws://localhost:12080")
    print("2. 可以从 https://github.com/jxhczhl/JsRpc 下载服务端")
    print("\n" + "=" * 60)
    
    # 运行示例
    await demo_jsrpc_basic()
    await demo_jsrpc_with_playwright()
    await demo_jsrpc_crack_signature()
    
    print("\n" + "=" * 60)
    print("所有示例完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

