"""
数据闭环验证脚本
模拟：注入 Hook -> 访问页面 -> 拦截数据 -> 管道处理 -> 本地存储
"""
import asyncio
import os
import json
from playwright.async_api import async_playwright
from astra_dataflow.pipeline import DataPipeline

async def verify_data_loop():
    print("🚀 开始验证数据闭环流程...")
    
    # 1. 模拟 Hook 脚本
    # 模拟一个会往 window._hook_data 写入数据的 Hook
    hook_script = """
    window._hook_data = {
        "timestamp": Date.now(),
        "token": "test_token_" + Math.random().toString(36).substring(7),
        "api_response": {
            "id": 123,
            "data": "secret_data"
        }
    };
    console.log("Hook 数据已注入");
    """
    
    # 2. 启动浏览器并执行
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 注入 Hook
        await page.add_init_script(hook_script)
        
        print("🌍 正在访问测试页面...")
        # 访问一个简单的页面
        await page.goto("https://example.com")
        
        # 模拟提取 Hook 数据 (参考 Worker 中的逻辑)
        hook_data = await page.evaluate("window._hook_data")
        print(f"🎣 提取到 Hook 数据: {json.dumps(hook_data, indent=2)}")
        
        # 获取 HTML
        html = await page.content()
        url = page.url
        
        await browser.close()
        
        # 3. 送入数据管道处理
        print("⚙️  正在送入数据管道...")
        # 使用临时目录
        output_dir = "tests/temp_data"
        pipeline = DataPipeline(storage_dir=output_dir)
        
        result = pipeline.process(html, url, hook_data)
        
        # 4. 验证存储结果
        print("💾 验证存储结果...")
        files = os.listdir(output_dir)
        jsonl_files = [f for f in files if f.endswith('.jsonl')]
        
        if jsonl_files:
            latest_file = os.path.join(output_dir, jsonl_files[-1])
            print(f"✅ 发现存储文件: {latest_file}")
            
            with open(latest_file, 'r') as f:
                lines = f.readlines()
                last_line = json.loads(lines[-1])
                
                # 验证关键字段
                assert last_line['url'] == url
                assert last_line['hook_data']['token'] == hook_data['token']
                
                print("🎉 验证成功！数据字段匹配。")
                print(f"   URL: {last_line['url']}")
                print(f"   Token: {last_line['hook_data']['token']}")
        else:
            print("❌ 验证失败：未找到输出文件")

if __name__ == "__main__":
    asyncio.run(verify_data_loop())

