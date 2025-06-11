#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神秘事件研究系统 - 演示脚本
Mystery Event Research System - Demo Script
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from workflow import run_mystery_research_workflow
    from models.mystery_event import MysteryEvent, MysteryEventType
    from models.document import Document
    from config.validator import validate_config
except ImportError as e:
    print(f"⚠️  导入错误: {e}")
    print("请确保所有依赖都已安装")
    sys.exit(1)

class MysteryResearchDemo:
    """神秘事件研究系统演示"""
    
    def __init__(self):
        self.demo_queries = [
            {
                "title": "百慕大三角神秘失踪",
                "query": "研究百慕大三角区域的飞机和船只神秘失踪事件，分析可能的原因和模式",
                "expected_types": [MysteryEventType.DISAPPEARANCE, MysteryEventType.PARANORMAL]
            },
            {
                "title": "不明飞行物目击报告",
                "query": "收集和分析最近的UFO目击报告，特别关注多目击者事件和雷达确认案例",
                "expected_types": [MysteryEventType.UFO]
            },
            {
                "title": "古代文明未解之谜",
                "query": "探索古代文明的建筑技术谜团，如金字塔建造方法和巨石阵的用途",
                "expected_types": [MysteryEventType.ANCIENT_MYSTERY]
            },
            {
                "title": "超自然现象调查",
                "query": "调查有记录的超自然现象，包括鬼魂目击、灵异事件和无法解释的现象",
                "expected_types": [MysteryEventType.PARANORMAL]
            },
            {
                "title": "密码学历史谜题",
                "query": "研究历史上著名的未破解密码和神秘文字，如伏尼契手稿和线性文字A",
                "expected_types": [MysteryEventType.ANCIENT_MYSTERY]
            }
        ]
    
    def print_banner(self):
        """打印横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    神秘事件研究系统演示                        ║
║                Mystery Event Research System Demo           ║
║                                                            ║
║  🔍 智能搜索  📊 数据分析  🤖 AI驱动  📈 可信度评估           ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def print_menu(self):
        """打印菜单"""
        print("\n📋 演示选项:")
        print("1. 🔧 配置验证")
        print("2. 🧪 模拟数据演示")
        print("3. 🔍 预设查询演示")
        print("4. 💬 自定义查询")
        print("5. 📊 系统信息")
        print("6. 🚀 完整工作流演示")
        print("0. 🚪 退出")
        print("-" * 50)
    
    def validate_system_config(self):
        """验证系统配置"""
        print("\n🔧 正在验证系统配置...")
        
        try:
            is_valid = validate_config(show_info=True)
            
            if is_valid:
                print("\n✅ 配置验证通过！系统可以正常运行。")
            else:
                print("\n⚠️  配置验证发现问题，请查看上述建议。")
                
        except Exception as e:
            print(f"\n❌ 配置验证失败: {e}")
            print("💡 提示: 请确保配置文件存在且格式正确")
    
    def demo_with_mock_data(self):
        """使用模拟数据演示"""
        print("\n🧪 模拟数据演示")
        print("=" * 30)
        
        # 创建模拟神秘事件
        mock_events = [
            MysteryEvent(
                title="百慕大三角MH370失踪事件",
                description="马来西亚航空MH370航班在百慕大三角附近区域神秘失踪，至今下落不明",
                event_type=MysteryEventType.DISAPPEARANCE,
                location="百慕大三角",
                date="2014-03-08",
                source_url="https://example.com/mh370",
                credibility_score=0.85
            ),
            MysteryEvent(
                title="凤凰城光点事件",
                description="1997年3月13日，数千人目击到巨大的V形不明飞行物飞过凤凰城",
                event_type=MysteryEventType.UFO_SIGHTING,
                location="亚利桑那州凤凰城",
                date="1997-03-13",
                source_url="https://example.com/phoenix-lights",
                credibility_score=0.92
            ),
            MysteryEvent(
                title="纳斯卡线条之谜",
                description="秘鲁纳斯卡高原上的巨大地画，只能从空中观察，制作目的和方法成谜",
                event_type=MysteryEventType.ANCIENT_MYSTERY,
                location="秘鲁纳斯卡",
                date="公元前500年-公元500年",
                source_url="https://example.com/nazca-lines",
                credibility_score=0.95
            )
        ]
        
        # 创建模拟学术文档
        mock_documents = [
            Document(
                title="百慕大三角现象的科学分析",
                content="通过统计分析和海洋学研究，探讨百慕大三角失踪事件的可能原因...",
                source_url="https://academic.example.com/bermuda-analysis",
                doc_type="academic_paper",
                metadata={
                    "author": "Dr. Marine Johnson",
                    "journal": "Ocean Mystery Research",
                    "year": 2023,
                    "citations": 45
                }
            ),
            Document(
                title="不明飞行物目击报告的心理学研究",
                content="分析UFO目击报告的心理学因素和认知偏差...",
                source_url="https://academic.example.com/ufo-psychology",
                doc_type="academic_paper",
                metadata={
                    "author": "Prof. Sarah Chen",
                    "journal": "Psychology of Anomalous Experiences",
                    "year": 2022,
                    "citations": 78
                }
            )
        ]
        
        # 显示模拟数据
        print("\n📊 模拟神秘事件:")
        for i, event in enumerate(mock_events, 1):
            print(f"\n{i}. {event.title}")
            print(f"   类型: {event.event_type.value}")
            print(f"   地点: {event.location}")
            print(f"   日期: {event.date}")
            print(f"   可信度: {event.credibility_score:.2f}")
            print(f"   描述: {event.description[:100]}...")
        
        print("\n📚 模拟学术资源:")
        for i, doc in enumerate(mock_documents, 1):
            print(f"\n{i}. {doc.title}")
            print(f"   类型: {doc.doc_type}")
            print(f"   作者: {doc.metadata.get('author', 'Unknown')}")
            print(f"   年份: {doc.metadata.get('year', 'Unknown')}")
            print(f"   引用数: {doc.metadata.get('citations', 0)}")
        
        # 模拟分析结果
        print("\n🔍 模拟分析结果:")
        print("\n📈 可信度分析:")
        print(f"  • 平均可信度: {sum(e.credibility_score for e in mock_events) / len(mock_events):.2f}")
        print(f"  • 最高可信度: {max(e.credibility_score for e in mock_events):.2f} ({max(mock_events, key=lambda x: x.credibility_score).title})")
        print(f"  • 最低可信度: {min(e.credibility_score for e in mock_events):.2f} ({min(mock_events, key=lambda x: x.credibility_score).title})")
        
        print("\n🔗 关联分析:")
        print("  • 地理关联: 百慕大三角事件与其他海域失踪案例存在模式相似性")
        print("  • 时间关联: UFO目击事件在特定时期呈现集中趋势")
        print("  • 类型关联: 古代谜团与现代考古发现存在技术关联")
        
        print("\n📋 模拟报告摘要:")
        print("  基于3个神秘事件和2个学术资源的分析显示，不同类型的神秘现象")
        print("  在地理分布、时间模式和可信度方面存在显著差异。建议进一步")
        print("  收集数据以验证初步发现的关联模式。")
    
    def demo_preset_queries(self):
        """预设查询演示"""
        print("\n🔍 预设查询演示")
        print("=" * 30)
        
        print("\n📝 可用的预设查询:")
        for i, demo in enumerate(self.demo_queries, 1):
            print(f"\n{i}. {demo['title']}")
            print(f"   查询: {demo['query'][:80]}...")
            print(f"   预期类型: {', '.join([t.value for t in demo['expected_types']])[:50]}...")
        
        try:
            choice = input("\n请选择一个查询 (1-5): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(self.demo_queries):
                selected = self.demo_queries[int(choice) - 1]
                print(f"\n🎯 已选择: {selected['title']}")
                print(f"📝 查询内容: {selected['query']}")
                
                # 询问是否执行
                execute = input("\n是否执行此查询？(y/N): ").strip().lower()
                if execute == 'y':
                    self.run_query(selected['query'])
                else:
                    print("已取消执行")
            else:
                print("❌ 无效选择")
        except KeyboardInterrupt:
            print("\n操作已取消")
    
    def custom_query_demo(self):
        """自定义查询演示"""
        print("\n💬 自定义查询")
        print("=" * 30)
        
        print("\n💡 提示: 请输入您想要研究的神秘事件或现象")
        print("例如: '调查罗斯威尔UFO事件的真相'")
        print("     '分析埃及金字塔的建造技术'")
        print("     '研究百慕大三角的失踪模式'")
        
        try:
            query = input("\n🔍 请输入您的查询: ").strip()
            
            if not query:
                print("❌ 查询不能为空")
                return
            
            if len(query) < 10:
                print("❌ 查询太短，请提供更详细的描述")
                return
            
            print(f"\n📝 您的查询: {query}")
            
            # 询问是否执行
            execute = input("\n是否执行此查询？(y/N): ").strip().lower()
            if execute == 'y':
                self.run_query(query)
            else:
                print("已取消执行")
                
        except KeyboardInterrupt:
            print("\n操作已取消")
    
    def show_system_info(self):
        """显示系统信息"""
        print("\n📊 系统信息")
        print("=" * 30)
        
        try:
            from __version__ import (
                __version__, __title__, __description__, __author__,
                SUPPORTED_PYTHON_VERSIONS, SUPPORTED_PLATFORMS,
                SUPPORTED_DATABASES, SUPPORTED_AI_MODELS
            )
            
            print(f"\n🏷️  系统名称: {__title__}")
            print(f"📦 版本: {__version__}")
            print(f"📝 描述: {__description__}")
            print(f"👨‍💻 作者: {__author__}")
            
            print(f"\n🐍 支持的Python版本: {', '.join(SUPPORTED_PYTHON_VERSIONS)}")
            print(f"💻 支持的平台: {', '.join(SUPPORTED_PLATFORMS)}")
            print(f"🗄️  支持的数据库: {', '.join(SUPPORTED_DATABASES)}")
            print(f"🤖 支持的AI模型: {', '.join(SUPPORTED_AI_MODELS)}")
            
        except ImportError:
            print("⚠️  无法加载版本信息")
        
        # 显示运行时信息
        print(f"\n🔧 运行时信息:")
        print(f"   Python版本: {sys.version.split()[0]}")
        print(f"   平台: {sys.platform}")
        print(f"   工作目录: {os.getcwd()}")
        print(f"   项目根目录: {project_root}")
        
        # 显示环境变量状态
        print(f"\n🔑 环境变量状态:")
        env_vars = [
            'OPENAI_API_KEY',
            'ANTHROPIC_API_KEY',
            'TAVILY_API_KEY',
            'NEO4J_URI',
            'ELASTICSEARCH_URL'
        ]
        
        for var in env_vars:
            status = "✅ 已设置" if os.getenv(var) else "❌ 未设置"
            print(f"   {var}: {status}")
    
    def run_full_workflow_demo(self):
        """运行完整工作流演示"""
        print("\n🚀 完整工作流演示")
        print("=" * 30)
        
        print("\n⚠️  注意: 此演示将尝试运行完整的研究工作流")
        print("需要有效的API密钥和网络连接")
        
        confirm = input("\n是否继续？(y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消演示")
            return
        
        # 选择一个简单的查询
        demo_query = "研究百慕大三角的神秘现象"
        print(f"\n🔍 演示查询: {demo_query}")
        
        try:
            self.run_query(demo_query, full_workflow=True)
        except Exception as e:
            print(f"\n❌ 工作流执行失败: {e}")
            print("💡 这可能是由于缺少API密钥或网络问题")
    
    def run_query(self, query: str, full_workflow: bool = False):
        """运行查询"""
        print(f"\n🔄 正在处理查询: {query}")
        print("⏳ 请稍候...")
        
        try:
            if full_workflow:
                # 运行完整工作流
                result = run_mystery_research_workflow(
                    user_input=query,
                    locale="zh-CN",
                    debug=True,
                    max_plan_iterations=3,
                    max_step_num=10,
                    enable_background_investigation=True,
                    enable_academic_search=True,
                    enable_credibility_filter=True,
                    enable_correlation_analysis=True,
                    enable_graph_storage=False  # 演示时禁用
                )
                
                if result and 'final_report' in result:
                    print("\n📋 研究报告:")
                    print("-" * 50)
                    print(result['final_report'])
                else:
                    print("\n⚠️  未生成完整报告")
            else:
                # 模拟处理
                import time
                
                steps = [
                    "🔍 分析查询内容",
                    "📊 制定研究计划",
                    "🌐 搜索相关信息",
                    "📚 查找学术资源",
                    "🔬 分析可信度",
                    "🔗 进行关联分析",
                    "📝 生成报告"
                ]
                
                for step in steps:
                    print(f"\n{step}...")
                    time.sleep(1)  # 模拟处理时间
                
                print("\n✅ 查询处理完成（模拟）")
                print("\n💡 在实际运行中，这里会显示详细的研究结果")
                
        except Exception as e:
            print(f"\n❌ 查询执行失败: {e}")
            print("💡 这可能是由于配置问题或缺少依赖")
    
    def run(self):
        """运行演示"""
        self.print_banner()
        
        while True:
            try:
                self.print_menu()
                choice = input("请选择操作 (0-6): ").strip()
                
                if choice == '0':
                    print("\n👋 感谢使用神秘事件研究系统演示！")
                    break
                elif choice == '1':
                    self.validate_system_config()
                elif choice == '2':
                    self.demo_with_mock_data()
                elif choice == '3':
                    self.demo_preset_queries()
                elif choice == '4':
                    self.custom_query_demo()
                elif choice == '5':
                    self.show_system_info()
                elif choice == '6':
                    self.run_full_workflow_demo()
                else:
                    print("❌ 无效选择，请重试")
                
                input("\n按回车键继续...")
                
            except KeyboardInterrupt:
                print("\n\n👋 演示已退出")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                input("按回车键继续...")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="神秘事件研究系统演示",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python demo.py                    # 交互式演示
  python demo.py --quick           # 快速演示
  python demo.py --query "UFO事件"  # 直接查询
  python demo.py --validate        # 只验证配置
        """
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="运行快速演示（模拟数据）"
    )
    
    parser.add_argument(
        "--query",
        type=str,
        help="直接执行指定查询"
    )
    
    parser.add_argument(
        "--validate",
        action="store_true",
        help="只验证系统配置"
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="运行完整工作流（需要API密钥）"
    )
    
    args = parser.parse_args()
    
    demo = MysteryResearchDemo()
    
    if args.validate:
        demo.validate_system_config()
    elif args.quick:
        demo.print_banner()
        demo.demo_with_mock_data()
    elif args.query:
        demo.print_banner()
        demo.run_query(args.query, full_workflow=args.full)
    else:
        demo.run()

if __name__ == "__main__":
    main()