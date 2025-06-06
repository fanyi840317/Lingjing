# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

import os
import enum
from dotenv import load_dotenv

load_dotenv()


class SearchEngine(enum.Enum):
    """搜索引擎枚举"""
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"
    BRAVE_SEARCH = "brave_search"
    ARXIV = "arxiv"
    ACADEMIC_SEARCH = "academic_search"  # 学术搜索引擎
    MYSTERY_SEARCH = "mystery_search"  # 神秘事件专用搜索


class RAGProvider(enum.Enum):
    """RAG提供商枚举"""
    RAGFLOW = "ragflow"
    NEO4J = "neo4j"  # 图数据库
    ELASTICSEARCH = "elasticsearch"  # 全文搜索


class AnalysisEngine(enum.Enum):
    """分析引擎枚举"""
    CREDIBILITY_ANALYZER = "credibility_analyzer"  # 可信度分析
    CORRELATION_ANALYZER = "correlation_analyzer"  # 关联分析
    TIMELINE_ANALYZER = "timeline_analyzer"  # 时间线分析
    LOCATION_ANALYZER = "location_analyzer"  # 地理位置分析


class DataExtractor(enum.Enum):
    """数据提取器枚举"""
    ACADEMIC_EXTRACTOR = "academic_extractor"  # 学术论文提取器
    NEWS_EXTRACTOR = "news_extractor"  # 新闻提取器
    FORUM_EXTRACTOR = "forum_extractor"  # 论坛提取器
    DOCUMENTARY_EXTRACTOR = "documentary_extractor"  # 纪录片提取器
    GOVERNMENT_EXTRACTOR = "government_extractor"  # 政府报告提取器


# 工具配置
SELECTED_SEARCH_ENGINE = os.getenv("SEARCH_API", SearchEngine.TAVILY.value)
SELECTED_RAG_PROVIDER = os.getenv("RAG_PROVIDER", RAGProvider.RAGFLOW.value)
SELECTED_ANALYSIS_ENGINE = os.getenv("ANALYSIS_ENGINE", AnalysisEngine.CREDIBILITY_ANALYZER.value)

# 神秘事件专用配置
ENABLE_ACADEMIC_SEARCH = os.getenv("ENABLE_ACADEMIC_SEARCH", "true").lower() == "true"
ENABLE_CREDIBILITY_FILTER = os.getenv("ENABLE_CREDIBILITY_FILTER", "true").lower() == "true"
ENABLE_CORRELATION_ANALYSIS = os.getenv("ENABLE_CORRELATION_ANALYSIS", "true").lower() == "true"
ENABLE_GRAPH_STORAGE = os.getenv("ENABLE_GRAPH_STORAGE", "true").lower() == "true"

# API配置
CNKI_API_KEY = os.getenv("CNKI_API_KEY", "")
WANFANG_API_KEY = os.getenv("WANFANG_API_KEY", "")
WEB_OF_SCIENCE_API_KEY = os.getenv("WEB_OF_SCIENCE_API_KEY", "")
MUFON_API_KEY = os.getenv("MUFON_API_KEY", "")

# 数据库配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "mystery_events")

# 分析配置
CREDIBILITY_THRESHOLD = float(os.getenv("CREDIBILITY_THRESHOLD", "0.6"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
TIME_WINDOW_DAYS = int(os.getenv("TIME_WINDOW_DAYS", "30"))
LOCATION_RADIUS_KM = float(os.getenv("LOCATION_RADIUS_KM", "100.0"))

# 报告生成配置
REPORT_OUTPUT_DIR = os.getenv("REPORT_OUTPUT_DIR", "./reports")
REPORT_TEMPLATE_DIR = os.getenv("REPORT_TEMPLATE_DIR", "./templates")
ENABLE_PDF_EXPORT = os.getenv("ENABLE_PDF_EXPORT", "true").lower() == "true"
ENABLE_WORD_EXPORT = os.getenv("ENABLE_WORD_EXPORT", "true").lower() == "true"

# API接口配置
API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "100"))
API_KEY_REQUIRED = os.getenv("API_KEY_REQUIRED", "true").lower() == "true"
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "mystery_research_secret_key")