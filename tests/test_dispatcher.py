"""
调度器测试
"""
import pytest
from astra_scheduler.dispatcher import schedule_task, get_task_status


@pytest.mark.skip(reason="需要 Redis 和 Celery Worker 运行")
def test_schedule_task():
    """测试任务调度"""
    task = schedule_task(
        url="https://example.com",
        priority="high"
    )
    assert task.id is not None
    assert task.status in ["PENDING", "STARTED"]


@pytest.mark.skip(reason="需要 Redis 和 Celery Worker 运行")
def test_get_task_status():
    """测试获取任务状态"""
    task = schedule_task(
        url="https://example.com",
        priority="medium"
    )
    status = get_task_status(task.id)
    assert "task_id" in status
    assert "status" in status

