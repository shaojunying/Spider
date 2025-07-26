# Spider Toolkit Makefile
# 提供常用的开发和部署命令

.PHONY: help install install-dev test lint format security clean build docs

# 默认目标
.DEFAULT_GOAL := help

# Python 解释器
PYTHON := python3
PIP := pip3

# 项目目录
PROJECT_DIR := $(shell pwd)
SRC_DIRS := core scrapers automation campus community tools

help: ## 显示帮助信息
	@echo "Spider Toolkit - 开发命令帮助"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装生产依赖
	$(PIP) install -r requirements.txt

install-dev: ## 安装开发依赖
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	pre-commit install

test: ## 运行测试
	pytest tests/ -v --cov=$(SRC_DIRS) --cov-report=term-missing --cov-report=html

test-fast: ## 运行快速测试(跳过慢速和集成测试)
	pytest tests/ -v -m "not slow and not integration"

test-integration: ## 运行集成测试
	pytest tests/ -v -m "integration"

test-slow: ## 运行慢速测试
	pytest tests/ -v -m "slow"

lint: ## 代码质量检查
	@echo "Running flake8..."
	flake8 $(SRC_DIRS) tests/
	@echo "Running mypy..."
	mypy $(SRC_DIRS)/ --ignore-missing-imports
	@echo "Running isort check..."
	isort --check-only --diff $(SRC_DIRS) tests/
	@echo "Running black check..."
	black --check --diff $(SRC_DIRS) tests/

format: ## 代码格式化
	@echo "Running isort..."
	isort $(SRC_DIRS) tests/
	@echo "Running black..."
	black $(SRC_DIRS) tests/

security: ## 安全检查
	@echo "Running bandit..."
	bandit -r $(SRC_DIRS) -f json -o bandit-report.json || true
	@echo "Running safety..."
	safety check --json --output safety-report.json || true

pre-commit: ## 运行pre-commit检查
	pre-commit run --all-files

clean: ## 清理临时文件
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.orig" -delete
	find . -type f -name "*~" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .tox/
	rm -f bandit-report.json
	rm -f safety-report.json

build: ## 构建包
	$(PYTHON) -m build

build-wheel: ## 构建wheel包
	$(PYTHON) -m build --wheel

build-sdist: ## 构建源码包
	$(PYTHON) -m build --sdist

install-package: build ## 本地安装包
	$(PIP) install dist/*.whl --force-reinstall

docs: ## 生成文档
	@echo "Generating documentation..."
	# TODO: 添加文档生成命令

run-house-scraper: ## 运行房价爬虫
	$(PYTHON) scrapers/house_price/anjuke_refactored.py

run-sports-scraper: ## 运行体育数据爬虫示例
	$(PYTHON) scrapers/sports_data/py/1.gymnastics_refactored.py

setup-dev: install-dev ## 设置开发环境
	@echo "Development environment setup complete!"
	@echo "Run 'make help' to see available commands."

check-all: lint test security ## 运行所有检查
	@echo "All checks completed!"

release-check: clean lint test security build ## 发布前检查
	@echo "Release checks completed!"
	@echo "Ready for release!"

# Docker 相关命令
docker-build: ## 构建Docker镜像
	docker build -t spider-toolkit:latest .

docker-run: ## 运行Docker容器
	docker run -it --rm spider-toolkit:latest

# 数据库相关命令
db-setup: ## 设置数据库(如果需要)
	@echo "Setting up database..."
	# TODO: 添加数据库设置命令

# 监控相关命令
monitor-logs: ## 监控日志文件
	tail -f logs/*.log

# 清理输出文件
clean-output: ## 清理输出文件
	rm -rf output/*.csv
	rm -rf output/*.xlsx
	rm -rf output/*.json
	rm -rf logs/*.log