"""
调度中心 API 服务

提供 RESTful API 接口用于任务提交和状态查询
"""
import logging
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, status, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl, Field

from .dispatcher import schedule_task, get_task_status, get_task_result
from .config import config
import redis

# 配置日志
logger = logging.getLogger(__name__)

# 安全认证
security = HTTPBearer(auto_error=False)

async def verify_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)):
    """验证 API Key"""
    if config.API_KEY:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if credentials.credentials != config.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API Key"
            )
    return credentials

# 创建 FastAPI 应用
app = FastAPI(
    title="AstraCrawler API",
    description="分布式浏览器集群平台 API",
    version="0.1.0"
)


# 请求模型
class CrawlRequest(BaseModel):
    """爬取任务请求模型"""
    url: HttpUrl = Field(..., description="目标 URL")
    priority: str = Field(
        default="medium",
        description="任务优先级",
        pattern="^(high|medium|low)$"
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="额外选项，如代理、超时时间等"
    )


class TaskResponse(BaseModel):
    """任务响应模型"""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """任务状态响应模型"""
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    traceback: Optional[str] = None


class SystemStatusResponse(BaseModel):
    """系统状态响应模型"""
    status: str
    queues: Dict[str, int]
    workers: int


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
async def create_task(request: CrawlRequest):
    """
    提交新的爬取任务
    
    Args:
        request: 爬取任务请求
    
    Returns:
        任务响应，包含任务 ID
    """
    try:
        result = schedule_task(
            url=str(request.url),
            priority=request.priority,
            options=request.options
        )
        
        logger.info(f"API: 新任务已创建 - TaskID={result.id}, URL={request.url}")
        
        return TaskResponse(
            task_id=result.id,
            status=result.status,
            message="任务已成功提交"
        )
    except Exception as e:
        logger.error(f"API: 创建任务失败 - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"任务创建失败: {str(e)}"
        )


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse, dependencies=[Depends(verify_api_key)])
async def get_task(task_id: str):
    """
    查询任务状态
    
    Args:
        task_id: 任务 ID
    
    Returns:
        任务状态信息
    """
    try:
        status_info = get_task_status(task_id)
        return TaskStatusResponse(**status_info)
    except Exception as e:
        logger.error(f"API: 查询任务失败 - TaskID={task_id}, Error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务不存在或查询失败: {str(e)}"
        )


@app.get("/tasks/{task_id}/result", dependencies=[Depends(verify_api_key)])
async def get_result(task_id: str):
    """
    获取任务结果
    
    Args:
        task_id: 任务 ID
    
    Returns:
        任务结果数据
    """
    try:
        result = get_task_result(task_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_202_ACCEPTED,
                detail="任务尚未完成"
            )
        return {"task_id": task_id, "result": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API: 获取结果失败 - TaskID={task_id}, Error={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取结果失败: {str(e)}"
        )


@app.get("/status", response_model=SystemStatusResponse, dependencies=[Depends(verify_api_key)])
async def get_system_status():
    """
    获取系统运行状态
    
    Returns:
        系统状态信息，包括队列长度和 Worker 数量
    """
    try:
        # 这里可以集成 Celery 的 inspect API 获取实际状态
        # 简化版本，返回基础信息
        from .dispatcher import celery_app
        
        inspect = celery_app.control.inspect()
        active_queues = inspect.active_queues() or {}
        active_workers = len(active_queues)
        
        # 获取队列长度（需要 Redis 连接）
        try:
            r = redis.from_url(config.CELERY_BROKER_URL)
            queues = {
                config.QUEUE_HIGH: r.llen(config.QUEUE_HIGH),
                config.QUEUE_MEDIUM: r.llen(config.QUEUE_MEDIUM),
                config.QUEUE_LOW: r.llen(config.QUEUE_LOW),
            }
        except Exception as e:
            logger.error(f"Redis 连接失败: {str(e)}")
            queues = {
                config.QUEUE_HIGH: -1,
                config.QUEUE_MEDIUM: -1,
                config.QUEUE_LOW: -1,
            }
        
        return SystemStatusResponse(
            status="running",
            queues=queues,
            workers=active_workers
        )
    except Exception as e:
        logger.error(f"API: 获取系统状态失败 - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统状态失败: {str(e)}"
        )


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "AstraCrawler API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

