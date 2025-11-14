#!/bin/bash
# AstraCrawler 服务停止脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}停止 AstraCrawler 服务...${NC}"

# 停止 Worker
if [ -f logs/worker.pid ]; then
    echo -e "${GREEN}停止 Worker...${NC}"
    kill $(cat logs/worker.pid) 2>/dev/null || true
    rm logs/worker.pid
fi

# 停止 API
if [ -f logs/api.pid ]; then
    echo -e "${GREEN}停止 API 服务...${NC}"
    kill $(cat logs/api.pid) 2>/dev/null || true
    rm logs/api.pid
fi

# 停止 Flower
if [ -f logs/flower.pid ]; then
    echo -e "${GREEN}停止 Flower...${NC}"
    kill $(cat logs/flower.pid) 2>/dev/null || true
    rm logs/flower.pid
fi

# 清理 Celery 进程
pkill -f "celery.*astra" 2>/dev/null || true
pkill -f "uvicorn.*astra" 2>/dev/null || true

echo -e "${GREEN}所有服务已停止${NC}"

