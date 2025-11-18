"""
获取加密参数的实际案例

演示如何使用 JsRpc 在实际场景中获取加密参数
模拟真实网站的加密函数调用场景
"""
import asyncio
import logging
import sys
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


async def demo_get_signature_params():
    """案例 1: 获取签名参数"""
    print("\n" + "=" * 70)
    print("案例 1: 获取签名参数")
    print("=" * 70)
    
    # 模拟真实网站的签名函数
    test_page_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>签名参数测试</title>
    </head>
    <body>
        <h1>签名参数测试页面</h1>
        <p>模拟真实网站的加密参数生成</p>
        <script>
            // 模拟真实网站的签名函数（类似得物、淘宝等）
            // 将 script 放在 body 中确保在 DOM 加载后执行
            (function() {
                window.generateSign = function(params) {
                    // 模拟复杂的签名逻辑
                    const timestamp = Date.now();
                    const nonce = Math.random().toString(36).substring(2, 15);
                    
                    // 构建签名数据
                    const signData = {
                        ...params,
                        timestamp: timestamp,
                        nonce: nonce,
                        appKey: 'test_app_key'
                    };
                    
                    // 按 key 排序
                    const sortedKeys = Object.keys(signData).sort();
                    const signString = sortedKeys.map(key => 
                        `${key}=${encodeURIComponent(String(signData[key]))}`
                    ).join('&');
                    
                    // 模拟 MD5 签名（实际使用 btoa 简化，处理中文字符）
                    const sign = btoa(unescape(encodeURIComponent(signString + 'secret_key'))).substring(0, 32);
                    
                    return {
                        sign: sign,
                        timestamp: timestamp,
                        nonce: nonce,
                        ...params
                    };
                };
                
                // 模拟获取 Token
                window.getToken = function() {
                    return {
                        token: 'Bearer_' + btoa(Date.now().toString()).substring(0, 20),
                        expires: Date.now() + 3600000  // 1小时后过期
                    };
                };
            })();
        </script>
    </body>
    </html>
    """
    
    # 启动 JsRpc 模拟服务端
    server = JsRpcMockServer(host="localhost", port=12080)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(3)  # 等待服务端启动  # 等待服务端启动
    
    try:
        # 加载 JsRpc 客户端脚本
        jsrpc_script = load_hook_script("jsrpc_client.js")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # 使用 set_content 设置页面内容
            await page.set_content(test_page_html)
            
            # 在页面加载后注入 JsRpc 客户端脚本
            await page.evaluate(jsrpc_script)
            
            # 等待页面完全加载（包括所有脚本执行）
            await page.wait_for_load_state("load")
            
            # 等待 WebSocket 连接建立
            await asyncio.sleep(2)
            
            # 等待函数定义（必须等待，不使用后备方案）
            try:
                await page.wait_for_function(
                    "() => typeof window.getToken === 'function' && typeof window.generateSign === 'function'",
                    timeout=10000
                )
                print("✅ HTML 中的函数已成功加载")
            except Exception as e:
                # 检查函数是否真的存在
                func_status = await page.evaluate("""
                    () => {
                        return {
                            getToken: typeof window.getToken,
                            generateSign: typeof window.generateSign
                        };
                    }
                """)
                raise Exception(f"HTML 中的函数未加载: {func_status}. 错误: {e}")
            
            # 等待客户端连接并注册（最多等待 15 秒）
            clients = []
            for i in range(15):  # 最多等待 15 次
                clients = server.get_client_list()
                if clients:
                    break
                await asyncio.sleep(1)
                if i % 3 == 0:  # 每3秒打印一次状态
                    print(f"等待客户端连接... ({i+1}/15)")
            
            if not clients:
                raise Exception("❌ 无法连接到 JsRpc 服务端，请检查：\n"
                              "  1. 服务端是否正常启动\n"
                              "  2. 浏览器是否成功注入 JsRpc 客户端脚本\n"
                              "  3. WebSocket 连接是否正常")
            
            client_id = clients[0]
            print(f"✅ JsRpc 连接成功，客户端: {client_id}")
            
            try:
                # 场景 1: 获取 Token
                print("\n【场景 1】获取 Token")
                token_result = await server.call_function(client_id, "window.getToken", [])
                print(f"Token 结果: {token_result}")
                print(f"  - Token: {token_result.get('token')}")
                print(f"  - 过期时间: {token_result.get('expires')}")
                
                # 场景 2: 为不同请求生成签名
                print("\n【场景 2】为不同请求生成签名")
                
                test_requests = [
                    {
                        "action": "getProductList",
                        "page": 1,
                        "pageSize": 20,
                        "category": "electronics"
                    },
                    {
                        "action": "search",
                        "keyword": "手机",
                        "page": 1
                    },
                    {
                        "action": "addToCart",
                        "productId": "12345",
                        "quantity": 2
                    }
                ]
                
                for i, request_params in enumerate(test_requests, 1):
                    print(f"\n请求 {i}: {request_params.get('action')}")
                    sign_result = await server.call_function(
                        client_id,
                        "window.generateSign",
                        [request_params]
                    )
                    print(f"  签名参数:")
                    print(f"    - sign: {sign_result.get('sign')}")
                    print(f"    - timestamp: {sign_result.get('timestamp')}")
                    print(f"    - nonce: {sign_result.get('nonce')}")
                    print(f"    - 完整参数: {sign_result}")
                
                # 场景 3: 批量获取签名（模拟爬取多个页面）
                print("\n【场景 3】批量获取签名（模拟爬取多个页面）")
                batch_results = []
                for page_num in range(1, 6):
                    params = {
                        "action": "getProductList",
                        "page": page_num,
                        "pageSize": 20
                    }
                    sign_result = await server.call_function(
                        client_id,
                        "window.generateSign",
                        [params]
                    )
                    batch_results.append({
                        "page": page_num,
                        "sign": sign_result.get("sign"),
                        "timestamp": sign_result.get("timestamp")
                    })
                    print(f"  页面 {page_num}: sign={sign_result.get('sign')[:20]}...")
                
                print(f"\n✅ 成功获取 {len(batch_results)} 个页面的签名参数")
                
            except Exception as e:
                print(f"❌ 错误: {e}")
            
            await browser.close()
            
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


async def demo_intercept_encryption():
    """案例 2: 拦截并获取加密参数"""
    print("\n" + "=" * 70)
    print("案例 2: 拦截并获取加密参数")
    print("=" * 70)
    
    # 模拟网站有加密函数，我们通过 Hook 拦截
    test_page_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>加密拦截测试</title>
    </head>
    <body>
        <h1>加密拦截测试</h1>
        <script>
            // 模拟网站的加密函数
            // 将 script 放在 body 中确保在 DOM 加载后执行
            (function() {
                window.encryptData = function(data) {
                    // 模拟 AES 加密（简化版）
                    const key = 'secret_key_12345';
                    const encrypted = btoa(JSON.stringify(data) + key)
                        .split('')
                        .reverse()
                        .join('');
                    return encrypted;
                };
                
                // 模拟签名函数
                window.signRequest = function(method, url, data) {
                    const timestamp = Date.now();
                    const signString = `${method}${url}${JSON.stringify(data)}${timestamp}`;
                    const sign = btoa(signString).substring(0, 40);
                    return {
                        'X-Sign': sign,
                        'X-Timestamp': timestamp,
                        'X-Request-Id': Math.random().toString(36).substring(7)
                    };
                };
            })();
        </script>
    </body>
    </html>
    """
    
    # 启动 JsRpc 模拟服务端
    server = JsRpcMockServer(host="localhost", port=12080)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(3)  # 等待服务端启动
    
    try:
        jsrpc_script = load_hook_script("jsrpc_client.js")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 使用 set_content 设置页面内容
            await page.set_content(test_page_html)
            
            # 等待页面完全加载（包括所有脚本执行）
            await page.wait_for_load_state("load")
            
            # 在页面加载后注入 JsRpc 客户端脚本
            await page.evaluate(jsrpc_script)
            
            # 等待 WebSocket 连接建立
            await asyncio.sleep(2)
            
            # 等待函数定义（必须等待，不使用后备方案）
            try:
                await page.wait_for_function(
                    "() => typeof window.encryptData === 'function' && typeof window.signRequest === 'function'",
                    timeout=10000
                )
                print("✅ HTML 中的函数已成功加载")
            except Exception as e:
                # 检查函数是否真的存在
                func_status = await page.evaluate("""
                    () => {
                        return {
                            encryptData: typeof window.encryptData,
                            signRequest: typeof window.signRequest
                        };
                    }
                """)
                raise Exception(f"HTML 中的函数未加载: {func_status}. 错误: {e}")
            
            # 等待客户端连接并注册（最多等待 15 秒）
            clients = []
            for i in range(15):  # 最多等待 15 次
                clients = server.get_client_list()
                if clients:
                    break
                await asyncio.sleep(1)
                if i % 3 == 0:  # 每3秒打印一次状态
                    print(f"等待客户端连接... ({i+1}/15)")
            
            if not clients:
                raise Exception("❌ 无法连接到 JsRpc 服务端，请检查：\n"
                              "  1. 服务端是否正常启动\n"
                              "  2. 浏览器是否成功注入 JsRpc 客户端脚本\n"
                              "  3. WebSocket 连接是否正常")
            
            client_id = clients[0]
            print(f"✅ JsRpc 连接成功，客户端: {client_id}")
            
            try:
                # 场景 1: 加密敏感数据
                print("\n【场景 1】加密敏感数据")
                sensitive_data = {
                    "username": "test_user",
                    "password": "test_password",
                    "email": "test@example.com"
                }
                
                encrypted = await server.call_function(
                    client_id,
                    "window.encryptData",
                    [sensitive_data]
                )
                print(f"原始数据: {sensitive_data}")
                print(f"加密结果: {encrypted}")
                
                # 场景 2: 为 API 请求生成签名头
                print("\n【场景 2】为 API 请求生成签名头")
                api_requests = [
                    {"method": "GET", "url": "/api/products", "data": {}},
                    {"method": "POST", "url": "/api/orders", "data": {"productId": "123"}},
                    {"method": "PUT", "url": "/api/cart", "data": {"action": "update"}}
                ]
                
                for req in api_requests:
                    headers = await server.call_function(
                        client_id,
                        "window.signRequest",
                        [req["method"], req["url"], req["data"]]
                    )
                    print(f"\n请求: {req['method']} {req['url']}")
                    print(f"签名头:")
                    for key, value in headers.items():
                        print(f"  {key}: {value}")
            
            except Exception as e:
                print(f"❌ 错误: {e}")
            
            await browser.close()
            
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


