.PHONY: help install dev-install test lint format clean run-api run-worker run-flower docker-build docker-up docker-down

help:
	@echo "AstraCrawler 开发命令"
	@echo ""
	@echo "安装与设置:"
	@echo "  make install          - 安装依赖"
	@echo "  make dev-install      - 安装开发依赖"
	@echo "  make playwright-install - 安装 Playwright 浏览器"
	@echo ""
	@echo "开发:"
	@echo "  make run-api          - 启动 API 服务"
	@echo "  make run-worker       - 启动 Worker"
	@echo "  make run-flower       - 启动 Flower 监控"
	@echo ""
	@echo "测试与质量:"
	@echo "  make test             - 运行测试"
	@echo "  make lint             - 代码检查"
	@echo "  make format           - 格式化代码"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     - 构建 Docker 镜像"
	@echo "  make docker-up        - 启动 Docker 服务"
	@echo "  make docker-down      - 停止 Docker 服务"
	@echo ""
	@echo "清理:"
	@echo "  make clean            - 清理临时文件"

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install pytest pytest-asyncio black flake8 mypy

playwright-install:
	playwright install chromium

run-api:
	uvicorn astra_scheduler.api:app --host 0.0.0.0 --port 8000 --reload

run-worker:
	celery -A astra_farm.workers.playwright_worker worker --loglevel=info

run-flower:
	celery -A astra_scheduler.dispatcher flower --port=5555

test:
	pytest tests/ -v

lint:
	flake8 astra_scheduler astra_farm astra_reverse_core astra_dataflow
	mypy astra_scheduler astra_farm astra_reverse_core astra_dataflow

format:
	black astra_scheduler astra_farm astra_reverse_core astra_dataflow tests examples

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} +

docker-build:
	cd docker && docker-compose build

docker-up:
	cd docker && docker-compose up -d

docker-down:
	cd docker && docker-compose down

