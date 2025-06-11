# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

import os
import yaml
from dataclasses import dataclass, field, fields
from typing import Any, Optional
from pathlib import Path

from langchain_core.runnables import RunnableConfig

from rag.retriever import Resource
from config.mystery_config import MysteryEventConfig


@dataclass(kw_only=True)
class Configuration:
    """神秘事件研究系统的可配置字段"""

    # 基础配置（继承自deer-flow）
    resources: list[Resource] = field(
        default_factory=list
    )  # 用于研究的资源
    max_plan_iterations: int = 1  # 最大计划迭代次数
    max_step_num: int = 5  # 计划中的最大步骤数（神秘事件研究需要更多步骤）
    max_search_results: int = 10  # 最大搜索结果数（神秘事件需要更多信息）
    mcp_settings: dict = None  # MCP设置，包括动态加载的工具
    
    # 神秘事件专用配置
    mystery_config: MysteryEventConfig = field(default_factory=MysteryEventConfig)
    enable_academic_search: bool = True  # 启用学术搜索
    enable_credibility_filter: bool = True  # 启用可信度过滤
    enable_correlation_analysis: bool = True  # 启用关联分析
    enable_graph_storage: bool = True  # 启用图数据库存储
    
    # 报告生成配置
    report_formats: list[str] = field(default_factory=lambda: ["markdown", "pdf", "json"])
    include_images: bool = True  # 报告中包含图片
    include_timeline: bool = True  # 包含时间线分析
    include_correlation_graph: bool = True  # 包含关联图
    
    # API接口配置
    api_rate_limit: int = 100  # API调用频率限制（每分钟）
    api_key_required: bool = True  # 是否需要API密钥
    enable_batch_processing: bool = True  # 启用批处理

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """从RunnableConfig创建Configuration实例"""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})
    
    def get_mystery_keywords(self, event_type: str = None) -> list[str]:
        """获取神秘事件关键词"""
        if event_type:
            from config.mystery_config import MysteryEventType
            try:
                event_enum = MysteryEventType(event_type)
                return self.mystery_config.get_keywords_by_type(event_enum)
            except ValueError:
                pass
        return self.mystery_config.get_all_keywords()
    
    def get_reliable_sources(self) -> list:
        """获取可靠数据源"""
        return self.mystery_config.get_reliable_sources()


def load_yaml_config(config_path: str) -> dict:
    """加载YAML配置文件"""
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            return {}
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Warning: Failed to load config from {config_path}: {e}")
        return {}