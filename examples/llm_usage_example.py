#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM Usage Examples for Lingjing Mystery Research System

This file demonstrates how to use different LLM providers and types
for various mystery research tasks.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llms.llm import (
    get_llm_by_type,
    create_llm_from_config,
    list_available_providers,
    detect_default_provider,
    clear_llm_cache
)
from llms.types import LLMType
from agents.agents import (
    create_mystery_agent,
    create_agent
)
from config.agents import (
    get_agent_llm_type,
    get_agent_config,
    list_available_agents
)


def demo_basic_llm_usage():
    """演示基本的LLM使用方法"""
    print("=== 基本LLM使用演示 ===")
    
    # 检查可用的LLM提供商
    print("\n可用的LLM提供商:")
    providers = list_available_providers()
    for provider, available in providers.items():
        status = "✓" if available else "✗"
        print(f"  {status} {provider}")
    
    # 检测默认提供商
    default_provider = detect_default_provider()
    print(f"\n默认提供商: {default_provider}")
    
    # 创建不同类型的LLM
    llm_types = [LLMType.BASIC, LLMType.REASONING, LLMType.ANALYSIS]
    
    for llm_type in llm_types:
        try:
            print(f"\n创建 {llm_type.value} LLM...")
            llm = get_llm_by_type(llm_type)
            print(f"  成功创建: {type(llm).__name__}")
            
            # 测试简单对话
            if hasattr(llm, 'generate'):
                response = llm.generate("你好，请简单介绍一下你自己。")
                print(f"  响应: {response[:100]}...")
            
        except Exception as e:
            print(f"  创建失败: {e}")


def demo_agent_creation():
    """演示智能体创建"""
    print("\n=== 智能体创建演示 ===")
    
    # 列出可用的智能体类型
    print("\n可用的智能体类型:")
    agents = list_available_agents()
    for agent in agents:
        llm_type = get_agent_llm_type(agent)
        print(f"  - {agent} (使用 {llm_type.value} LLM)")
    
    # 创建不同类型的智能体
    agent_types = ["mystery_researcher", "credibility_analyzer", "correlation_analyzer"]
    
    for agent_type in agent_types:
        try:
            print(f"\n创建 {agent_type} 智能体...")
            
            # 获取智能体配置
            config = get_agent_config(agent_type)
            print(f"  配置: {config.get('description', 'N/A')}")
            
            # 创建智能体
            agent = create_mystery_agent(
                agent_type=agent_type,
                mystery_config={"research_focus": "UFO目击事件"},
                state={"current_time": "2024-01-15"}
            )
            
            print(f"  成功创建智能体: {type(agent).__name__}")
            
        except Exception as e:
            print(f"  创建失败: {e}")


def demo_multi_provider_fallback():
    """演示多提供商回退机制"""
    print("\n=== 多提供商回退演示 ===")
    
    # 尝试使用不同的提供商
    providers = ["openai", "anthropic", "qwen", "zhipu", "baidu", "ollama"]
    
    for provider in providers:
        try:
            print(f"\n尝试使用 {provider} 提供商...")
            
            # 创建特定提供商的LLM
            llm = create_llm_from_config(
                llm_type=LLMType.BASIC,
                provider=provider
            )
            
            print(f"  成功创建: {type(llm).__name__}")
            
            # 测试生成
            if hasattr(llm, 'generate'):
                response = llm.generate("请用一句话描述神秘事件研究的重要性。")
                print(f"  响应: {response[:80]}...")
            
        except Exception as e:
            print(f"  失败: {e}")


