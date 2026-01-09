---
title: 调度中心 (Scheduler)
status: complete
priority: high
assignee: morein
created: 2025-01-27T10:00:00Z
tags:
  - api
  - celery
  - redis
---

# 调度中心 (Scheduler)

## 1. API 接口

### 1.1 任务提交
- **场景**: POST /tasks
- **行为**: 验证 API Key，接收 URL 和参数，将任务推送到 Celery 队列。
- **验证**:
  - 返回 Task ID。
  - 任务状态为 PENDING。

### 1.2 系统状态
- **场景**: GET /status
- **行为**: 连接 Redis，查询各优先级队列的长度。
- **验证**:
  - 返回 `queues` 字典，包含 `high`, `medium`, `low` 的任务数。

## 2. 速率限制 (Rate Limiting)

### 2.1 滑动窗口限流
- **场景**: Worker 发起请求前
- **行为**:
  - 计算当前域名在过去 60 秒内的请求数。
  - 如果超过限制，阻塞等待。
  - 如果未超过，记录当前请求时间戳。
- **验证**:
  - 高并发下，每分钟实际请求数不超过配置值 (默认 60)。
