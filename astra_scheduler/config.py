"""
调度中心配置模块
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """调度中心配置类"""
    
    def __init__(self):
        """初始化配置，设置默认值"""
        # Redis 配置
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        
        # Celery 配置
        default_url = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        self.CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", default_url)
        self.CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", default_url)
        
        # 队列配置
        self.QUEUE_HIGH = "high_priority"
        self.QUEUE_MEDIUM = "medium_priority"
        self.QUEUE_LOW = "low_priority"
        
        # 任务配置
        self.TASK_TIME_LIMIT = 300  # 任务超时时间（秒）
        self.TASK_SOFT_TIME_LIMIT = 240  # 任务软超时时间（秒）
        
        # 结果过期时间（秒）
        self.RESULT_EXPIRES = 3600
        
        # 速率限制配置
        # 默认每域名每分钟最大请求数
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        
        # API 配置
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        # 简单的 API 密钥认证，如果未设置则不启用认证（开发模式）
        self.API_KEY = os.getenv("API_KEY")
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE")


# 全局配置实例
config = Config()
