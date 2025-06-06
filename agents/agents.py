# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

from langgraph.prebuilt import create_react_agent
from typing import List, Any

from prompts import apply_prompt_template
from llms.llm import get_llm_by_type
from config.agents import AGENT_LLM_MAP


def create_agent(agent_name: str, agent_type: str, tools: list, prompt_template: str):
    """Factory function to create agents with consistent configuration."""
    return create_react_agent(
        name=agent_name,
        model=get_llm_by_type(AGENT_LLM_MAP[agent_type]),
        tools=tools,
        prompt=lambda state: apply_prompt_template(prompt_template, state),
    )


def create_mystery_agent(
    agent_name: str, 
    agent_type: str, 
    tools: list, 
    prompt_template: str,
    mystery_config: dict = None
):
    """Factory function to create mystery research agents with specialized configuration."""
    llm = get_llm_by_type(AGENT_LLM_MAP[agent_type])
    
    # Enhance prompt with mystery research context
    def enhanced_prompt(state):
        base_prompt = apply_prompt_template(prompt_template, state)
        
        # Add mystery research context
        mystery_context = ""
        if mystery_config:
            mystery_context += f"\n\n## 神秘事件研究配置\n"
            if mystery_config.get("event_types"):
                mystery_context += f"关注事件类型: {', '.join(mystery_config['event_types'])}\n"
            if mystery_config.get("credibility_threshold"):
                mystery_context += f"可信度阈值: {mystery_config['credibility_threshold']}\n"
            if mystery_config.get("correlation_enabled"):
                mystery_context += f"关联分析: {'启用' if mystery_config['correlation_enabled'] else '禁用'}\n"
        
        # Add mystery events context if available
        mystery_events = state.get("mystery_events", [])
        if mystery_events:
            mystery_context += f"\n## 已收集神秘事件\n"
            for i, event in enumerate(mystery_events[:3]):  # Show first 3 events
                mystery_context += f"{i+1}. {event.title} (可信度: {event.credibility_score:.2f})\n"
            if len(mystery_events) > 3:
                mystery_context += f"... 还有 {len(mystery_events) - 3} 个事件\n"
        
        # Add academic sources context if available
        academic_sources = state.get("academic_sources", [])
        if academic_sources:
            mystery_context += f"\n## 学术资源\n已收集 {len(academic_sources)} 个学术资源\n"
        
        # Add credibility analysis context if available
        credibility_scores = state.get("credibility_scores", {})
        if credibility_scores:
            avg_credibility = sum(credibility_scores.values()) / len(credibility_scores)
            mystery_context += f"\n## 可信度分析\n平均可信度: {avg_credibility:.2f}\n"
        
        # Add correlation analysis context if available
        correlation_results = state.get("correlation_results", {})
        if correlation_results:
            mystery_context += f"\n## 关联分析\n发现 {len(correlation_results)} 个关联关系\n"
        
        if mystery_context:
            if isinstance(base_prompt, list):
                # Add context to the last user message or create a new one
                enhanced_messages = base_prompt.copy()
                enhanced_messages.append({
                    "role": "user",
                    "content": mystery_context
                })
                return enhanced_messages
            else:
                return base_prompt + mystery_context
        
        return base_prompt
    
    return create_react_agent(
        name=agent_name,
        model=llm,
        tools=tools,
        prompt=enhanced_prompt,
    )


def create_mystery_researcher_agent(tools: list, mystery_config: dict = None):
    """Create a specialized mystery researcher agent."""
    return create_mystery_agent(
        agent_name="mystery_researcher",
        agent_type="researcher",
        tools=tools,
        prompt_template="mystery_researcher",
        mystery_config=mystery_config
    )


def create_academic_researcher_agent(tools: list, mystery_config: dict = None):
    """Create a specialized academic researcher agent."""
    return create_mystery_agent(
        agent_name="academic_researcher",
        agent_type="researcher",
        tools=tools,
        prompt_template="academic_researcher",
        mystery_config=mystery_config
    )


def create_credibility_analyzer_agent(tools: list, mystery_config: dict = None):
    """Create a specialized credibility analyzer agent."""
    return create_mystery_agent(
        agent_name="credibility_analyzer",
        agent_type="analyzer",
        tools=tools,
        prompt_template="credibility_analyzer",
        mystery_config=mystery_config
    )


def create_correlation_analyzer_agent(tools: list, mystery_config: dict = None):
    """Create a specialized correlation analyzer agent."""
    return create_mystery_agent(
        agent_name="correlation_analyzer",
        agent_type="analyzer",
        tools=tools,
        prompt_template="correlation_analyzer",
        mystery_config=mystery_config
    )


def create_mystery_planner_agent(tools: list, mystery_config: dict = None):
    """Create a specialized mystery research planner agent."""
    return create_mystery_agent(
        agent_name="mystery_planner",
        agent_type="planner",
        tools=tools,
        prompt_template="mystery_planner",
        mystery_config=mystery_config
    )


def create_mystery_reporter_agent(tools: list, mystery_config: dict = None):
    """Create a specialized mystery research reporter agent."""
    return create_mystery_agent(
        agent_name="mystery_reporter",
        agent_type="reporter",
        tools=tools,
        prompt_template="mystery_reporter",
        mystery_config=mystery_config
    )