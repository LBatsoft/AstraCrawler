"""
JsRpc 模拟服务端

用于测试的简单 JsRpc WebSocket 服务端实现
基于 JsRpc 协议规范
"""
import asyncio
import json
import logging
from typing import Dict, Set, Optional
import websockets
from websockets.server import WebSocketServerProtocol
try:
    from websockets.server import serve
except ImportError:
    # 兼容旧版本
    from websockets import serve

logger = logging.getLogger(__name__)


class JsRpcMockServer:
    """JsRpc 模拟服务端"""
    
    def __init__(self, host: str = "localhost", port: int = 12080):
        """
        初始化服务端
        
        Args:
            host: 监听地址
            port: 监听端口
        """
        self.host = host
        self.port = port
        self.clients: Dict[str, WebSocketServerProtocol] = {}  # group:name -> websocket
        self.pending_calls: Dict[int, asyncio.Future] = {}
        self.call_id = 0
        
    async def handle_client(self, websocket, path: str):
        """处理客户端连接"""
        client_id = None
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_message(websocket, data, client_id)
                except json.JSONDecodeError:
                    logger.error(f"无效的 JSON 消息: {message}")
                except Exception as e:
                    logger.error(f"处理消息错误: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端断开连接: {client_id}")
        finally:
            # 清理客户端
            if client_id:
                self.clients.pop(client_id, None)
    
    async def handle_message(
        self,
        websocket,
        message: Dict,
        client_id: Optional[str]
    ):
        """处理接收到的消息"""
        msg_type = message.get("type")
        
        if msg_type == "register":
            # 客户端注册
            group = message.get("group", "default")
            name = message.get("name", "unknown")
            client_id = f"{group}:{name}"
            self.clients[client_id] = websocket
            
            logger.info(f"客户端已注册: {client_id}")
            
            # 发送确认消息
            await websocket.send(json.dumps({
                "type": "registered",
                "clientId": client_id
            }))
            
        elif msg_type == "response":
            # 客户端响应（执行结果）
            call_id = message.get("id")
            if call_id in self.pending_calls:
                future = self.pending_calls.pop(call_id)
                if message.get("success"):
                    future.set_result(message.get("result"))
                else:
                    future.set_exception(
                        Exception(message.get("error", "未知错误"))
                    )
    
    async def call_function(
        self,
        client_id: str,
        function_name: str,
        args: Optional[list] = None,
        timeout: float = 30.0
    ) -> any:
        """
        调用客户端函数
        
        Args:
            client_id: 客户端 ID (group:name)
            function_name: 函数名
            args: 函数参数
            timeout: 超时时间
        
        Returns:
            函数执行结果
        """
        if client_id not in self.clients:
            raise Exception(f"客户端未连接: {client_id}")
        
        self.call_id += 1
        call_id = self.call_id
        
        # 创建 Future 等待响应
        future = asyncio.Future()
        self.pending_calls[call_id] = future
        
        # 发送调用消息
        call_msg = {
            "type": "call",
            "id": call_id,
            "functionName": function_name,
            "args": args or []
        }
        
        websocket = self.clients[client_id]
        await websocket.send(json.dumps(call_msg))
        
        # 等待响应
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            self.pending_calls.pop(call_id, None)
            raise Exception(f"调用超时: {function_name}")
    
    async def execute_code(
        self,
        client_id: str,
        code: str,
        timeout: float = 30.0
    ) -> any:
        """
        在客户端执行代码
        
        Args:
            client_id: 客户端 ID
            code: JavaScript 代码
            timeout: 超时时间
        
        Returns:
            代码执行结果
        """
        if client_id not in self.clients:
            raise Exception(f"客户端未连接: {client_id}")
        
        self.call_id += 1
        call_id = self.call_id
        
        # 创建 Future 等待响应
        future = asyncio.Future()
        self.pending_calls[call_id] = future
        
        # 发送执行消息
        call_msg = {
            "type": "call",
            "id": call_id,
            "code": code
        }
        
        websocket = self.clients[client_id]
        await websocket.send(json.dumps(call_msg))
        
        # 等待响应
        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            self.pending_calls.pop(call_id, None)
            raise Exception("代码执行超时")
    
    async def start(self):
        """启动服务端"""
        logger.info(f"JsRpc 模拟服务端启动在 ws://{self.host}:{self.port}")
        async with serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # 永远运行
    
    def get_client_list(self) -> list:
        """获取已连接的客户端列表"""
        return list(self.clients.keys())


async def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    server = JsRpcMockServer(host="localhost", port=12080)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())