async def demo_real_world_crack():
    """案例 3: 真实场景 - 破解加密参数"""
    print("\n" + "=" * 70)
    print("案例 3: 真实场景 - 破解加密参数")
    print("=" * 70)
    print("模拟破解类似得物、淘宝等网站的加密参数")
    
    # 模拟真实网站的复杂加密逻辑
    test_page_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>真实场景加密破解</title>
    </head>
    <body>
        <h1>真实场景加密破解</h1>
        <script>
            // 模拟真实网站的加密函数（类似得物）
            // 将 script 放在 body 中确保在 DOM 加载后执行
            (function() {
                window.dewuEncrypt = function(params) {
                    const timestamp = Date.now();
                    const deviceId = 'device_' + Math.random().toString(36).substring(7);
                    
                    // 构建加密参数
                    const encryptParams = {
                        ...params,
                        timestamp: timestamp,
                        deviceId: deviceId,
                        version: '1.0.0',
                        platform: 'web'
                    };
                    
                    // 模拟签名算法
                    const keys = Object.keys(encryptParams).sort();
                    let signStr = '';
                    keys.forEach(key => {
                        signStr += `${key}=${encodeURIComponent(String(encryptParams[key]))}&`;
                    });
                    signStr += 'secret=dewu_secret_key';
                    
                    // 模拟 MD5（简化版，处理中文字符）
                    const sign = btoa(unescape(encodeURIComponent(signStr))).substring(0, 32).replace(/[+/=]/g, '');
                    
                    return {
                        ...encryptParams,
                        sign: sign
                    };
                };
                
                // 模拟获取用户 Token
                window.getUserToken = function() {
                    const userId = Math.floor(Math.random() * 1000000);
                    const token = btoa(`user_${userId}_${Date.now()}`).substring(0, 40);
                    return {
                        token: token,
                        userId: userId,
                        expiresIn: 7200
                    };
                };
                
                // 模拟生成请求 ID
                window.generateRequestId = function() {
                    return 'req_' + Date.now() + '_' + Math.random().toString(36).substring(7);
                };
            })();
        </script>
    </body>
    </html>
    """
    
    # 启动 JsRpc 模拟服务端
    server = JsRpcMockServer(host="localhost", port=12080)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(3)  # 等待服务端启动
    
    try:
        jsrpc_script = load_hook_script("jsrpc_client.js")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # 使用 set_content 设置页面内容
            await page.set_content(test_page_html)
            
            # 等待页面完全加载（包括所有脚本执行）
            await page.wait_for_load_state("load")
            
            # 在页面加载后注入 JsRpc 客户端脚本
            await page.evaluate(jsrpc_script)
            
            # 等待 WebSocket 连接建立
            await asyncio.sleep(2)
            
            # 等待函数定义（必须等待，不使用后备方案）
            try:
                await page.wait_for_function(
                    "() => typeof window.dewuEncrypt === 'function' && typeof window.getUserToken === 'function' && typeof window.generateRequestId === 'function'",
                    timeout=10000
                )
                print("✅ HTML 中的函数已成功加载")
            except Exception as e:
                # 检查函数是否真的存在
                func_status = await page.evaluate("""
                    () => {
                        return {
                            dewuEncrypt: typeof window.dewuEncrypt,
                            getUserToken: typeof window.getUserToken,
                            generateRequestId: typeof window.generateRequestId
                        };
                    }
                """)
                raise Exception(f"HTML 中的函数未加载: {func_status}. 错误: {e}")
            
            # 等待客户端连接并注册（最多等待 15 秒）
            clients = []
            for i in range(15):  # 最多等待 15 次
                clients = server.get_client_list()
                if clients:
                    break
                await asyncio.sleep(1)
                if i % 3 == 0:  # 每3秒打印一次状态
                    print(f"等待客户端连接... ({i+1}/15)")
            
            if not clients:
                raise Exception("❌ 无法连接到 JsRpc 服务端，请检查：\n"
                              "  1. 服务端是否正常启动\n"
                              "  2. 浏览器是否成功注入 JsRpc 客户端脚本\n"
                              "  3. WebSocket 连接是否正常")
            
            client_id = clients[0]
            print(f"✅ JsRpc 连接成功，客户端: {client_id}")
            
            try:
                # 步骤 1: 获取用户 Token
                print("\n【步骤 1】获取用户 Token")
                user_token = await server.call_function(client_id, "window.getUserToken", [])
                print(f"✅ Token 获取成功:")
                print(f"  - Token: {user_token.get('token')}")
                print(f"  - UserID: {user_token.get('userId')}")
                print(f"  - 过期时间: {user_token.get('expiresIn')} 秒")
                
                # 步骤 2: 为搜索请求生成加密参数
                print("\n【步骤 2】为搜索请求生成加密参数")
                search_params = {
                    "keyword": "Nike 运动鞋",
                    "page": 1,
                    "pageSize": 20,
                    "sort": "price_asc"
                }
                
                encrypted_search = await server.call_function(
                    client_id,
                    "window.dewuEncrypt",
                    [search_params]
                )
                print(f"✅ 搜索参数加密成功:")
                print(f"  - 关键词: {search_params['keyword']}")
                print(f"  - 签名: {encrypted_search.get('sign')}")
                print(f"  - 时间戳: {encrypted_search.get('timestamp')}")
                print(f"  - 设备ID: {encrypted_search.get('deviceId')}")
                print(f"  - 完整参数: {encrypted_search}")
                
                # 步骤 3: 为商品详情请求生成加密参数
                print("\n【步骤 3】为商品详情请求生成加密参数")
                product_params = {
                    "productId": "123456789",
                    "skuId": "987654321"
                }
                
                encrypted_product = await server.call_function(
                    client_id,
                    "window.dewuEncrypt",
                    [product_params]
                )
                print(f"✅ 商品参数加密成功:")
                print(f"  - 商品ID: {product_params['productId']}")
                print(f"  - 签名: {encrypted_product.get('sign')}")
                
                # 步骤 4: 生成请求 ID（用于追踪）
                print("\n【步骤 4】生成请求 ID")
                request_id = await server.call_function(client_id, "window.generateRequestId", [])
                print(f"✅ 请求ID: {request_id}")
                
                # 步骤 5: 构建完整的请求头
                print("\n【步骤 5】构建完整的请求头")
                headers = {
                    "Authorization": f"Bearer {user_token.get('token')}",
                    "X-Sign": encrypted_search.get('sign'),
                    "X-Timestamp": str(encrypted_search.get('timestamp')),
                    "X-Request-Id": request_id,
                    "X-Device-Id": encrypted_search.get('deviceId'),
                    "Content-Type": "application/json"
                }
                
                print("✅ 完整请求头:")
                for key, value in headers.items():
                    print(f"  {key}: {value}")
                
                # 步骤 6: 模拟批量请求（爬取多个页面）
                print("\n【步骤 6】模拟批量请求（爬取多个页面）")
                batch_requests = []
                for page_num in range(1, 4):
                    page_params = {
                        "keyword": "Nike 运动鞋",
                        "page": page_num,
                        "pageSize": 20
                    }
                    encrypted = await server.call_function(
                        client_id,
                        "window.dewuEncrypt",
                        [page_params]
                    )
                    batch_requests.append({
                        "page": page_num,
                        "sign": encrypted.get("sign"),
                        "timestamp": encrypted.get("timestamp")
                    })
                
                print(f"✅ 成功生成 {len(batch_requests)} 个页面的加密参数")
                for req in batch_requests:
                    print(f"  页面 {req['page']}: sign={req['sign'][:20]}...")
                
            except Exception as e:
                print(f"❌ 错误: {e}")
                import traceback
                traceback.print_exc()
            
            await browser.close()
            
            print("\n" + "=" * 70)
            print("✅ 加密参数获取完成！")
            print("=" * 70)
            print("\n现在可以使用这些加密参数发送真实的 API 请求了。")
            
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


async def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("AstraCrawler - 获取加密参数案例演示")
    print("=" * 70)
    print("\n注意: 运行这些案例需要 JsRpc 服务端运行在 ws://localhost:12080")
    print("可以运行: python tests/jsrpc_mock_server.py")
    print("\n" + "=" * 70)
    
    # 运行所有案例
    await demo_get_signature_params()
    await demo_intercept_encryption()
    await demo_real_world_crack()
    
    print("\n" + "=" * 70)
    print("所有案例演示完成！")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

