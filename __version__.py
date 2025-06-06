#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神秘事件研究系统 - 版本信息
Mystery Event Research System - Version Information
"""

# 版本信息
__version__ = "0.1.0"
__version_info__ = (0, 1, 0)

# 项目信息
__title__ = "Mystery Event Research System"
__description__ = "基于AI的综合性神秘现象研究平台"
__author__ = "Mystery Research Team"
__author_email__ = "research@mystery-system.com"
__license__ = "MIT"
__copyright__ = "Copyright 2024 Mystery Research Team"

# 构建信息
__build__ = "stable"
__status__ = "Beta"

# API版本
__api_version__ = "1.0"

# 支持的Python版本
__python_requires__ = ">=3.8"

# 项目URL
__url__ = "https://github.com/your-username/mystery-research-system"
__download_url__ = "https://github.com/your-username/mystery-research-system/archive/v0.1.0.tar.gz"
__documentation_url__ = "https://mystery-research-system.readthedocs.io/"
__repository_url__ = "https://github.com/your-username/mystery-research-system"
__issues_url__ = "https://github.com/your-username/mystery-research-system/issues"

# 发布信息
__release_date__ = "2024-01-01"
__release_notes__ = """
神秘事件研究系统 v0.1.0 发布说明

🎉 首次发布！

主要功能：
✅ 多源数据采集系统
✅ 智能分析引擎
✅ AI驱动的研究工作流
✅ 图数据库存储
✅ 可信度评估
✅ 事件关联分析
✅ 自动化报告生成

支持的神秘事件类型：
🛸 UFO目击事件
🦶 神秘生物目击
👻 超自然现象
🏛️ 古代未解之谜
🌊 神秘失踪案例
⚡ 自然异常现象

技术特性：
🤖 基于LangGraph的多代理系统
🕷️ 专业化网络爬虫
📊 Neo4j图数据库集成
🔍 Elasticsearch全文搜索
📈 高级数据分析和可视化
🌐 多语言支持（中文、英文、日文、韩文）

安装和使用：
1. pip install mystery-research-system
2. 配置环境变量
3. mystery-research --interactive

更多信息请参考项目文档。
"""

# 兼容性信息
__compatibility__ = {
    "python": ["3.8", "3.9", "3.10", "3.11", "3.12"],
    "platforms": ["Windows", "macOS", "Linux"],
    "databases": ["Neo4j", "Elasticsearch", "PostgreSQL", "MongoDB"],
    "ai_models": ["OpenAI GPT", "Anthropic Claude", "Google Gemini"],
}

# 功能标志
__features__ = {
    "web_crawling": True,
    "academic_search": True,
    "credibility_analysis": True,
    "correlation_analysis": True,
    "graph_storage": True,
    "timeline_analysis": True,
    "location_analysis": True,
    "multi_language": True,
    "batch_processing": True,
    "interactive_mode": True,
    "report_generation": True,
    "data_visualization": True,
}

# 系统要求
__system_requirements__ = {
    "min_python_version": "3.8.0",
    "recommended_python_version": "3.11.0",
    "min_memory_mb": 2048,
    "recommended_memory_mb": 8192,
    "min_disk_space_mb": 1024,
    "recommended_disk_space_mb": 10240,
    "network_required": True,
    "gpu_required": False,
    "gpu_recommended": True,
}

# 依赖版本
__dependencies__ = {
    "langchain": ">=0.1.0",
    "langgraph": ">=0.0.40",
    "openai": ">=1.0.0",
    "neo4j": ">=5.15.0",
    "elasticsearch": ">=8.11.0",
    "requests": ">=2.31.0",
    "beautifulsoup4": ">=4.12.0",
    "pandas": ">=2.0.0",
    "numpy": ">=1.24.0",
}

# 更新日志
__changelog__ = {
    "0.1.0": {
        "date": "2024-01-01",
        "changes": [
            "首次发布",
            "实现多源数据采集系统",
            "添加智能分析引擎",
            "集成AI驱动的研究工作流",
            "支持Neo4j图数据库",
            "实现可信度评估功能",
            "添加事件关联分析",
            "支持自动化报告生成",
            "多语言界面支持",
            "完整的文档和示例",
        ],
        "breaking_changes": [],
        "bug_fixes": [],
        "known_issues": [
            "某些网站的爬虫可能需要额外配置",
            "大规模数据处理时内存使用较高",
            "部分AI模型响应时间较长",
        ],
    },
}

# 路线图
__roadmap__ = {
    "0.2.0": {
        "planned_date": "2024-03-01",
        "features": [
            "增强的图像和视频分析",
            "实时数据流处理",
            "改进的用户界面",
            "更多数据源集成",
            "高级可视化功能",
        ],
    },
    "0.3.0": {
        "planned_date": "2024-06-01",
        "features": [
            "机器学习模型训练",
            "预测分析功能",
            "协作研究平台",
            "API接口开放",
            "移动应用支持",
        ],
    },
    "1.0.0": {
        "planned_date": "2024-12-01",
        "features": [
            "完整的生产环境支持",
            "企业级安全功能",
            "高可用性部署",
            "完整的监控和日志",
            "专业技术支持",
        ],
    },
}

# 获取版本信息的便捷函数
def get_version():
    """获取版本号"""
    return __version__

def get_version_info():
    """获取详细版本信息"""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "title": __title__,
        "description": __description__,
        "author": __author__,
        "license": __license__,
        "build": __build__,
        "status": __status__,
        "release_date": __release_date__,
        "python_requires": __python_requires__,
        "url": __url__,
    }

def print_version_info():
    """打印版本信息"""
    info = get_version_info()
    print(f"""
🔍 {info['title']} v{info['version']}

📝 描述: {info['description']}
👥 作者: {info['author']}
📄 许可: {info['license']}
🏗️  构建: {info['build']}
📊 状态: {info['status']}
📅 发布: {info['release_date']}
🐍 Python: {info['python_requires']}
🌐 网址: {info['url']}

⚠️  本系统仅用于学术研究和教育目的。
请保持科学和理性的态度对待研究结果。
""")

if __name__ == "__main__":
    print_version_info()