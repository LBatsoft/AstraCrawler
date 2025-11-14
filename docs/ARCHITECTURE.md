# AstraCrawler 架构文档

## 系统架构

AstraCrawler 采用分布式架构，主要包含以下模块：

```
┌─────────────────┐
│   客户端/API     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  调度中心        │  ← astra_scheduler
│  (Dispatcher)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  任务队列        │  ← Redis/Celery
│  (Queue)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Worker 节点     │  ← astra_farm
│  (Playwright)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  数据处理        │  ← astra_dataflow
│  (Pipeline)     │
└─────────────────┘
```

## 模块说明

### 1. astra_scheduler（调度中心）

**职责**：
- 接收爬取任务请求
- 根据优先级分发任务到不同队列
- 管理任务状态和结果
- 提供 RESTful API 接口

**核心组件**：
- `dispatcher.py`: 任务调度器
- `api.py`: FastAPI 接口服务
- `config.py`: 配置管理

### 2. astra_farm（浏览器工作节点）

**职责**：
- 执行实际的网页爬取任务
- 使用 Playwright 驱动真实浏览器
- 注入 JavaScript 钩子脚本
- 处理异常和重试

**核心组件**：
- `workers/playwright_worker.py`: Playwright Worker 实现
- `config.py`: Worker 配置

### 3. astra_reverse_core（逆向模块）

**职责**：
- 提供 JavaScript 钩子脚本
- 拦截 WebSocket 通信
- Hook 签名生成函数
- 捕获加密参数

**核心组件**：
- `hook_engine.js`: 通用钩子引擎
- `ws_interceptor.js`: WebSocket 拦截器
- `signature_hook.js`: 签名函数 Hook
- `utils.py`: 脚本加载工具

### 4. astra_dataflow（数据处理模块）

**职责**：
- 提取 HTML 内容
- 清洗和格式化数据
- 结构化数据解析
- 数据持久化接口

**核心组件**：
- `extractors/html_extractor.py`: HTML 提取器
- `cleaners/simple_cleaner.py`: 数据清洗器
- `pipeline.py`: 数据处理管道

## 数据流

### 任务提交流程

```
1. 客户端 → POST /tasks → API 服务
2. API → schedule_task() → Dispatcher
3. Dispatcher → send_task() → Celery Queue
4. Celery → 分发任务 → Worker
5. Worker → 执行爬取 → 返回结果
6. 结果 → Redis → 客户端查询
```

### 爬取执行流程

```
1. Worker 接收任务
2. 启动 Playwright 浏览器
3. 注入钩子脚本（可选）
4. 导航到目标 URL
5. 等待页面加载
6. 提取页面内容
7. 数据处理（提取、清洗）
8. 返回结果
```

## 技术栈

- **语言**: Python 3.9+
- **异步框架**: Playwright (async)
- **任务队列**: Celery
- **消息代理**: Redis
- **Web 框架**: FastAPI
- **HTML 解析**: BeautifulSoup4
- **监控**: Flower

## 部署架构

### 开发环境

```
- Redis (本地)
- API 服务 (本地)
- Worker (本地)
- Flower (可选)
```

### 生产环境（Docker）

```
- Redis 容器
- API 服务容器
- Worker 容器（可多个）
- Flower 容器
```

### Kubernetes（可选）

```
- Redis StatefulSet
- API Deployment + Service
- Worker Deployment（可水平扩展）
- Flower Deployment
```

## 扩展性

### 水平扩展

- 可以启动多个 Worker 节点
- 每个 Worker 可以配置不同的并发数
- 支持按队列分配 Worker

### 垂直扩展

- 增加 Worker 并发数
- 优化浏览器资源使用
- 使用更强大的服务器

## 安全考虑

1. **API 认证**: 建议添加 API Key 或 OAuth2
2. **代理支持**: 支持代理池轮换
3. **速率限制**: 避免对目标站点造成压力
4. **错误处理**: 完善的异常处理和重试机制

## 监控指标

- 任务队列长度
- Worker 状态和数量
- 任务执行时间
- 任务成功率
- 系统资源使用率

