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

#### 查看系统信息
```bash
python main.py --info
```

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