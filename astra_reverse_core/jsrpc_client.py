"""
JsRpc Python 客户端

用于连接 JsRpc 服务端，远程执行浏览器中的 JavaScript 代码
"""
import json
import asyncio
import logging
from typing import Optional, Dict, Any, Callable
try:
    # 使用新版本 websockets API
    from websockets.client import connect as ws_connect
    from websockets.exceptions import ConnectionClosed
except ImportError:
    # 兼容旧版本 websockets
    try:
        from websockets import connect as ws_connect
        from websockets.exceptions import ConnectionClosed
    except ImportError:
        # 如果都没有，使用 legacy API
        import websockets
        ws_connect = websockets.connect
        ConnectionClosed = websockets.exceptions.ConnectionClosed

logger = logging.getLogger(__name__)


class JsRpcClient:
    """JsRpc 客户端"""
    
    def __init__(
        self,
        ws_url: str = "ws://localhost:12080",
        group: str = "default",
        name: str = "astracrawler"
    ):
        """
        初始化 JsRpc 客户端
        
        Args:
            ws_url: WebSocket 服务端地址
            group: 分组名称
            name: 客户端名称
        """
        self.ws_url = ws_url
        self.group = group
        self.name = name
        self.ws = None
        self.connected = False
        self.call_id = 0
        self.pending_calls = {}
        self.loop = None
        
    async def connect(self):
        """连接到 WebSocket 服务端"""
        try:
            self.ws = await ws_connect(self.ws_url)
            self.connected = True
            
            # 发送注册消息
            register_msg = {
                "type": "register",
                "group": self.group,
                "name": self.name
            }
            await self.ws.send(json.dumps(register_msg))
            
            logger.info(f"JsRpc 客户端已连接: {self.ws_url}")
            
            # 启动消息接收任务
            asyncio.create_task(self._receive_messages())
            
            return True
            
        except Exception as e:
            logger.error(f"JsRpc 连接失败: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self.ws:
            await self.ws.close()
            self.ws = None
            self.connected = False
            logger.info("JsRpc 客户端已断开连接")
    
    async def _receive_messages(self):
        """接收消息"""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logger.error(f"消息解析失败: {message}")
        except ConnectionClosed:
            logger.info("WebSocket 连接已关闭")
            self.connected = False
        except Exception as e:
            logger.error(f"接收消息错误: {e}")
            self.connected = False
    
    async def _handle_message(self, message: Dict[str, Any]):
        """处理接收到的消息"""
        msg_type = message.get("type")
        
        if msg_type == "response":
            # 处理响应消息
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
        function_name: str,
        args: Optional[list] = None,
        timeout: float = 30.0
    ) -> Any:
        """
        调用浏览器中的函数
        
        Args:
            function_name: 函数名（支持路径，如 "window.sign"）
            args: 函数参数列表
            timeout: 超时时间（秒）
        
        Returns:
            函数执行结果
        """
        if not self.connected:
            raise Exception("JsRpc 客户端未连接")
        
        self.call_id += 1
        call_id = self.call_id
        
        # 创建 Future 用于等待响应
        future = asyncio.Future()
        self.pending_calls[call_id] = future
        
        # 发送调用消息
        call_msg = {
            "type": "call",
            "id": call_id,
            "functionName": function_name,
            "args": args or []
        }
        
        try:
            await self.ws.send(json.dumps(call_msg))
            
            # 等待响应
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
            
        except asyncio.TimeoutError:
            self.pending_calls.pop(call_id, None)
            raise Exception(f"调用超时: {function_name}")
        except Exception as e:
            self.pending_calls.pop(call_id, None)
            raise
    
    async def execute_code(
        self,
        code: str,
        timeout: float = 30.0
    ) -> Any:
        """
        执行 JavaScript 代码
        
        Args:
            code: JavaScript 代码字符串
            timeout: 超时时间（秒）
        
        Returns:
            代码执行结果
        """
        if not self.connected:
            raise Exception("JsRpc 客户端未连接")
        
        self.call_id += 1
        call_id = self.call_id
        
        # 创建 Future 用于等待响应
        future = asyncio.Future()
        self.pending_calls[call_id] = future
        
        # 发送执行消息
        call_msg = {
            "type": "call",
            "id": call_id,
            "code": code
        }
        
        try:
            await self.ws.send(json.dumps(call_msg))
            
            # 等待响应
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
            
        except asyncio.TimeoutError:
            self.pending_calls.pop(call_id, None)
            raise Exception(f"代码执行超时")
        except Exception as e:
            self.pending_calls.pop(call_id, None)
            raise
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()


# 同步包装器（用于非异步环境）
class JsRpcClientSync:
    """JsRpc 客户端同步包装器"""
    
    def __init__(self, *args, **kwargs):
        self.client = JsRpcClient(*args, **kwargs)
        self.loop = None
    
    def _ensure_loop(self):
        """确保事件循环存在"""
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
    
    def connect(self):
        """连接（同步）"""
        self._ensure_loop()
        return self.loop.run_until_complete(self.client.connect())
    
    def disconnect(self):
        """断开连接（同步）"""
        if self.loop:
            self.loop.run_until_complete(self.client.disconnect())
    
    def call_function(self, function_name: str, args=None, timeout=30.0):
        """调用函数（同步）"""
        self._ensure_loop()
        return self.loop.run_until_complete(
            self.client.call_function(function_name, args, timeout)
        )
    
    def execute_code(self, code: str, timeout=30.0):
        """执行代码（同步）"""
        self._ensure_loop()
        return self.loop.run_until_complete(
            self.client.execute_code(code, timeout)
        )
    
    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()

