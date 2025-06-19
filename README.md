# 神秘事件研究系统 (Mystery Event Research System)

🔍 一个基于AI的综合性神秘现象研究平台，集成了多种数据源、分析工具和智能代理，用于系统性地研究和分析各种神秘事件。

## 🌟 主要特性

### 🎯 支持的神秘事件类型
- **UFO目击事件** - 不明飞行物体目击报告和相关证据
- **神秘生物目击** - 大脚怪、尼斯湖水怪等隐秘动物学研究
- **超自然现象** - 鬼魂目击、闹鬼地点、超自然活动
- **古代未解之谜** - 金字塔、巨石阵等古代文明谜团
- **神秘失踪案例** - 百慕大三角、人员失踪等异常事件
- **自然异常现象** - 球状闪电、地磁异常等科学难题

### 🛠️ 核心功能模块

#### 📊 多源数据采集
- **网络爬虫系统** - 专业化爬虫，支持多种网站类型
- **学术数据库检索** - 集成学术搜索引擎和数据库
- **新闻媒体监控** - 实时新闻和媒体报道收集
- **论坛社区挖掘** - 社区讨论和用户生成内容
- **纪录片内容分析** - 视频和纪录片内容提取

#### 🧠 智能分析引擎
- **可信度评估器** - 基于多维度指标的信息可信度分析
- **事件关联分析器** - 发现事件间的潜在关联和模式
- **时间线分析器** - 构建事件时间序列和趋势分析
- **地理位置分析器** - 空间分布和地理模式识别
- **证人证词分析** - 目击者报告的一致性和可靠性评估

#### 🗄️ 数据存储与管理
- **Neo4j图数据库** - 复杂关系存储和图查询
- **Elasticsearch搜索** - 全文搜索和数据索引
- **批量数据处理** - 高效的大规模数据处理
- **数据版本控制** - 数据更新和历史记录管理

#### 🤖 AI驱动的研究工作流
- **多代理协作** - 基于LangGraph的智能代理系统
- **自动化研究流程** - 从数据收集到报告生成的全自动化
- **人机交互界面** - 支持人工干预和反馈
- **自适应学习** - 根据研究结果优化分析策略

## 🏗️ 系统架构

```
神秘事件研究系统
├── 🖥️ 前端界面 (Frontend - Svelte 5)
│   ├── 📊 仪表板 (Dashboard)
│   ├── 🔬 研究管理 (Research Management)
│   ├── 💬 智能对话 (AI Chat)
│   ├── 🕸️ 关系图谱 (Knowledge Graph)
│   ├── ⏰ 时间线 (Timeline)
│   ├── 📋 报告管理 (Reports)
│   └── ⚙️ 系统配置 (Configuration)
├── 🚀 后端API (Backend - FastAPI)
│   ├── 🔌 API路由 (API Routes)
│   ├── 🔄 工作流引擎 (Workflow Engine)
│   ├── 📊 数据处理 (Data Processing)
│   └── 🤖 AI集成 (AI Integration)
├── 🕷️ 数据采集层 (Crawler Layer)
│   ├── 通用爬虫 (Generic Crawler)
│   ├── 学术爬虫 (Academic Crawler)
│   ├── 新闻爬虫 (News Crawler)
│   ├── 论坛爬虫 (Forum Crawler)
│   └── 纪录片爬虫 (Documentary Crawler)
│
├── 🧠 分析处理层 (Analysis Layer)
│   ├── 可信度分析 (Credibility Analysis)
│   ├── 关联分析 (Correlation Analysis)
│   ├── 时间线分析 (Timeline Analysis)
│   ├── 地理分析 (Location Analysis)
│   └── 模式识别 (Pattern Recognition)
│
├── 🗄️ 数据存储层 (Storage Layer)
│   ├── Neo4j 图数据库
│   ├── Elasticsearch 搜索引擎
│   └── 文件系统存储
│
├── 🤖 AI代理层 (Agent Layer)
│   ├── 协调代理 (Coordinator Agent)
│   ├── 规划代理 (Planner Agent)
│   ├── 研究代理 (Researcher Agent)
│   ├── 分析代理 (Analyzer Agent)
│   └── 报告代理 (Reporter Agent)
│
└── 🖥️ 用户界面层 (Interface Layer)
    ├── 命令行界面 (CLI)
    ├── 交互式模式 (Interactive Mode)
    └── 批处理模式 (Batch Mode)
```

## 🚀 快速开始

### 📋 系统要求
- Python 3.8+
- Neo4j 数据库 (可选)
- Elasticsearch (可选)
- 足够的磁盘空间用于数据存储

### 🔧 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd Lingjing

# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置API密钥和数据库连接
```

### 🎮 使用方法

#### 交互模式
```bash
python main.py --interactive
```

#### 单次查询
```bash
python main.py --query "请研究最近的UFO目击事件"
```

#### 运行示例
```bash
# UFO研究示例
python main.py --example ufo

# 神秘生物研究示例
python main.py --example cryptid

# 超自然现象研究示例
python main.py --example paranormal
```

#### 批处理模式
```bash
# 从文件读取查询列表
python main.py --batch queries.txt --output results/
```

#### 启动Web服务
```bash
# 开发模式 - 启动FastAPI服务器
python main.py --mode server --reload

# 生产模式 - 启动Web服务
python main.py --mode server --host 0.0.0.0 --port 8000

# 仅启动研究引擎（命令行模式）
python main.py --mode research --query "研究UFO事件"
```

#### 前端开发
```bash
# 进入前端目录
cd web

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览构建结果
npm run preview
```

#### 查看系统信息
```bash
python main.py --info
```

## 🖥️ Web界面功能

### 📊 仪表板 (Dashboard)
- **系统概览**: 实时显示研究任务状态、数据统计
- **快速操作**: 一键启动常用研究任务
- **性能监控**: 系统资源使用情况和API调用统计

### 🔬 研究管理 (Research Management)
- **任务创建**: 图形化界面创建研究任务
- **进度跟踪**: 实时查看任务执行状态和进度
- **结果查看**: 浏览研究结果和生成的报告
- **任务管理**: 暂停、恢复、删除研究任务

### 💬 智能对话 (AI Chat)
- **多模型支持**: 选择不同的AI模型进行对话
- **上下文记忆**: 保持对话的连续性和上下文
- **快速提示**: 预设的神秘事件研究提示模板
- **对话历史**: 查看和管理历史对话记录

### 🕸️ 关系图谱 (Knowledge Graph)
- **交互式可视化**: 3D图谱展示事件、人物、地点关系
- **节点详情**: 点击查看详细信息和关联数据
- **筛选搜索**: 按类型、时间、关键词筛选节点
- **布局调整**: 多种图谱布局算法和自定义参数

### ⏰ 时间线 (Timeline)
- **事件时序**: 按时间顺序展示研究事件
- **筛选排序**: 按日期范围、事件类型筛选
- **详情查看**: 点击事件查看详细信息
- **导出功能**: 导出时间线数据和图表

### 📋 报告管理 (Reports)
- **报告列表**: 查看所有生成的研究报告
- **在线预览**: 直接在浏览器中查看报告内容
- **多格式导出**: 支持PDF、Word、HTML等格式
- **报告分享**: 生成分享链接和权限管理

### ⚙️ 系统配置 (Configuration)
- **AI模型设置**: 配置不同AI提供商的API密钥和参数
- **爬虫配置**: 设置爬取规则、频率和目标网站
- **数据库连接**: 配置Neo4j、Elasticsearch等数据库
- **报告格式**: 自定义报告模板和输出格式
- **API设置**: 配置速率限制、日志级别等

## 🔌 API文档

### 核心端点

#### 研究任务管理
```http
# 获取任务列表
GET /api/research/tasks

# 创建新任务
POST /api/research/tasks
Content-Type: application/json
{
  "title": "UFO事件研究",
  "description": "研究最近的UFO目击事件",
  "keywords": ["UFO", "目击", "外星人"],
  "priority": "high"
}

# 获取任务详情
GET /api/research/tasks/{task_id}

# 更新任务状态
PUT /api/research/tasks/{task_id}/status
{
  "status": "paused"
}

# 删除任务
DELETE /api/research/tasks/{task_id}
```

#### 智能对话
```http
# 发送消息
POST /api/chat/message
{
  "message": "请分析这个UFO事件的可信度",
  "model": "gpt-4",
  "temperature": 0.7
}

# 获取对话历史
GET /api/chat/history

# 清除对话历史
DELETE /api/chat/history
```

#### 图谱数据
```http
# 获取图谱数据
GET /api/graph/data?type=all&limit=100

# 搜索节点
GET /api/graph/search?q=UFO&type=event
```

#### 报告管理
```http
# 获取报告列表
GET /api/reports

# 生成报告
POST /api/reports/generate
{
  "task_id": "task_123",
  "format": "pdf",
  "include_timeline": true,
  "include_graph": true
}

# 下载报告
GET /api/reports/{report_id}/download

# 删除报告
DELETE /api/reports/{report_id}
```

#### 时间线事件
```http
# 获取时间线事件
GET /api/timeline/events?start_date=2024-01-01&end_date=2024-12-31

# 创建事件
POST /api/timeline/events
{
  "title": "UFO目击事件",
  "date": "2024-03-15",
  "location": "美国内华达州",
  "description": "多名证人目击不明飞行物"
}
```

#### 系统配置
```http
# 获取配置
GET /api/config