def demo_mystery_research_workflow():
    """演示神秘事件研究工作流"""
    print("\n=== 神秘事件研究工作流演示 ===")
    
    # 模拟神秘事件数据
    mystery_event = {
        "title": "不明飞行物目击事件",
        "location": "北京市朝阳区",
        "date": "2024-01-10",
        "witnesses": 3,
        "description": "多名目击者报告在夜空中看到不明发光物体，呈三角形排列，无声移动。",
        "evidence": ["目击者证词", "手机拍摄视频", "雷达数据异常"]
    }
    
    # 研究工作流
    workflow_steps = [
        ("mystery_researcher", "初步事件调研"),
        ("credibility_analyzer", "可信度分析"),
        ("academic_researcher", "学术文献检索"),
        ("correlation_analyzer", "关联性分析"),
        ("mystery_planner", "深入研究规划"),
        ("mystery_reporter", "研究报告生成")
    ]
    
    results = {}
    
    for agent_type, task_description in workflow_steps:
        try:
            print(f"\n执行任务: {task_description}")
            print(f"使用智能体: {agent_type}")
            
            # 创建智能体
            agent = create_mystery_agent(
                agent_type=agent_type,
                mystery_config={
                    "research_focus": mystery_event["title"],
                    "location": mystery_event["location"],
                    "evidence_types": mystery_event["evidence"]
                },
                state={
                    "current_time": "2024-01-15",
                    "mystery_events": [mystery_event],
                    "previous_results": results
                }
            )
            
            # 模拟任务执行
            task_prompt = f"""
            请分析以下神秘事件：
            
            事件标题：{mystery_event['title']}
            发生地点：{mystery_event['location']}
            发生时间：{mystery_event['date']}
            目击者数量：{mystery_event['witnesses']}
            事件描述：{mystery_event['description']}
            现有证据：{', '.join(mystery_event['evidence'])}
            
            请根据你的专业领域进行分析。
            """
            
            # 这里应该调用智能体的实际方法
            # result = agent.process(task_prompt)
            
            # 模拟结果
            mock_result = f"{agent_type} 完成了 {task_description} 任务"
            results[agent_type] = mock_result
            
            print(f"  任务完成: {mock_result}")
            
        except Exception as e:
            print(f"  任务失败: {e}")
            results[agent_type] = f"任务失败: {e}"
    
    # 输出最终结果
    print("\n=== 工作流执行结果 ===")
    for step, result in results.items():
        print(f"{step}: {result}")


def demo_llm_configuration():
    """演示LLM配置管理"""
    print("\n=== LLM配置管理演示 ===")
    
    # 显示当前配置
    from llms.llm import load_llm_config
    
    try:
        config = load_llm_config()
        print("\n当前LLM配置:")
        
        # 显示默认提供商
        default_providers = config.get("default_providers", [])
        print(f"默认提供商优先级: {' > '.join(default_providers)}")
        
        # 显示各提供商的模型配置
        for provider in ["openai", "anthropic", "qwen", "zhipu", "baidu"]:
            if provider in config:
                provider_config = config[provider]
                models = provider_config.get("models", {})
                print(f"\n{provider.upper()} 模型配置:")
                for llm_type, model in models.items():
                    if model:  # 跳过空模型
                        print(f"  {llm_type}: {model}")
        
        # 显示回退配置
        fallback = config.get("fallback", {})
        if fallback:
            print(f"\n回退机制: {'启用' if fallback.get('enabled') else '禁用'}")
            print(f"最大重试次数: {fallback.get('max_retries', 'N/A')}")
        
        # 显示速率限制
        rate_limiting = config.get("rate_limiting", {})
        if rate_limiting:
            print(f"\n速率限制: {'启用' if rate_limiting.get('enabled') else '禁用'}")
            print(f"每分钟请求数: {rate_limiting.get('requests_per_minute', 'N/A')}")
        
    except Exception as e:
        print(f"配置加载失败: {e}")


def main():
    """主函数"""
    print("Lingjing 神秘事件研究系统 - LLM使用示例")
    print("=" * 50)
    
    # 设置环境变量示例（实际使用时应该在.env文件中配置）
    print("\n注意：请确保已正确配置相关API密钥")
    print("可以通过以下方式配置：")
    print("1. 设置环境变量")
    print("2. 修改 config/llm_config.yaml 文件")
    print("3. 创建 .env 文件")
    
    # 运行演示
    try:
        demo_llm_configuration()
        demo_basic_llm_usage()
        demo_agent_creation()
        demo_multi_provider_fallback()
        demo_mystery_research_workflow()
        
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中发生错误: {e}")
    finally:
        # 清理缓存
        clear_llm_cache()
        print("\n演示结束，已清理LLM缓存")


if __name__ == "__main__":
    main()