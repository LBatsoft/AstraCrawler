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

### 最近变更 (feat/ci-cd)
已完成 CI/CD 流水线配置：
1.  **GitHub Actions**:
    -   创建 `.github/workflows/python-app.yml`。
    -   **CI**: 自动运行 `flake8` 代码检查和 `pytest` 单元测试（排除集成测试）。
    -   **Build**: 自动验证 Docker 镜像构建。
    -   受影响文件: `.github/workflows/python-app.yml`

### 最近变更 (feat/antibot-enhanced)
已完成反爬能力增强：
1.  **动态指纹库**:
    -   新增 `fingerprints.py`，提供多套真实的指纹数据（Windows/Mac/Linux，High/Mid End）。
    -   升级 `cdp_fingerprint.py`，自动注入与 User-Agent 逻辑一致的 `hardwareConcurrency`, `deviceMemory`, `screen`, `WebGL Vendor` 等特征。
    -   受影响文件: `astra_farm/workers/fingerprints.py`, `astra_farm/workers/cdp_fingerprint.py`
2.  **拟人化行为**:
    -   新增 `human_behavior.py`，实现基于贝塞尔曲线的鼠标移动和随机滚动。
    -   在 Worker 中集成，可通过 `options.human_behavior=True` 开启。
    -   受影响文件: `astra_farm/workers/human_behavior.py`, `astra_farm/workers/playwright_worker.py`

### 最近变更 (feat/rate-limit-proxy)
已完成流控与代理池功能：
1.  **速率限制 (Rate Limiting)**:
    -   实现基于 Redis 滑动窗口算法的 `RateLimiter`。
    -   在 Worker 中集成限流逻辑，自动根据域名进行每分钟请求限制。
    -   受影响文件: `astra_scheduler/rate_limiter.py`, `astra_farm/workers/playwright_worker.py`
2.  **简易代理池 (Proxy Pool)**:
    -   实现 `ProxyPool` 模块，支持从环境变量 `PROXY_POOL` 读取代理列表并轮换。
    -   受影响文件: `astra_farm/proxy_pool.py`, `astra_farm/workers/playwright_worker.py`

### 最近变更 (feat/data-loop)
已完成 Hook 数据闭环和基础存储：
1.  **Hook 数据提取**: Worker 自动提取 `window._hook_data`，支持自定义变量名。
    -   受影响文件: `astra_farm/workers/playwright_worker.py`
2.  **数据持久化**: `DataPipeline` 实现 JSONL 本地文件存储，自动按日期分片。
    -   受影响文件: `astra_dataflow/pipeline.py`
3.  **验证脚本**: 新增 `examples/verify_data_loop.py`，验证从注入到存储的全流程。

### 最近变更 (feat/worker-optimization)
已完成 Worker 性能优化和反爬增强：
1.  **等待策略优化**:
    -   默认策略从慢速的 `networkidle` 改为 `domcontentloaded`。
    -   新增 `wait_for_selector` 选项，允许精确等待关键元素。
    -   受影响文件: `astra_farm/workers/playwright_worker.py`
2.  **反爬能力增强**:
    -   集成 `playwright-stealth`，自动隐藏自动化特征。
    -   实现自定义 User-Agent 设置，默认使用现代 Chrome UA。
    -   **底层定制**:
        -   支持 `BROWSER_EXECUTABLE_PATH` 配置，允许加载自定义/去指纹 Chromium 内核。
        -   新增 `cdp_fingerprint.py` 模块，通过 CDP 协议深度注入 UA Client Hints、WebGL 厂商信息。
        -   禁用 `AutomationControlled` 等自动化特征标志。
    -   受影响文件: `astra_farm/workers/playwright_worker.py`, `astra_farm/workers/cdp_fingerprint.py`

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
- [x] **数据持久化**: 实现 `astra_dataflow/pipeline.py` 的存储逻辑 (DB/MQ)。
- [x] **Hook 数据提取**: 在 Worker (`playwright_worker.py`) 中自动提取 `window._hook_data` 并返回。
- [x] **流控与代理**: 实现请求速率限制和代理池轮换。

#### 低优先级 / 运维
- [x] **CI/CD**: 添加 GitHub Actions 配置文件。
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