# 更新配置
PUT /api/config
{
  "ai_models": {
    "openai_api_key": "sk-...",
    "default_model": "gpt-4"
  },
  "crawler": {
    "max_depth": 3,
    "delay": 1000
  }
}
```

### 访问地址
- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **交互式API**: http://localhost:8000/redoc

## 📝 示例查询

### UFO研究
```
请研究最近5年内的UFO目击事件，特别关注有多个证人的案例，并分析其可信度和地理分布模式。
```

### 神秘生物学
```
调查关于大脚怪(Bigfoot)的最新报告和科学研究，包括DNA证据分析和目击者证词。
```

### 超自然现象
```
分析世界各地著名闹鬼地点的超自然现象报告，评估证据质量并寻找共同模式。
```

### 古代谜团
```
研究古代文明中的未解之谜，如金字塔建造技术、史前巨石阵等，结合考古学和工程学观点。
```

## 🔧 配置选项

### 环境变量
```bash
# API配置
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key

# 数据库配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

ELASTICSEARCH_URL=http://localhost:9200

# 搜索引擎选择
SELECTED_SEARCH_ENGINE=tavily  # tavily, mystery_search, web_search

# RAG提供商
SELECTED_RAG_PROVIDER=neo4j  # neo4j, ragflow
```

### 研究参数
```python
# 工作流配置
max_plan_iterations = 3        # 最大规划迭代次数
max_step_num = 8              # 最大执行步骤数
max_search_results = 10       # 最大搜索结果数

# 功能开关
enable_background_investigation = True   # 背景调查
enable_academic_search = True           # 学术搜索
enable_credibility_filter = True       # 可信度过滤
enable_correlation_analysis = True      # 关联分析
enable_graph_storage = True            # 图数据库存储
```

## 📊 输出格式

### 研究报告结构
```markdown
# 神秘事件研究报告

## 执行摘要
- 研究概述和主要发现

## 研究方法
- 数据来源和分析方法

## 主要发现
- 关键事件和证据

## 可信度分析
- 信息源可信度评估

## 关联分析
- 事件间关系和模式

## 学术资源
- 相关学术研究和论文

## 处理过程
- 详细的处理步骤和观察
```

### 数据结构
```python
# 神秘事件数据模型
class MysteryEvent:
    event_id: str
    event_type: str          # UFO, Cryptid, Paranormal, etc.
    title: str
    description: str
    location: str
    date: str
    credibility_score: float # 0.0 - 1.0
    source_url: str
    witnesses: List[str]
    evidence: List[str]
    metadata: Dict[str, Any]
```

## 🛠️ 开发指南

### 添加新的爬虫
```python
from crawler import Crawler

class CustomCrawler(Crawler):
    async def crawl_url(self, url: str) -> Optional[Document]:
        # 实现自定义爬虫逻辑
        pass
    
    async def search(self, query: str, max_results: int = 10) -> List[str]:
        # 实现搜索功能
        pass
```

### 添加新的分析工具
```python
from tools.decorators import mystery_tool

@mystery_tool
def custom_analyzer_tool(data: Dict[str, Any]) -> Dict[str, Any]:
    """自定义分析工具"""
    # 实现分析逻辑
    return analysis_results
```

### 扩展数据模型
```python
from rag import MysteryEvent

class ExtendedMysteryEvent(MysteryEvent):
    custom_field: str
    additional_metadata: Dict[str, Any]
```

## 📈 性能优化

### 并发处理
- 异步爬虫支持并发数据采集
- 批量数据库操作减少I/O开销
- 智能缓存机制避免重复计算

### 内存管理
- 流式数据处理避免内存溢出
- 分页查询处理大型数据集
- 垃圾回收优化长时间运行

### 数据库优化
- Neo4j索引优化图查询性能
- Elasticsearch分片配置
- 连接池管理数据库连接

## 🔒 安全考虑

### 数据隐私
- 敏感信息脱敏处理
- 用户数据加密存储
- 访问权限控制

### 网络安全
- API密钥安全管理
- 请求频率限制
- 恶意内容过滤

## 🤝 贡献指南

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 多代理工作流框架
- [Neo4j](https://neo4j.com/) - 图数据库支持
- [Elasticsearch](https://www.elastic.co/) - 搜索引擎支持
- [OpenAI](https://openai.com/) - AI模型支持
- [Tavily](https://tavily.com/) - 搜索API支持

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 创建 GitHub Issue
- 发送邮件至项目维护者
- 参与项目讨论区

---

**免责声明**: 本系统仅用于学术研究和教育目的。对于神秘事件的研究结果，请保持科学和理性的态度。系统提供的分析和结论不构成任何形式的科学断言或事实声明。