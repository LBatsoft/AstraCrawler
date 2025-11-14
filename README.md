# AstraCrawler

AstraCrawler 是一个用于高并发网页数据采集与前端加密破解的分布式浏览器集群平台。

## 项目特性

- 🚀 **分布式架构**：基于 Celery 的分布式任务队列，支持高并发爬取
- 🌐 **真实浏览器**：使用 Playwright 驱动真实浏览器，完美模拟用户行为
- 🔓 **加密破解**：支持注入自定义 JavaScript 钩子破解签名参数或截获 WebSocket 数据
- 🔌 **JsRpc 集成**：集成 JsRpc，支持远程调用浏览器中的 JavaScript 函数
- 📊 **数据处理**：内置数据提取、清洗和结构化解析功能
- 🔍 **监控告警**：集成 Flower 监控面板，支持 Prometheus 指标
- 🐳 **容器化部署**：提供 Docker 和 docker-compose 配置，支持 Kubernetes 部署

## 项目结构

```
AstraCrawler/
├── astra_scheduler/      # 调度中心模块
├── astra_farm/          # 浏览器工作节点
├── astra_reverse_core/  # 逆向与加密破解模块
├── astra_dataflow/      # 数据处理模块
├── docs/                # 文档目录
├── examples/            # 示例脚本
├── tests/               # 测试文件
├── docker/              # Docker 配置文件
└── requirements.txt     # 依赖清单
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery 配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# API 配置
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. 启动服务

```bash
# 启动 Redis（如果未运行）
redis-server

# 启动调度中心（终端 1）
celery -A astra_scheduler.dispatcher worker --loglevel=info

# 启动 Worker 节点（终端 2）
celery -A astra_farm.workers.playwright_worker worker --loglevel=info

# 启动 API 服务（终端 3）
uvicorn astra_scheduler.api:app --host 0.0.0.0 --port 8000

# 启动监控面板（终端 4，可选）
celery -A astra_scheduler.dispatcher flower
```

### 4. 使用示例

```python
from astra_scheduler.dispatcher import schedule_task

# 提交爬取任务
task = schedule_task(
    url="https://example.com",
    priority="high"
)
print(f"任务 ID: {task.id}")
```

## 开发指南

详细的开发文档请参考 [docs/](docs/) 目录：

- [快速启动指南](docs/QUICKSTART.md) - 快速开始使用 AstraCrawler
- [架构文档](docs/ARCHITECTURE.md) - 系统架构设计说明
- [逆向指南](docs/REVERSE_GUIDE.md) - JavaScript 钩子使用指南
- [JsRpc 集成指南](docs/JSRPC_GUIDE.md) - JsRpc 使用和集成说明

## 许可证

[待添加]

## 贡献

欢迎提交 Issue 和 Pull Request！

