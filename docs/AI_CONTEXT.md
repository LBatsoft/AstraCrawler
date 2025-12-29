# AstraCrawler AI Context & Memory

> Last Updated: 2025-01-27
> Branch: feat/high-priority-tasks

此文档旨在为 AI 助手提供项目上下文、架构理解和当前开发状态的快照。

## 1. 项目概览

**AstraCrawler** 是一个分布式浏览器集群爬虫系统，专注于：
- 高并发网页采集 (Celery + Redis)
- 真实浏览器模拟 (Playwright)
- 前端加密破解与逆向 (JsRpc + Hook Engine)

### 核心模块
- **astra_scheduler/**: 调度中心。FastAPI 提供接口，Celery 负责任务分发。
- **astra_farm/**: 工作节点。运行 Playwright Browser，执行爬取和 Hook 注入。
- **astra_reverse_core/**: 逆向核心。包含 JS Hook 脚本和 JsRpc 客户端/服务端逻辑。
- **astra_dataflow/**: 数据处理。清洗、提取 pipeline（目前持久化层待实现）。

## 2. 当前开发状态

### 最近变更 (feat/worker-optimization)
已完成 Worker 性能优化和反爬增强：
1.  **等待策略优化**:
    -   默认策略从慢速的 `networkidle` 改为 `domcontentloaded`。
    -   新增 `wait_for_selector` 选项，允许精确等待关键元素。
    -   受影响文件: `astra_farm/workers/playwright_worker.py`
2.  **反爬能力增强**:
    -   集成 `playwright-stealth`，自动隐藏自动化特征。
    -   实现自定义 User-Agent 设置，默认使用现代 Chrome UA。
    -   受影响文件: `astra_farm/workers/playwright_worker.py`, `requirements.txt`

### 最近变更 (feat/high-priority-tasks)
已完成高优先级任务：
1.  **API 认证**: 实现基于 `API_KEY` 的 Bearer Token 认证。
    -   受影响文件: `astra_scheduler/api.py`, `astra_scheduler/config.py`
2.  **系统状态监控**: `/status` 接口集成 Redis `LLEN` 获取真实队列长度。
    -   受影响文件: `astra_scheduler/api.py`
3.  **代码清理**: 修复 `websockets` 库弃用警告，移除遗留兼容代码。
    -   受影响文件: `astra_reverse_core/jsrpc_client.py`

### 待办事项 (ToDo List)

#### 中优先级 (Medium Priority)
- [ ] **数据持久化**: 实现 `astra_dataflow/pipeline.py` 的存储逻辑 (DB/MQ)。
- [ ] **Hook 数据提取**: 在 Worker (`playwright_worker.py`) 中自动提取 `window._hook_data` 并返回。
- [ ] **流控与代理**: 实现请求速率限制和代理池轮换。

#### 低优先级 / 运维
- [ ] **CI/CD**: 添加 GitHub Actions 配置文件。
- [ ] **许可证**: 添加 LICENSE 文件。
- [ ] **监控告警**: 集成 Prometheus/Grafana。

## 3. 关键文件路径索引

| 模块 | 路径 | 说明 |
| :--- | :--- | :--- |
| **Config** | `astra_scheduler/config.py` | 系统全局配置 (Redis, API, Logging) |
| **API** | `astra_scheduler/api.py` | FastAPI 入口，定义 HTTP 接口 |
| **Worker** | `astra_farm/workers/playwright_worker.py` | 爬虫核心逻辑，浏览器控制 |
| **Hook** | `astra_reverse_core/hook_engine.js` | 注入浏览器的 JS 核心 Hook 逻辑 |
| **JsRpc** | `astra_reverse_core/jsrpc_client.py` | Python 端 JsRpc 客户端 |

## 4. 开发备忘录

### 启动命令
```bash
# 调度器
celery -A astra_scheduler.dispatcher worker --loglevel=info

# Worker
celery -A astra_farm.workers.playwright_worker worker --loglevel=info

# API 服务 (需设置 API_KEY)
export API_KEY=secret && uvicorn astra_scheduler.api:app --reload
```

### 环境配置
- `.env` 文件控制所有敏感配置 (Redis URL, API Key 等)。
- 生产环境务必设置 `API_KEY`。

### 代码规范
- 使用 `logging` 模块而不是 `print`。
- 新增依赖需更新 `requirements.txt`。
- 修改 API 需同步更新 Pydantic Model。

