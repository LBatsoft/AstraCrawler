#!/bin/bash
# AstraCrawler 服务启动脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}启动 AstraCrawler 服务...${NC}"

# 检查 Redis 是否运行
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}警告: Redis 未运行，请先启动 Redis${NC}"
    echo "可以使用: redis-server 或 docker run -d -p 6379:6379 redis:7-alpine"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 启动 Worker（后台运行）
echo -e "${GREEN}启动 Worker...${NC}"
celery -A astra_farm.workers.playwright_worker worker \
    --loglevel=info \
    --concurrency=4 \
    --logfile=logs/worker.log \
    --pidfile=logs/worker.pid \
    --detach

# 启动 API 服务（后台运行）
echo -e "${GREEN}启动 API 服务...${NC}"
uvicorn astra_scheduler.api:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-config=logging.conf \
    > logs/api.log 2>&1 &

echo $! > logs/api.pid

# 启动 Flower（可选，后台运行）
echo -e "${GREEN}启动 Flower 监控面板...${NC}"
celery -A astra_scheduler.dispatcher flower \
    --port=5555 \
    --logfile=logs/flower.log \
    --pidfile=logs/flower.pid \
    --detach

echo -e "${GREEN}所有服务已启动！${NC}"
echo ""
echo "服务地址:"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Flower: http://localhost:5555"
echo ""
echo "日志文件:"
echo "  - Worker: logs/worker.log"
echo "  - API: logs/api.log"
echo "  - Flower: logs/flower.log"
echo ""
echo "停止服务: ./scripts/stop_services.sh"

