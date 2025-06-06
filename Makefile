# 神秘事件研究系统 - Makefile
# 提供常用的开发、测试、部署命令

# ================================
# 变量定义
# ================================
PROJECT_NAME := mystery-research
PYTHON := python
PIP := pip
DOCKER := docker
DOCKER_COMPOSE := docker-compose
VENV_DIR := venv
REQUIREMENTS := requirements.txt
TEST_DIR := tests
COVERAGE_DIR := htmlcov

# 颜色定义
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m
WHITE := \033[37m
RESET := \033[0m

# 默认目标
.DEFAULT_GOAL := help

# ================================
# 帮助信息
# ================================
.PHONY: help
help: ## 显示帮助信息
	@echo "$(CYAN)神秘事件研究系统 - 开发工具$(RESET)"
	@echo "$(CYAN)================================$(RESET)"
	@echo ""
	@echo "$(YELLOW)开发环境:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(install|setup|clean|venv)"
	@echo ""
	@echo "$(YELLOW)代码质量:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(lint|format|test|coverage)"
	@echo ""
	@echo "$(YELLOW)运行和部署:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(run|dev|deploy|docker)"
	@echo ""
	@echo "$(YELLOW)数据库和服务:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -E "(db|service|backup|health)"
	@echo ""
	@echo "$(YELLOW)其他:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST) | grep -vE "(install|setup|clean|venv|lint|format|test|coverage|run|dev|deploy|docker|db|service|backup|health)"

# ================================
# 开发环境设置
# ================================
.PHONY: install
install: ## 安装项目依赖
	@echo "$(BLUE)📦 安装项目依赖...$(RESET)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r $(REQUIREMENTS)
	$(PIP) install -e .
	@echo "$(GREEN)✅ 依赖安装完成$(RESET)"

.PHONY: install-dev
install-dev: ## 安装开发依赖
	@echo "$(BLUE)🛠️ 安装开发依赖...$(RESET)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r $(REQUIREMENTS)
	$(PIP) install -e .
	$(PIP) install pytest pytest-cov black flake8 mypy pre-commit
	@echo "$(GREEN)✅ 开发依赖安装完成$(RESET)"

.PHONY: venv
venv: ## 创建虚拟环境
	@echo "$(BLUE)🐍 创建虚拟环境...$(RESET)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)✅ 虚拟环境创建完成$(RESET)"
	@echo "$(YELLOW)💡 激活虚拟环境: source $(VENV_DIR)/bin/activate (Linux/Mac) 或 $(VENV_DIR)\\Scripts\\activate (Windows)$(RESET)"

.PHONY: setup
setup: venv install-dev ## 完整环境设置
	@echo "$(BLUE)⚙️ 设置开发环境...$(RESET)"
	pre-commit install
	@if [ ! -f .env ]; then cp .env.example .env 2>/dev/null || echo "# 请配置环境变量" > .env; fi
	@echo "$(GREEN)✅ 开发环境设置完成$(RESET)"
	@echo "$(YELLOW)💡 请编辑 .env 文件配置API密钥$(RESET)"

.PHONY: clean
clean: ## 清理临时文件
	@echo "$(BLUE)🧹 清理临时文件...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage $(COVERAGE_DIR)/
	@echo "$(GREEN)✅ 清理完成$(RESET)"

# ================================
# 代码质量
# ================================
.PHONY: lint
lint: ## 代码检查
	@echo "$(BLUE)🔍 执行代码检查...$(RESET)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	mypy . --ignore-missing-imports
	@echo "$(GREEN)✅ 代码检查完成$(RESET)"

.PHONY: format
format: ## 代码格式化
	@echo "$(BLUE)✨ 格式化代码...$(RESET)"
	black . --line-length=100
	@echo "$(GREEN)✅ 代码格式化完成$(RESET)"

.PHONY: format-check
format-check: ## 检查代码格式
	@echo "$(BLUE)🔍 检查代码格式...$(RESET)"
	black . --check --line-length=100
	@echo "$(GREEN)✅ 代码格式检查完成$(RESET)"

.PHONY: test
test: ## 运行测试
	@echo "$(BLUE)🧪 运行测试...$(RESET)"
	pytest $(TEST_DIR)/ -v
	@echo "$(GREEN)✅ 测试完成$(RESET)"

.PHONY: test-quick
test-quick: ## 快速测试
	@echo "$(BLUE)⚡ 快速测试...$(RESET)"
	pytest $(TEST_DIR)/ -v -x --tb=short
	@echo "$(GREEN)✅ 快速测试完成$(RESET)"

.PHONY: coverage
coverage: ## 测试覆盖率
	@echo "$(BLUE)📊 生成测试覆盖率报告...$(RESET)"
	pytest $(TEST_DIR)/ --cov=. --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ 覆盖率报告生成完成$(RESET)"
	@echo "$(YELLOW)💡 查看报告: open $(COVERAGE_DIR)/index.html$(RESET)"

.PHONY: quality
quality: format lint test ## 完整代码质量检查
	@echo "$(GREEN)✅ 代码质量检查完成$(RESET)"

# ================================
# 运行和开发
# ================================
.PHONY: run
run: ## 运行应用
	@echo "$(BLUE)🚀 启动应用...$(RESET)"
	$(PYTHON) main.py

.PHONY: dev
dev: ## 开发模式运行
	@echo "$(BLUE)🛠️ 开发模式启动...$(RESET)"
	$(PYTHON) main.py --debug --reload

.PHONY: demo
demo: ## 运行演示
	@echo "$(BLUE)🎭 运行系统演示...$(RESET)"
	$(PYTHON) demo.py

.PHONY: config-check
config-check: ## 检查配置
	@echo "$(BLUE)⚙️ 检查系统配置...$(RESET)"
	$(PYTHON) -c "from config.validator import validate_config; validate_config()"
	@echo "$(GREEN)✅ 配置检查完成$(RESET)"

# ================================
# Docker相关
# ================================
.PHONY: docker-build
docker-build: ## 构建Docker镜像
	@echo "$(BLUE)🐳 构建Docker镜像...$(RESET)"
	$(DOCKER) build -t $(PROJECT_NAME):latest .
	@echo "$(GREEN)✅ Docker镜像构建完成$(RESET)"

.PHONY: docker-run
docker-run: ## 运行Docker容器
	@echo "$(BLUE)🐳 运行Docker容器...$(RESET)"
	$(DOCKER) run -p 8000:8000 --env-file .env $(PROJECT_NAME):latest

.PHONY: docker-compose-up
docker-compose-up: ## 启动所有服务
	@echo "$(BLUE)🐳 启动所有服务...$(RESET)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✅ 所有服务已启动$(RESET)"
	@echo "$(YELLOW)💡 访问地址:$(RESET)"
	@echo "  - 应用: http://localhost:8000"
	@echo "  - Neo4j: http://localhost:7474"
	@echo "  - Elasticsearch: http://localhost:9200"
	@echo "  - Grafana: http://localhost:3000"
	@echo "  - Kibana: http://localhost:5601"

.PHONY: docker-compose-down
docker-compose-down: ## 停止所有服务
	@echo "$(BLUE)🐳 停止所有服务...$(RESET)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✅ 所有服务已停止$(RESET)"

.PHONY: docker-compose-logs
docker-compose-logs: ## 查看服务日志
	@echo "$(BLUE)📋 查看服务日志...$(RESET)"
	$(DOCKER_COMPOSE) logs -f

.PHONY: docker-clean
docker-clean: ## 清理Docker资源
	@echo "$(BLUE)🧹 清理Docker资源...$(RESET)"
	$(DOCKER) system prune -f
	$(DOCKER) volume prune -f
	@echo "$(GREEN)✅ Docker资源清理完成$(RESET)"

# ================================
# 部署相关
# ================================
.PHONY: deploy-dev
deploy-dev: ## 部署到开发环境
	@echo "$(BLUE)🚀 部署到开发环境...$(RESET)"
	$(PYTHON) deploy.py --env development
	@echo "$(GREEN)✅ 开发环境部署完成$(RESET)"

.PHONY: deploy-prod
deploy-prod: ## 部署到生产环境
	@echo "$(BLUE)🚀 部署到生产环境...$(RESET)"
	$(PYTHON) deploy.py --env production
	@echo "$(GREEN)✅ 生产环境部署完成$(RESET)"

.PHONY: deploy-quick
deploy-quick: ## 快速部署
	@echo "$(BLUE)⚡ 快速部署...$(RESET)"
	$(PYTHON) deploy.py --env development --quick-start
	@echo "$(GREEN)✅ 快速部署完成$(RESET)"

# ================================
# 数据库和服务管理
# ================================
.PHONY: db-init
db-init: ## 初始化数据库
	@echo "$(BLUE)🗄️ 初始化数据库...$(RESET)"
	$(PYTHON) -c "from database import init_databases; init_databases()"
	@echo "$(GREEN)✅ 数据库初始化完成$(RESET)"

.PHONY: db-migrate
db-migrate: ## 数据库迁移
	@echo "$(BLUE)🗄️ 执行数据库迁移...$(RESET)"
	$(PYTHON) -c "from database import migrate_databases; migrate_databases()"
	@echo "$(GREEN)✅ 数据库迁移完成$(RESET)"

.PHONY: db-seed
db-seed: ## 填充示例数据
	@echo "$(BLUE)🌱 填充示例数据...$(RESET)"
	$(PYTHON) -c "from database import seed_data; seed_data()"
	@echo "$(GREEN)✅ 示例数据填充完成$(RESET)"

.PHONY: backup
backup: ## 创建系统备份
	@echo "$(BLUE)💾 创建系统备份...$(RESET)"
	$(PYTHON) deploy.py --backup
	@echo "$(GREEN)✅ 系统备份完成$(RESET)"

.PHONY: restore
restore: ## 恢复系统备份
	@echo "$(BLUE)🔄 恢复系统备份...$(RESET)"
	$(PYTHON) deploy.py --rollback
	@echo "$(GREEN)✅ 系统恢复完成$(RESET)"

.PHONY: health
health: ## 系统健康检查
	@echo "$(BLUE)🏥 执行系统健康检查...$(RESET)"
	$(PYTHON) deploy.py --check-health
	@echo "$(GREEN)✅ 健康检查完成$(RESET)"

# ================================
# 文档和报告
# ================================
.PHONY: docs
docs: ## 生成文档
	@echo "$(BLUE)📚 生成项目文档...$(RESET)"
	@if command -v sphinx-build >/dev/null 2>&1; then \
		sphinx-build -b html docs/ docs/_build/html; \
		echo "$(GREEN)✅ 文档生成完成$(RESET)"; \
		echo "$(YELLOW)💡 查看文档: open docs/_build/html/index.html$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️ Sphinx未安装，跳过文档生成$(RESET)"; \
	fi

.PHONY: api-docs
api-docs: ## 生成API文档
	@echo "$(BLUE)📖 生成API文档...$(RESET)"
	@echo "$(YELLOW)💡 API文档已存在: API.md$(RESET)"

.PHONY: changelog
changelog: ## 生成更新日志
	@echo "$(BLUE)📝 生成更新日志...$(RESET)"
	@if command -v git >/dev/null 2>&1; then \
		git log --oneline --decorate --graph > CHANGELOG.txt; \
		echo "$(GREEN)✅ 更新日志生成完成$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️ Git未安装，跳过更新日志生成$(RESET)"; \
	fi

# ================================
# 监控和日志
# ================================
.PHONY: logs
logs: ## 查看应用日志
	@echo "$(BLUE)📋 查看应用日志...$(RESET)"
	@if [ -f logs/app.log ]; then \
		tail -f logs/app.log; \
	else \
		echo "$(YELLOW)⚠️ 日志文件不存在$(RESET)"; \
	fi

.PHONY: monitor
monitor: ## 启动监控服务
	@echo "$(BLUE)📊 启动监控服务...$(RESET)"
	$(DOCKER_COMPOSE) up -d prometheus grafana
	@echo "$(GREEN)✅ 监控服务已启动$(RESET)"
	@echo "$(YELLOW)💡 Grafana: http://localhost:3000$(RESET)"

.PHONY: stats
stats: ## 显示项目统计
	@echo "$(CYAN)📊 项目统计信息$(RESET)"
	@echo "$(CYAN)==================$(RESET)"
	@echo "Python文件数量: $$(find . -name '*.py' | wc -l)"
	@echo "代码行数: $$(find . -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $$1}')"
	@echo "测试文件数量: $$(find $(TEST_DIR) -name '*.py' | wc -l)"
	@echo "配置文件数量: $$(find config -name '*.yaml' -o -name '*.yml' | wc -l)"
	@echo "Docker镜像大小: $$(docker images $(PROJECT_NAME):latest --format 'table {{.Size}}' | tail -1 2>/dev/null || echo '未构建')"

# ================================
# 实用工具
# ================================
.PHONY: requirements
requirements: ## 更新依赖列表
	@echo "$(BLUE)📦 更新依赖列表...$(RESET)"
	$(PIP) freeze > $(REQUIREMENTS)
	@echo "$(GREEN)✅ 依赖列表已更新$(RESET)"

.PHONY: security
security: ## 安全检查
	@echo "$(BLUE)🔒 执行安全检查...$(RESET)"
	@if command -v safety >/dev/null 2>&1; then \
		safety check; \
		echo "$(GREEN)✅ 安全检查完成$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️ Safety未安装，跳过安全检查$(RESET)"; \
		echo "$(YELLOW)💡 安装: pip install safety$(RESET)"; \
	fi

.PHONY: update
update: ## 更新依赖
	@echo "$(BLUE)🔄 更新项目依赖...$(RESET)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -r $(REQUIREMENTS)
	@echo "$(GREEN)✅ 依赖更新完成$(RESET)"

.PHONY: version
version: ## 显示版本信息
	@echo "$(CYAN)版本信息$(RESET)"
	@echo "$(CYAN)========$(RESET)"
	@$(PYTHON) -c "from __version__ import __version__; print(f'项目版本: {__version__}')"
	@echo "Python版本: $$($(PYTHON) --version)"
	@echo "Pip版本: $$($(PIP) --version)"
	@echo "Docker版本: $$($(DOCKER) --version 2>/dev/null || echo '未安装')"

# ================================
# 特殊目标
# ================================
.PHONY: all
all: clean install quality test ## 完整构建流程
	@echo "$(GREEN)🎉 完整构建流程完成$(RESET)"

.PHONY: ci
ci: install lint test coverage ## CI/CD流程
	@echo "$(GREEN)🎉 CI/CD流程完成$(RESET)"

.PHONY: fresh
fresh: clean setup ## 全新安装
	@echo "$(GREEN)🎉 全新安装完成$(RESET)"

# 防止文件名冲突
.PHONY: *