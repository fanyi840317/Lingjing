# 贡献指南 (Contributing Guide)

感谢您对神秘事件研究系统的关注！我们欢迎所有形式的贡献，包括但不限于代码、文档、测试、反馈和建议。

## 🤝 贡献方式

### 🐛 报告问题

如果您发现了bug或有功能建议，请：

1. 检查 [Issues](https://github.com/your-username/mystery-research/issues) 确保问题未被报告
2. 使用适当的Issue模板创建新Issue
3. 提供详细的描述和复现步骤
4. 包含相关的系统信息和日志

### 💡 功能请求

对于新功能建议：

1. 在Issue中详细描述功能需求
2. 解释功能的用途和价值
3. 提供可能的实现方案
4. 考虑向后兼容性

### 📝 文档改进

文档贡献包括：

- 修复错别字和语法错误
- 改进现有文档的清晰度
- 添加缺失的文档
- 翻译文档到其他语言
- 添加使用示例和教程

### 🔧 代码贡献

代码贡献流程：

1. Fork 项目仓库
2. 创建功能分支
3. 进行开发和测试
4. 提交Pull Request

## 🛠️ 开发环境设置

### 前置要求

- Python 3.8+
- Git
- 推荐使用虚拟环境

### 快速设置

```bash
# 1. Fork并克隆项目
git clone https://github.com/your-username/mystery-research.git
cd mystery-research

# 2. 设置开发环境
make setup

# 3. 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 4. 验证安装
make test
```

### 手动设置

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 2. 安装开发依赖
pip install -r requirements.txt
pip install -e .
pip install pytest pytest-cov black flake8 mypy pre-commit

# 3. 设置pre-commit钩子
pre-commit install

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件
```

## 📋 开发规范

### 代码风格

我们使用以下工具确保代码质量：

- **Black**: 代码格式化
- **Flake8**: 代码检查
- **MyPy**: 类型检查
- **Pre-commit**: 提交前检查

```bash
# 格式化代码
make format

# 检查代码质量
make lint

# 运行所有质量检查
make quality
```

### 编码标准

#### Python代码规范

1. **PEP 8**: 遵循Python官方代码风格指南
2. **类型注解**: 为函数参数和返回值添加类型注解
3. **文档字符串**: 使用Google风格的docstring
4. **命名规范**:
   - 类名使用PascalCase
   - 函数和变量使用snake_case
   - 常量使用UPPER_CASE
   - 私有成员以下划线开头

#### 示例代码

```python
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class MysteryEvent:
    """神秘事件数据模型。
    
    Attributes:
        event_id: 事件唯一标识符
        title: 事件标题
        description: 事件描述
        credibility_score: 可信度评分 (0.0-1.0)
    """
    event_id: str
    title: str
    description: str
    credibility_score: float
    metadata: Optional[Dict[str, Any]] = None


class EventAnalyzer:
    """事件分析器。"""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """初始化分析器。
        
        Args:
            config: 配置参数字典
        """
        self._config = config
        self._events: List[MysteryEvent] = []
    
    def analyze_credibility(self, event: MysteryEvent) -> float:
        """分析事件可信度。
        
        Args:
            event: 待分析的神秘事件
            
        Returns:
            可信度评分 (0.0-1.0)
            
        Raises:
            ValueError: 当事件数据无效时
        """
        if not event.description:
            raise ValueError("事件描述不能为空")
        
        # 实现可信度分析逻辑
        score = self._calculate_credibility_score(event)
        return min(max(score, 0.0), 1.0)
    
    def _calculate_credibility_score(self, event: MysteryEvent) -> float:
        """计算可信度评分的内部方法。"""
        # 具体实现
        pass
```

### 测试规范

#### 测试要求

1. **覆盖率**: 新代码测试覆盖率应达到80%以上
2. **测试类型**: 包括单元测试、集成测试和端到端测试
3. **测试命名**: 使用描述性的测试方法名
4. **测试隔离**: 每个测试应该独立运行

#### 测试示例

```python
import pytest
from unittest.mock import Mock, patch
from mystery_research.analysis import EventAnalyzer
from mystery_research.models import MysteryEvent


class TestEventAnalyzer:
    """事件分析器测试类。"""
    
    @pytest.fixture
    def analyzer(self):
        """创建分析器实例。"""
        config = {"credibility_threshold": 0.5}
        return EventAnalyzer(config)
    
    @pytest.fixture
    def sample_event(self):
        """创建示例事件。"""
        return MysteryEvent(
            event_id="test-001",
            title="UFO目击事件",
            description="在某地发现不明飞行物",
            credibility_score=0.0
        )
    
    def test_analyze_credibility_valid_event(self, analyzer, sample_event):
        """测试有效事件的可信度分析。"""
        score = analyzer.analyze_credibility(sample_event)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
    
    def test_analyze_credibility_empty_description(self, analyzer):
        """测试空描述事件的处理。"""
        event = MysteryEvent(
            event_id="test-002",
            title="测试事件",
            description="",
            credibility_score=0.0
        )
        
        with pytest.raises(ValueError, match="事件描述不能为空"):
            analyzer.analyze_credibility(event)
    
    @patch('mystery_research.analysis.external_api_call')
    def test_analyze_credibility_with_mock(self, mock_api, analyzer, sample_event):
        """测试使用Mock的可信度分析。"""
        mock_api.return_value = {"credibility": 0.8}
        
        score = analyzer.analyze_credibility(sample_event)
        
        assert score == 0.8
        mock_api.assert_called_once()
```

#### 运行测试

```bash
# 运行所有测试
make test

# 运行特定测试文件
pytest tests/test_analysis.py -v

# 运行特定测试方法
pytest tests/test_analysis.py::TestEventAnalyzer::test_analyze_credibility_valid_event -v

# 生成覆盖率报告
make coverage

# 快速测试（失败时停止）
make test-quick
```

### 提交规范

#### 提交消息格式

使用约定式提交(Conventional Commits)格式：

```
<类型>[可选的作用域]: <描述>

[可选的正文]

[可选的脚注]
```

#### 提交类型

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化
- `ci`: CI/CD相关更改

#### 提交示例

```bash
# 功能提交
git commit -m "feat(crawler): 添加学术论文爬虫支持"

# 修复提交
git commit -m "fix(analysis): 修复可信度计算中的除零错误"

# 文档提交
git commit -m "docs: 更新API文档和使用示例"

# 重构提交
git commit -m "refactor(database): 优化Neo4j查询性能"
```

## 🔄 Pull Request流程

### 创建Pull Request

1. **分支命名**: 使用描述性的分支名
   ```bash
   git checkout -b feature/academic-crawler
   git checkout -b fix/credibility-calculation
   git checkout -b docs/api-examples
   ```

2. **开发过程**:
   ```bash
   # 进行开发
   # 运行测试
   make test
   
   # 检查代码质量
   make quality
   
   # 提交更改
   git add .
   git commit -m "feat: 添加新功能"
   ```

3. **推送分支**:
   ```bash
   git push origin feature/academic-crawler
   ```

4. **创建PR**: 在GitHub上创建Pull Request

### PR模板

创建PR时，请包含以下信息：

```markdown
## 更改描述

简要描述此PR的更改内容。

## 更改类型

- [ ] 新功能
- [ ] Bug修复
- [ ] 文档更新
- [ ] 代码重构
- [ ] 性能优化
- [ ] 其他（请说明）

## 测试

- [ ] 添加了新的测试用例
- [ ] 所有现有测试通过
- [ ] 手动测试通过

## 检查清单

- [ ] 代码遵循项目编码规范
- [ ] 自我审查了代码更改
- [ ] 添加了必要的注释
- [ ] 更新了相关文档
- [ ] 没有引入新的警告
- [ ] 添加了适当的测试

## 相关Issue

关闭 #(issue编号)

## 截图（如适用）

如果更改涉及UI，请添加截图。

## 额外说明

任何审查者需要知道的额外信息。
```

### 代码审查

#### 审查要点

1. **功能正确性**: 代码是否实现了预期功能
2. **代码质量**: 是否遵循编码规范
3. **性能影响**: 是否有性能问题
4. **安全性**: 是否存在安全漏洞
5. **测试覆盖**: 是否有足够的测试
6. **文档完整性**: 是否更新了相关文档

#### 审查流程

1. **自动检查**: CI/CD流水线自动运行测试和代码检查
2. **人工审查**: 至少一名维护者审查代码
3. **反馈处理**: 根据审查意见修改代码
4. **最终批准**: 审查通过后合并到主分支

## 🏗️ 项目架构

### 目录结构

```
Lingjing/
├── agents/              # AI代理模块
│   ├── __init__.py
│   └── agents.py
├── config/              # 配置管理
│   ├── __init__.py
│   ├── configuration.py
│   ├── default.yaml
│   ├── mystery_config.py
│   ├── tools.py
│   └── validator.py
├── crawler/             # 数据爬虫
│   ├── __init__.py
│   ├── academic_crawler.py
│   ├── crawler.py
│   ├── mystery_crawler.py
│   └── ...
├── graph/               # 图数据处理
│   ├── __init__.py
│   ├── builder.py
│   ├── nodes.py
│   └── types.py
├── rag/                 # 检索增强生成
│   ├── __init__.py
│   ├── builder.py
│   ├── neo4j_retriever.py
│   └── ...
├── tools/               # 分析工具
│   ├── __init__.py
│   ├── analysis.py
│   ├── correlation.py
│   └── ...
├── tests/               # 测试文件
│   └── test_system.py
├── docs/                # 文档
├── data/                # 数据文件
└── logs/                # 日志文件
```

### 核心组件

1. **配置系统** (`config/`): 管理系统配置和参数
2. **爬虫系统** (`crawler/`): 多源数据采集
3. **AI代理** (`agents/`): 智能分析和决策
4. **图数据库** (`graph/`): 知识图谱构建
5. **RAG系统** (`rag/`): 检索增强生成
6. **分析工具** (`tools/`): 各种分析功能

### 扩展指南

#### 添加新的爬虫

```python
# crawler/custom_crawler.py
from .crawler import Crawler
from typing import List, Optional

class CustomCrawler(Crawler):
    """自定义爬虫实现。"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.custom_param = config.get('custom_param')
    
    async def crawl_url(self, url: str) -> Optional[Document]:
        """爬取单个URL。"""
        # 实现爬取逻辑
        pass
    
    async def search(self, query: str, max_results: int = 10) -> List[str]:
        """搜索相关URL。"""
        # 实现搜索逻辑
        pass
```

#### 添加新的分析工具

```python
# tools/custom_analysis.py
from .decorators import mystery_tool
from typing import Dict, Any, List

@mystery_tool
def custom_analysis_tool(data: Dict[str, Any]) -> Dict[str, Any]:
    """自定义分析工具。
    
    Args:
        data: 输入数据
        
    Returns:
        分析结果
    """
    # 实现分析逻辑
    result = {
        'analysis_type': 'custom',
        'results': [],
        'confidence': 0.0
    }
    return result
```

#### 添加新的AI模型

```python
# ai/custom_model.py
from .base import BaseAIProvider
from typing import str, Dict, Any

class CustomAIProvider(BaseAIProvider):
    """自定义AI模型提供者。"""
    
    def __init__(self, api_key: str, **kwargs):
        super().__init__()
        self.api_key = api_key
        self.model_config = kwargs
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成AI响应。"""
        # 实现模型调用逻辑
        pass
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """分析文本内容。"""
        # 实现文本分析逻辑
        pass
```

## 🚀 发布流程

### 版本管理

我们使用语义化版本控制(SemVer)：

- **主版本号**: 不兼容的API更改
- **次版本号**: 向后兼容的功能性新增
- **修订号**: 向后兼容的问题修正

### 发布步骤

1. **更新版本号**:
   ```bash
   # 更新 __version__.py
   vim __version__.py
   ```

2. **更新变更日志**:
   ```bash
   # 更新 CHANGELOG.md
   vim CHANGELOG.md
   ```

3. **创建发布分支**:
   ```bash
   git checkout -b release/v1.2.0
   git commit -m "chore: 准备v1.2.0发布"
   ```

4. **测试和验证**:
   ```bash
   make test
   make quality
   make build
   ```

5. **创建标签**:
   ```bash
   git tag -a v1.2.0 -m "发布v1.2.0"
   git push origin v1.2.0
   ```

## 📞 获取帮助

### 联系方式

- **GitHub Issues**: 报告问题和功能请求
- **GitHub Discussions**: 一般讨论和问答
- **邮件**: 联系维护团队
- **文档**: 查看项目文档

### 社区准则

我们致力于创建一个开放、友好的社区环境。请遵循以下准则：

1. **尊重他人**: 保持礼貌和专业
2. **建设性反馈**: 提供有用的建议和批评
3. **包容性**: 欢迎不同背景的贡献者
4. **耐心**: 帮助新手学习和成长
5. **协作**: 共同努力改进项目

### 行为准则

本项目采用[贡献者公约](https://www.contributor-covenant.org/)行为准则。参与项目即表示您同意遵守其条款。

## 🙏 致谢

感谢所有为项目做出贡献的人员：

- 代码贡献者
- 文档编写者
- 测试人员
- 问题报告者
- 功能建议者
- 社区维护者

您的贡献让这个项目变得更好！

---

**再次感谢您的贡献！** 🎉

如果您有任何问题或需要帮助，请随时联系我们。我们期待您的参与！