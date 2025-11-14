"""
任务调度器模块

负责将爬取任务分发到不同优先级的队列
"""
import logging
from typing import Optional, Dict, Any
from celery import Celery
from celery.result import AsyncResult

from .config import config

# 配置日志
logger = logging.getLogger(__name__)

# 创建 Celery 应用实例
celery_app = Celery(
    "astra_scheduler",
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND
)

# 配置 Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_time_limit=config.TASK_TIME_LIMIT,
    task_soft_time_limit=config.TASK_SOFT_TIME_LIMIT,
    result_expires=config.RESULT_EXPIRES,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


def schedule_task(
    url: str,
    priority: str = "medium",
    options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> AsyncResult:
    """
    调度爬取任务到指定优先级队列
    
    Args:
        url: 目标 URL
        priority: 任务优先级，可选值: "high", "medium", "low"
        options: 额外选项，如代理、超时时间等
        **kwargs: 其他参数传递给任务函数
    
    Returns:
        AsyncResult: Celery 任务结果对象
    """
    # 确定目标队列
    queue_map = {
        "high": config.QUEUE_HIGH,
        "medium": config.QUEUE_MEDIUM,
        "low": config.QUEUE_LOW,
    }
    
    queue = queue_map.get(priority.lower(), config.QUEUE_MEDIUM)
    
    # 构建任务参数
    task_kwargs = {
        "url": url,
        "options": options or {},
        **kwargs
    }
    
    # 发送任务到队列
    # 注意：实际的任务函数定义在 astra_farm 模块中
    result = celery_app.send_task(
        "astra_farm.workers.playwright_worker.crawl_page",
        kwargs=task_kwargs,
        queue=queue,
    )
    
    logger.info(
        f"任务已调度: URL={url}, Priority={priority}, "
        f"Queue={queue}, TaskID={result.id}"
    )
    
    return result


def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    查询任务状态
    
    Args:
        task_id: 任务 ID
    
    Returns:
        包含任务状态的字典
    """
    result = AsyncResult(task_id, app=celery_app)
    
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
        "traceback": result.traceback if result.failed() else None,
    }


def get_task_result(task_id: str) -> Optional[Dict[str, Any]]:
    """
    获取任务结果
    
    Args:
        task_id: 任务 ID
    
    Returns:
        任务结果字典，如果任务未完成则返回 None
    """
    result = AsyncResult(task_id, app=celery_app)
    
    if result.ready():
        return result.result
    
    return None

