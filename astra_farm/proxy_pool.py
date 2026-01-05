"""
简易代理池模块

提供代理轮换和健康检查功能
"""
import random
import logging
import os
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class ProxyPool:
    """简易代理池"""
    
    def __init__(self, proxy_list: List[str] = None):
        """
        初始化代理池
        
        Args:
            proxy_list: 代理列表，格式 ["http://user:pass@ip:port", ...]
        """
        self.proxies = proxy_list or []
        # 如果未提供列表，尝试从环境变量读取 (逗号分隔)
        if not self.proxies and os.getenv("PROXY_POOL"):
            self.proxies = [p.strip() for p in os.getenv("PROXY_POOL").split(",") if p.strip()]
            
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        随机获取一个代理配置
        
        Returns:
            Dict: Playwright 代理配置格式 {"server": "...", "username": "...", "password": "..."}
        """
        if not self.proxies:
            return None
            
        proxy_url = random.choice(self.proxies)
        return self._parse_proxy(proxy_url)
        
    def _parse_proxy(self, proxy_url: str) -> Dict[str, str]:
        """解析代理 URL 为 Playwright 格式"""
        try:
            # 简单解析逻辑，支持 http://user:pass@ip:port 或 http://ip:port
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            
            config = {
                "server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"
            }
            
            if parsed.username and parsed.password:
                config["username"] = parsed.username
                config["password"] = parsed.password
                
            return config
        except Exception as e:
            logger.error(f"代理解析失败 {proxy_url}: {e}")
            return {"server": proxy_url}

# 全局单例
proxy_pool = ProxyPool()

