# 快速启动指南

## 前置要求

- Python 3.9 或更高版本
- Redis 服务器
- 足够的系统资源（每个 Worker 需要内存和 CPU）

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd AstraCrawler
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
# 编辑 .env 文件
```

### 5. 启动 Redis

如果本地没有 Redis，可以使用 Docker：

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

或直接安装并启动：

```bash
redis-server
```

## 启动服务

### 方式一：使用启动脚本（推荐）

```bash
./scripts/start_services.sh
```

### 方式二：手动启动

**终端 1 - Worker**:
```bash
celery -A astra_farm.workers.playwright_worker worker --loglevel=info
```

**终端 2 - API 服务**:
```bash
uvicorn astra_scheduler.api:app --host 0.0.0.0 --port 8000
```

**终端 3 - Flower 监控（可选）**:
```bash
celery -A astra_scheduler.dispatcher flower --port=5555
```

## 验证安装

### 1. 检查 API 服务

访问 http://localhost:8000/docs 查看 API 文档

### 2. 检查 Flower 监控

访问 http://localhost:5555 查看任务监控

### 3. 运行示例脚本

```bash
python examples/demo_task.py
```

## 使用 Docker Compose（推荐生产环境）

```bash
cd docker
docker-compose up -d
```

这将启动：
- Redis 服务
- API 服务（端口 8000）
- 2 个 Worker 节点
- Flower 监控（端口 5555）

## 常见问题

### 1. Playwright 浏览器未安装

```bash
playwright install chromium
```

### 2. Redis 连接失败

检查 Redis 是否运行：
```bash
redis-cli ping
```

应该返回 `PONG`

### 3. Worker 无法启动

检查：
- Redis 连接配置是否正确
- 是否有足够的系统资源
- 查看日志文件 `logs/worker.log`

### 4. 端口被占用

修改 `.env` 文件中的端口配置，或停止占用端口的进程

## 下一步

- 阅读 [架构文档](ARCHITECTURE.md) 了解系统设计
- 查看 [逆向指南](REVERSE_GUIDE.md) 学习如何使用钩子脚本
- 运行示例脚本了解基本用法
- 查看 API 文档了解接口详情

