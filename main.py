#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

"""
神秘事件研究系统 (Mystery Event Research System)

这是一个综合性的神秘事件研究平台，集成了多种数据源、分析工具和AI代理，
用于系统性地研究和分析各种神秘现象，包括UFO目击、超自然事件、古代谜团等。

主要功能:
- 多源数据采集 (网络爬虫、学术数据库、新闻媒体、论坛社区)
- 智能内容分析 (可信度评估、关联分析、时间线分析)
- 图数据库存储 (Neo4j集成，支持复杂关系查询)
- AI驱动的研究工作流 (基于LangGraph的多代理协作)
- 综合报告生成 (支持多种格式输出)
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from workflow import run_mystery_research_workflow, run_mystery_research_workflow_async
from config import Configuration
from tools import *
from crawler import build_specialized_crawlers
from rag import MysteryEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("mystery_research.log", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)


def setup_example_queries():
    """设置示例查询，用于演示系统功能。"""
    return {
        "ufo": "请研究最近5年内的UFO目击事件，特别关注有多个证人的案例，并分析其可信度和地理分布模式。",
        "cryptid": "调查关于大脚怪(Bigfoot)的最新报告和科学研究，包括DNA证据分析和目击者证词。",
        "paranormal": "分析世界各地著名闹鬼地点的超自然现象报告，评估证据质量并寻找共同模式。",
        "ancient": "研究古代文明中的未解之谜，如金字塔建造技术、史前巨石阵等，结合考古学和工程学观点。",
        "disappearance": "调查百慕大三角和其他神秘失踪案例，分析可能的科学解释和阴谋理论。",
        "anomaly": "研究自然界中的异常现象，如球状闪电、极光异常、地磁扰动等。"
    }


def print_system_info():
    """打印系统信息和功能介绍。"""
    print("\n" + "="*80)
    print("🔍 神秘事件研究系统 (Mystery Event Research System)")
    print("="*80)
    print("\n📋 系统功能:")
    print("  • 多源数据采集: 网络爬虫、学术数据库、新闻媒体、论坛社区")
    print("  • 智能内容分析: 可信度评估、关联分析、时间线分析、地理分析")
    print("  • 图数据库存储: Neo4j集成，支持复杂关系查询和可视化")
    print("  • AI驱动工作流: 基于LangGraph的多代理协作研究")
    print("  • 综合报告生成: 支持Markdown、PDF等多种格式")
    
    print("\n🎯 支持的神秘事件类型:")
    print("  • UFO目击事件 (UFO Sightings)")
    print("  • 神秘生物目击 (Cryptid Encounters)")
    print("  • 超自然现象 (Paranormal Events)")
    print("  • 古代未解之谜 (Ancient Mysteries)")
    print("  • 神秘失踪案例 (Mysterious Disappearances)")
    print("  • 自然异常现象 (Natural Anomalies)")
    
    print("\n🛠️ 可用工具:")
    print("  • 网络搜索和爬虫工具")
    print("  • 学术数据库检索")
    print("  • 可信度分析器")
    print("  • 事件关联分析器")
    print("  • 时间线分析器")
    print("  • 地理位置分析器")
    print("  • 图数据库存储")
    print("  • Python代码执行环境")
    print("  • 文档检索系统")
    print("="*80)


def print_example_queries():
    """打印示例查询。"""
    examples = setup_example_queries()
    print("\n📝 示例查询:")
    for key, query in examples.items():
        print(f"\n  {key.upper()}:")
        print(f"    {query}")
    print()


async def run_interactive_mode():
    """运行交互模式。"""
    print("\n🎮 进入交互模式 (输入 'quit' 或 'exit' 退出)")
    print("💡 提示: 您可以询问任何关于神秘事件的问题，系统将自动进行研究和分析。\n")
    
    while True:
        try:
            user_input = input("🔍 请输入您的研究问题: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 感谢使用神秘事件研究系统！")
                break
            
            if not user_input:
                print("❌ 请输入有效的研究问题。")
                continue
            
            print(f"\n🚀 开始研究: {user_input}")
            print("⏳ 正在处理，请稍候...\n")
            
            # 运行研究工作流
            result = await run_mystery_research_workflow_async(
                user_input=user_input,
                debug=True,
                max_plan_iterations=3,
                max_step_num=8,
                enable_background_investigation=True,
                enable_academic_search=True,
                enable_credibility_filter=True,
                enable_correlation_analysis=True,
                enable_graph_storage=True,
            )
            
            # 显示结果
            print("\n" + "="*60)
            print("📊 研究结果")
            print("="*60)
            
            if result.get("final_report"):
                print(result["final_report"])
            else:
                print("❌ 未能生成完整报告")
            
            # 显示统计信息
            mystery_events = result.get("mystery_events", [])
            academic_sources = result.get("academic_sources", [])
            credibility_scores = result.get("credibility_scores", {})
            
            print(f"\n📈 统计信息:")
            print(f"  • 发现神秘事件: {len(mystery_events)} 个")
            print(f"  • 学术资源: {len(academic_sources)} 个")
            print(f"  • 可信度评估: {len(credibility_scores)} 项")
            
            if credibility_scores:
                avg_credibility = sum(credibility_scores.values()) / len(credibility_scores)
                print(f"  • 平均可信度: {avg_credibility:.2f}")
            
            print("\n" + "="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出系统。")
            break
        except Exception as e:
            logger.error(f"交互模式错误: {e}")
            print(f"❌ 处理过程中出现错误: {e}")
            print("请重试或输入新的问题。\n")


async def run_batch_mode(queries: list, output_dir: Optional[str] = None):
    """运行批处理模式。"""
    print(f"\n🔄 批处理模式: 处理 {len(queries)} 个查询")
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 输出目录: {output_path.absolute()}")
    
    results = []
    
    for i, query in enumerate(queries, 1):
        print(f"\n🔍 [{i}/{len(queries)}] 处理查询: {query[:50]}...")
        
        try:
            result = await run_mystery_research_workflow_async(
                user_input=query,
                debug=False,
                max_plan_iterations=2,
                max_step_num=6,
            )
            
            results.append({
                "query": query,
                "result": result,
                "status": "success"
            })
            
            # 保存单个结果
            if output_dir:
                filename = f"result_{i:03d}.md"
                filepath = output_path / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# 查询: {query}\n\n")
                    f.write(result.get("final_report", "无报告生成"))
                print(f"💾 结果已保存: {filepath}")
            
        except Exception as e:
            logger.error(f"批处理查询失败 [{i}]: {e}")
            results.append({
                "query": query,
                "error": str(e),
                "status": "error"
            })
    
    # 生成汇总报告
    successful = sum(1 for r in results if r["status"] == "success")
    print(f"\n📊 批处理完成: {successful}/{len(queries)} 成功")
    
    return results


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(
        description="神秘事件研究系统 - 综合性神秘现象研究平台",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py --interactive                    # 交互模式
  python main.py --query "UFO目击事件研究"        # 单次查询
  python main.py --example ufo                   # 运行示例查询
  python main.py --batch queries.txt             # 批处理模式
  python main.py --info                          # 显示系统信息
        """
    )
    
    parser.add_argument(
        "--interactive", "-i", 
        action="store_true", 
        help="启动交互模式"
    )
    
    parser.add_argument(
        "--query", "-q", 
        type=str, 
        help="执行单次查询"
    )
    
    parser.add_argument(
        "--example", "-e", 
        choices=["ufo", "cryptid", "paranormal", "ancient", "disappearance", "anomaly"],
        help="运行预设示例查询"
    )
    
    parser.add_argument(
        "--batch", "-b", 
        type=str, 
        help="批处理模式，从文件读取查询列表"
    )
    
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        help="输出目录 (用于批处理模式)"
    )
    
    parser.add_argument(
        "--info", 
        action="store_true", 
        help="显示系统信息和功能介绍"
    )
    
    parser.add_argument(
        "--debug", "-d", 
        action="store_true", 
        help="启用调试模式"
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 显示系统信息
    if args.info:
        print_system_info()
        print_example_queries()
        return
    
    # 如果没有指定任何操作，显示帮助信息
    if not any([args.interactive, args.query, args.example, args.batch]):
        print_system_info()
        parser.print_help()
        return
    
    try:
        # 交互模式
        if args.interactive:
            asyncio.run(run_interactive_mode())
        
        # 单次查询
        elif args.query:
            print(f"\n🔍 执行查询: {args.query}")
            result = run_mystery_research_workflow(
                user_input=args.query,
                debug=args.debug
            )
            print("\n" + "="*60)
            print("📊 研究结果")
            print("="*60)
            print(result.get("final_report", "无报告生成"))
        
        # 示例查询
        elif args.example:
            examples = setup_example_queries()
            query = examples[args.example]
            print(f"\n🎯 运行示例查询 ({args.example.upper()}): {query}")
            result = run_mystery_research_workflow(
                user_input=query,
                debug=args.debug
            )
            print("\n" + "="*60)
            print("📊 研究结果")
            print("="*60)
            print(result.get("final_report", "无报告生成"))
        
        # 批处理模式
        elif args.batch:
            batch_file = Path(args.batch)
            if not batch_file.exists():
                print(f"❌ 批处理文件不存在: {batch_file}")
                return
            
            with open(batch_file, 'r', encoding='utf-8') as f:
                queries = [line.strip() for line in f if line.strip()]
            
            if not queries:
                print(f"❌ 批处理文件为空: {batch_file}")
                return
            
            asyncio.run(run_batch_mode(queries, args.output))
    
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出。")
    except Exception as e:
        logger.error(f"程序执行错误: {e}")
        print(f"❌ 程序执行出现错误: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()