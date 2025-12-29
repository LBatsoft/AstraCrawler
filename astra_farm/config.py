"""
浏览器工作节点配置模块
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class WorkerConfig:
    """Worker 配置类"""
    
    def __init__(self):
        """初始化配置"""
        # Celery 配置（与调度中心保持一致）
        self.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        self.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        self.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        
        default_url = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        self.CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", default_url)
        self.CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", default_url)
        
        # Worker 配置
        self.WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))
        self.WORKER_PREFETCH_MULTIPLIER = int(
            os.getenv("WORKER_PREFETCH_MULTIPLIER", "1")
        )
        
        # 浏览器配置
        self.BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"
        self.BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))  # 毫秒
        
        # 浏览器底层定制配置
        # 指定自定义 Chromium 可执行文件路径（如指纹浏览器内核）
        self.BROWSER_EXECUTABLE_PATH = os.getenv("BROWSER_EXECUTABLE_PATH")
        # 自定义启动参数（逗号分隔），例如: --disable-blink-features=AutomationControlled
        self.BROWSER_ARGS = os.getenv("BROWSER_ARGS", "").split(",") if os.getenv("BROWSER_ARGS") else []
        
        # 代理配置
        self.PROXY_URL = os.getenv("PROXY_URL")
        self.PROXY_USERNAME = os.getenv("PROXY_USERNAME")
        self.PROXY_PASSWORD = os.getenv("PROXY_PASSWORD")
        
        # 重试配置
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        self.RETRY_DELAY = int(os.getenv("RETRY_DELAY", "60"))  # 秒
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE")


# 全局配置实例
worker_config = WorkerConfig()

