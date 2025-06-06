# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

from llms.types import LLMType
from typing import Dict

# 延迟导入以避免循环依赖
def _get_llm_by_type(llm_type: LLMType):
    from llms.llm import get_llm_by_type
    return get_llm_by_type(llm_type)

# Agent to LLM type mapping
AGENT_LLM_MAP: Dict[str, LLMType] = {
    # Research agents - use reasoning models for complex analysis
    "researcher": LLMType.REASONING,
    "mystery_researcher": LLMType.REASONING,
    "academic_researcher": LLMType.RESEARCH,
    
    # Analysis agents - use analysis-optimized models
    "analyzer": LLMType.ANALYSIS,
    "credibility_analyzer": LLMType.ANALYSIS,
    "correlation_analyzer": LLMType.ANALYSIS,
    
    # Planning agents - use reasoning models for strategic thinking
    "planner": LLMType.REASONING,
    "mystery_planner": LLMType.REASONING,
    
    # Reporting agents - use basic models for text generation
    "reporter": LLMType.BASIC,
    "mystery_reporter": LLMType.BASIC,
    
    # Utility agents
    "crawler": LLMType.FAST,
    "validator": LLMType.BASIC,
    "coordinator": LLMType.BASIC,
    
    # Vision-related agents
    "image_analyzer": LLMType.VISION,
    "video_analyzer": LLMType.VISION,
    
    # Code-related agents
    "code_generator": LLMType.CODE,
    "code_reviewer": LLMType.CODE,
}

# Agent configuration templates
AGENT_CONFIGS = {
    "mystery_researcher": {
        "description": "专业的神秘事件研究专家，负责收集和分析神秘现象",
        "capabilities": [
            "多源信息收集",
            "事件可信度评估",
            "科学方法应用",
            "跨领域知识整合"
        ],
        "tools": [
            "crawl_mystery_events",
            "search_academic_papers",
            "analyze_credibility",
            "extract_timeline"
        ],
        "prompt_template": "mystery_researcher",
        "max_iterations": 10,
        "temperature": 0.3
    },
    
    "academic_researcher": {
        "description": "学术研究专家，专注于科学文献和理论分析",
        "capabilities": [
            "学术文献检索",
            "科学方法论",
            "统计分析",
            "理论建构"
        ],
        "tools": [
            "search_academic_papers",
            "analyze_statistics",
            "build_knowledge_graph",
            "validate_theories"
        ],
        "prompt_template": "academic_researcher",
        "max_iterations": 8,
        "temperature": 0.2
    },
    
    "credibility_analyzer": {
        "description": "可信度分析专家，评估信息和事件的可靠性",
        "capabilities": [
            "信息源评估",
            "证据质量分析",
            "偏见识别",
            "统计验证"
        ],
        "tools": [
            "analyze_credibility",
            "validate_sources",
            "detect_bias",
            "calculate_confidence"
        ],
        "prompt_template": "credibility_analyzer",
        "max_iterations": 6,
        "temperature": 0.1
    },
    
    "correlation_analyzer": {
        "description": "关联分析专家，识别事件间的关系和模式",
        "capabilities": [
            "模式识别",
            "关联分析",
            "统计建模",
            "预测分析"
        ],
        "tools": [
            "analyze_correlations",
            "detect_patterns",
            "build_timeline",
            "predict_trends"
        ],
        "prompt_template": "correlation_analyzer",
        "max_iterations": 8,
        "temperature": 0.2
    },
    
    "mystery_planner": {
        "description": "神秘事件研究规划师，制定研究策略和计划",
        "capabilities": [
            "研究设计",
            "资源配置",
            "风险评估",
            "项目管理"
        ],
        "tools": [
            "create_research_plan",
            "allocate_resources",
            "assess_risks",
            "monitor_progress"
        ],
        "prompt_template": "mystery_planner",
        "max_iterations": 5,
        "temperature": 0.3
    },
    
    "mystery_reporter": {
        "description": "神秘事件研究报告员，生成专业研究报告",
        "capabilities": [
            "科学写作",
            "数据可视化",
            "结果整合",
            "质量控制"
        ],
        "tools": [
            "generate_report",
            "create_visualizations",
            "format_citations",
            "validate_content"
        ],
        "prompt_template": "mystery_reporter",
        "max_iterations": 5,
        "temperature": 0.4
    }
}

# Default agent settings
DEFAULT_AGENT_SETTINGS = {
    "max_iterations": 10,
    "temperature": 0.3,
    "max_tokens": 4000,
    "timeout": 300,  # 5 minutes
    "retry_attempts": 3,
    "retry_delay": 1.0,
}

# Agent role descriptions for system prompts
AGENT_ROLES = {
    "mystery_researcher": "你是一位专业的神秘事件研究专家",
    "academic_researcher": "你是一位专业的学术研究专家", 
    "credibility_analyzer": "你是一位专业的可信度分析专家",
    "correlation_analyzer": "你是一位专业的关联分析专家",
    "mystery_planner": "你是一位专业的神秘事件研究规划师",
    "mystery_reporter": "你是一位专业的神秘事件研究报告员",
}


def get_agent_llm_type(agent_type: str) -> LLMType:
    """Get the LLM type for a given agent type."""
    return AGENT_LLM_MAP.get(agent_type, LLMType.BASIC)


def get_agent_config(agent_name: str) -> dict:
    """Get configuration for a specific agent."""
    config = AGENT_CONFIGS.get(agent_name, {})
    # Merge with default settings
    merged_config = DEFAULT_AGENT_SETTINGS.copy()
    merged_config.update(config)
    return merged_config


def list_available_agents() -> list:
    """List all available agent types."""
    return list(AGENT_CONFIGS.keys())


def get_agent_role(agent_name: str) -> str:
    """Get the role description for an agent."""
    return AGENT_ROLES.get(agent_name, "你是一位专业的AI助手")


def create_agent_from_config(agent_name: str) -> dict:
    """Create an agent from configuration."""
    # 获取代理的LLM类型
    llm_type = get_agent_llm_type(agent_name)
    
    # 获取LLM实例
    llm = _get_llm_by_type(llm_type)
    
    # 获取代理配置
    config = get_agent_config(agent_name)
    
    return {
        'llm': llm,
        'config': config,
        'agent_name': agent_name,
        'llm_type': llm_type
    }