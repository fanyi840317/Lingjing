# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class StepType(str, Enum):
    """研究步骤类型枚举"""
    INFORMATION_COLLECTION = "information_collection"  # 信息收集
    DATA_ANALYSIS = "data_analysis"  # 数据分析
    CREDIBILITY_ASSESSMENT = "credibility_assessment"  # 可信度评估
    CORRELATION_ANALYSIS = "correlation_analysis"  # 关联分析
    ACADEMIC_RESEARCH = "academic_research"  # 学术研究
    MYSTERY_INVESTIGATION = "mystery_investigation"  # 神秘事件调查
    BACKGROUND_INVESTIGATION = "background_investigation"  # 背景调查
    REPORT_GENERATION = "report_generation"  # 报告生成
    HUMAN_FEEDBACK = "human_feedback"  # 人工反馈
    GRAPH_STORAGE = "graph_storage"  # 图谱存储


class ResearchStep(BaseModel):
    """研究步骤模型"""
    step_type: StepType = Field(..., description="步骤类型")
    description: str = Field(..., description="步骤描述")
    priority: int = Field(default=1, description="优先级 (1-5, 5最高)")
    estimated_duration: Optional[str] = Field(None, description="预估耗时")
    dependencies: List[str] = Field(default_factory=list, description="依赖的前置步骤")
    resources_needed: List[str] = Field(default_factory=list, description="所需资源")
    success_criteria: Optional[str] = Field(None, description="成功标准")
    completed: bool = Field(default=False, description="是否已完成")


class Plan(BaseModel):
    """研究计划模型"""
    title: str = Field(..., description="计划标题")
    objective: str = Field(..., description="研究目标")
    steps: List[ResearchStep] = Field(..., description="研究步骤列表")
    estimated_total_duration: Optional[str] = Field(None, description="预估总耗时")
    risk_assessment: Optional[str] = Field(None, description="风险评估")
    success_metrics: List[str] = Field(default_factory=list, description="成功指标")
    has_enough_context: bool = Field(default=False, description="是否有足够的上下文信息")
    confidence_level: float = Field(default=0.5, description="计划可信度 (0-1)")
    notes: Optional[str] = Field(None, description="备注信息")
    
    def get_next_step(self) -> Optional[ResearchStep]:
        """获取下一个未完成的步骤"""
        for step in self.steps:
            if not step.completed:
                return step
        return None
    
    def mark_step_completed(self, step_type: StepType) -> bool:
        """标记指定类型的步骤为已完成"""
        for step in self.steps:
            if step.step_type == step_type:
                step.completed = True
                return True
        return False
    
    def get_completion_rate(self) -> float:
        """获取计划完成率"""
        if not self.steps:
            return 0.0
        completed_count = sum(1 for step in self.steps if step.completed)
        return completed_count / len(self.steps)
    
    def is_completed(self) -> bool:
        """检查计划是否已完成"""
        return all(step.completed for step in self.steps)