"""
速率限制器模块

基于 Redis 的滑动窗口或令牌桶算法实现分布式限流
"""
import time
import logging
import redis
from urllib.parse import urlparse
from typing import Optional

logger = logging.getLogger(__name__)

class RateLimiter:
    """基于 Redis 的分布式速率限制器"""
    
    def __init__(self, redis_url: str):
        """
        初始化限流器
        
        Args:
            redis_url: Redis 连接 URL
        """
        self.redis = redis.from_url(redis_url)
        
    def is_allowed(self, url: str, limit: int = 60, window: int = 60) -> bool:
        """
        检查是否允许请求 (滑动窗口算法)
        
        Args:
            url: 请求 URL (将自动提取域名作为 Key)
            limit: 时间窗口内的最大请求数
            window: 时间窗口大小 (秒)
            
        Returns:
            bool: True 表示允许，False 表示限流
        """
        try:
            domain = urlparse(url).netloc
            key = f"rate_limit:{domain}"
            now = time.time()
            
            pipeline = self.redis.pipeline()
            
            # 1. 移除窗口外的旧记录
            pipeline.zremrangebyscore(key, 0, now - window)
            
            # 2. 获取当前窗口内的请求数
            pipeline.zcard(key)
            
            # 3. 添加当前请求记录 (score=timestamp, member=timestamp)
            # 使用微秒级时间戳作为 member 以避免重复
            pipeline.zadd(key, {str(now): now})
            
            # 4. 设置过期时间 (窗口大小 + 1秒)
            pipeline.expire(key, window + 1)
            
            results = pipeline.execute()
            current_count = results[1]
            
            if current_count < limit:
                return True
            else:
                # 如果超限，需要移除刚才添加的记录（回滚）
                self.redis.zrem(key, str(now))
                logger.warning(f"触发限流: {domain} (当前: {current_count}, 限制: {limit}/{window}s)")
                return False
                
        except Exception as e:
            logger.error(f"限流检查失败: {str(e)}")
            # 故障开放原则：如果 Redis 挂了，默认允许请求，避免阻塞业务
            return True

    def wait_if_needed(self, url: str, limit: int = 60, window: int = 60):
        """
        如果限流则阻塞等待
        """
        while not self.is_allowed(url, limit, window):
            time.sleep(1)


