# 神秘事件研究系统 - 部署指南

## 📋 目录

- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [配置设置](#配置设置)
- [数据库设置](#数据库设置)
- [API密钥配置](#api密钥配置)
- [部署选项](#部署选项)
- [性能优化](#性能优化)
- [监控和日志](#监控和日志)
- [故障排除](#故障排除)
- [安全考虑](#安全考虑)

## 🖥️ 系统要求

### 最低要求
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8+
- **内存**: 4GB RAM
- **存储**: 10GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **操作系统**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.10+
- **内存**: 8GB+ RAM
- **存储**: 50GB+ SSD
- **CPU**: 4核心+
- **网络**: 高速宽带连接

### 依赖服务（可选）
- **Neo4j**: 4.4+ (图数据库)
- **Elasticsearch**: 7.0+ (搜索引擎)
- **PostgreSQL**: 12+ (关系数据库)
- **Redis**: 6.0+ (缓存)

## 🚀 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/your-org/mystery-research-system.git
cd mystery-research-system
```

### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 或使用 pip-tools
pip-sync requirements.txt

# 开发环境（包含测试工具）
pip install -r requirements-dev.txt
```

### 4. 安装系统包

```bash
# 安装为可编辑包
pip install -e .

# 或直接安装
python setup.py install
```

### 5. 验证安装

```bash
# 运行配置验证
python -m config.validator

# 运行快速测试
python -m tests.test_system --quick

# 运行演示
python demo.py --validate
```

## ⚙️ 配置设置

### 1. 环境变量配置

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的配置：

```bash
# AI 服务配置
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# 搜索引擎配置
TAVILY_API_KEY=your_tavily_api_key
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id

# 数据库配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# 系统配置
LOG_LEVEL=INFO
DEBUG_MODE=false
DEFAULT_LANGUAGE=zh-CN
```

### 2. 配置文件设置

创建用户配置文件：

```bash
cp config/default.yaml config/user.yaml
```

编辑 `config/user.yaml` 以覆盖默认设置：

```yaml
# 用户自定义配置
system:
  debug: false
  max_workers: 4

ai:
  default_provider: openai
  openai:
    model: gpt-4
    temperature: 0.7
    max_tokens: 2000

search:
  default_engine: tavily
  max_results_per_query: 20

workflow:
  max_plan_iterations: 5
  max_step_num: 20
  features:
    background_investigation: true
    academic_search: true
    credibility_filter: true
    correlation_analysis: true
    graph_storage: true
```

## 🗄️ 数据库设置

### Neo4j 设置（推荐）

1. **安装 Neo4j**:

```bash
# 使用 Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:latest

# 或下载桌面版
# https://neo4j.com/download/
```

2. **配置连接**:

```bash
# 在 .env 文件中设置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

3. **初始化数据库**:

```bash
python -c "from database.neo4j_manager import Neo4jManager; Neo4jManager().initialize_schema()"
```

### Elasticsearch 设置（可选）

1. **安装 Elasticsearch**:

```bash
# 使用 Docker
docker run -d \
  --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  elasticsearch:7.17.0
```

2. **配置连接**:

```bash
# 在 .env 文件中设置
ELASTICSEARCH_URL=http://localhost:9200
```

### PostgreSQL 设置（可选）

1. **安装 PostgreSQL**:

```bash
# 使用 Docker
docker run -d \
  --name postgres \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=mystery_research \
  postgres:13
```

2. **配置连接**:

```bash
# 在 .env 文件中设置
POSTGRES_URL=postgresql://postgres:your_password@localhost:5432/mystery_research
```

## 🔑 API密钥配置

### 获取API密钥

1. **OpenAI API**:
   - 访问 https://platform.openai.com/api-keys
   - 创建新的API密钥
   - 设置 `OPENAI_API_KEY`

2. **Tavily Search API**:
   - 访问 https://tavily.com
   - 注册并获取API密钥
   - 设置 `TAVILY_API_KEY`

3. **Google Search API**:
   - 访问 https://developers.google.com/custom-search/v1/introduction
   - 创建自定义搜索引擎
   - 获取API密钥和搜索引擎ID
   - 设置 `GOOGLE_SEARCH_API_KEY` 和 `GOOGLE_SEARCH_ENGINE_ID`

4. **Anthropic API** (可选):
   - 访问 https://console.anthropic.com
   - 获取API密钥
   - 设置 `ANTHROPIC_API_KEY`

### API密钥安全

- 永远不要将API密钥提交到版本控制
- 使用环境变量或安全的密钥管理服务
- 定期轮换API密钥
- 设置适当的API使用限制

## 🚀 部署选项

### 本地开发部署

```bash
# 启动开发服务器
python main.py --interactive

# 或使用演示模式
python demo.py
```

### Docker 部署

1. **创建 Dockerfile**:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py", "--port", "8000"]
```

2. **构建和运行**:

```bash
# 构建镜像
docker build -t mystery-research-system .

# 运行容器
docker run -d \
  --name mystery-research \
  -p 8000:8000 \
  --env-file .env \
  mystery-research-system
```

3. **使用 Docker Compose**:

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://neo4j:7687
      - ELASTICSEARCH_URL=http://elasticsearch:9200
    depends_on:
      - neo4j
      - elasticsearch
    env_file:
      - .env

  neo4j:
    image: neo4j:latest
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data

  elasticsearch:
    image: elasticsearch:7.17.0
    ports:
      - "9200:9200"
    environment:
      - discovery.type=single-node
    volumes:
      - es_data:/usr/share/elasticsearch/data

volumes:
  neo4j_data:
  es_data:
```

```bash
# 启动所有服务
docker-compose up -d
```

### 云部署

#### AWS 部署

1. **使用 EC2**:
   - 启动 EC2 实例（推荐 t3.medium 或更高）
   - 安装 Docker 和 Docker Compose
   - 部署应用程序

2. **使用 ECS**:
   - 创建 ECS 集群
   - 定义任务定义
   - 创建服务

3. **使用 Lambda**（适用于轻量级查询）:
   - 打包应用程序
   - 创建 Lambda 函数
   - 配置 API Gateway

#### Google Cloud 部署

1. **使用 Compute Engine**:
   - 创建虚拟机实例
   - 安装依赖和应用程序

2. **使用 Cloud Run**:
   - 构建容器镜像
   - 部署到 Cloud Run

#### Azure 部署

1. **使用 Container Instances**:
   - 创建容器组
   - 部署应用程序

2. **使用 App Service**:
   - 创建 Web 应用
   - 部署代码

## ⚡ 性能优化

### 系统优化

```yaml
# config/user.yaml
performance:
  max_memory_mb: 2048
  max_concurrent_requests: 10
  cache_size_mb: 512
  request_timeout: 30
  
crawler:
  max_concurrent_requests: 5
  request_delay: 1.0
  max_retries: 3
  timeout: 15
  
ai:
  batch_size: 5
  max_tokens: 1500
  temperature: 0.7
```

### 缓存配置

```bash
# Redis 缓存
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
CACHE_MAX_SIZE=1000
```

### 数据库优化

```cypher
// Neo4j 索引优化
CREATE INDEX event_title_index FOR (e:MysteryEvent) ON (e.title);
CREATE INDEX event_type_index FOR (e:MysteryEvent) ON (e.event_type);
CREATE INDEX event_date_index FOR (e:MysteryEvent) ON (e.date);
```

## 📊 监控和日志

### 日志配置

```yaml
# config/user.yaml
logging:
  level: INFO
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  file: logs/mystery_research.log
  max_size_mb: 100
  backup_count: 5
  
  loggers:
    crawler: DEBUG
    ai: INFO
    database: WARNING
```

### 监控设置

```bash
# 系统监控
pip install prometheus-client
pip install grafana-api

# 健康检查端点
curl http://localhost:8000/health
```

### 性能监控

```python
# 启用性能监控
ENABLE_METRICS=true
METRICS_PORT=9090
METRICS_PATH=/metrics
```

## 🔧 故障排除

### 常见问题

1. **API密钥错误**:
   ```bash
   # 检查环境变量
   echo $OPENAI_API_KEY
   
   # 验证API密钥
   python -c "import openai; print(openai.api_key)"
   ```

2. **数据库连接失败**:
   ```bash
   # 检查Neo4j连接
   python -c "from database.neo4j_manager import Neo4jManager; Neo4jManager().test_connection()"
   ```

3. **内存不足**:
   ```yaml
   # 减少并发数
   performance:
     max_concurrent_requests: 3
     max_memory_mb: 1024
   ```

4. **网络超时**:
   ```yaml
   # 增加超时时间
   crawler:
     timeout: 30
     request_delay: 2.0
   ```

### 调试模式

```bash
# 启用调试模式
DEBUG_MODE=true
LOG_LEVEL=DEBUG

# 运行调试
python main.py --debug
```

### 日志分析

```bash
# 查看错误日志
grep "ERROR" logs/mystery_research.log

# 查看性能日志
grep "PERFORMANCE" logs/mystery_research.log

# 实时监控日志
tail -f logs/mystery_research.log
```

## 🔒 安全考虑

### API安全

- 使用HTTPS进行所有API通信
- 实施API速率限制
- 验证和清理所有输入
- 使用API密钥轮换

### 数据安全

- 加密敏感数据
- 实施访问控制
- 定期备份数据
- 监控异常访问

### 网络安全

- 使用防火墙限制访问
- 实施VPN访问
- 监控网络流量
- 定期安全审计

### 配置安全

```yaml
# config/user.yaml
security:
  api_rate_limit:
    requests_per_minute: 60
    burst_limit: 10
  
  content_filtering:
    enable_profanity_filter: true
    enable_content_validation: true
  
  encryption:
    enable_data_encryption: true
    encryption_key_rotation_days: 90
  
  access_control:
    enable_ip_whitelist: false
    allowed_ips: []
    enable_user_authentication: false
```

## 📈 扩展和维护

### 定期维护

```bash
# 更新依赖
pip install --upgrade -r requirements.txt

# 清理缓存
python -c "from utils.cache import clear_cache; clear_cache()"

# 数据库维护
python -c "from database.maintenance import run_maintenance; run_maintenance()"
```

### 备份策略

```bash
# 数据库备份
neo4j-admin dump --database=neo4j --to=/backup/neo4j-backup.dump

# 配置备份
cp -r config/ /backup/config-$(date +%Y%m%d)/

# 日志归档
tar -czf /backup/logs-$(date +%Y%m%d).tar.gz logs/
```

### 版本升级

```bash
# 备份当前版本
cp -r . /backup/mystery-research-$(date +%Y%m%d)/

# 拉取新版本
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 运行迁移
python manage.py migrate

# 验证升级
python -m tests.test_system --quick
```

## 📞 支持和帮助

- **文档**: [README.md](README.md)
- **问题报告**: [GitHub Issues](https://github.com/your-org/mystery-research-system/issues)
- **讨论**: [GitHub Discussions](https://github.com/your-org/mystery-research-system/discussions)
- **邮件**: support@mystery-research.com

---

*最后更新: 2024年12月*