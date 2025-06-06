#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神秘事件研究系统 - 配置验证器
Mystery Event Research System - Configuration Validator
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ValidationLevel(Enum):
    """验证级别"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationResult:
    """验证结果"""
    level: ValidationLevel
    message: str
    key: Optional[str] = None
    suggestion: Optional[str] = None

class ConfigValidator:
    """配置验证器"""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path(__file__).parent
        self.results: List[ValidationResult] = []
    
    def validate_all(self) -> List[ValidationResult]:
        """验证所有配置"""
        self.results.clear()
        
        # 验证配置文件存在性
        self._validate_config_files()
        
        # 验证配置结构
        self._validate_config_structure()
        
        # 验证API密钥
        self._validate_api_keys()
        
        # 验证数据库连接
        self._validate_database_config()
        
        # 验证AI模型配置
        self._validate_ai_config()
        
        # 验证搜索引擎配置
        self._validate_search_config()
        
        # 验证爬虫配置
        self._validate_crawler_config()
        
        # 验证工作流配置
        self._validate_workflow_config()
        
        # 验证性能配置
        self._validate_performance_config()
        
        return self.results
    
    def _add_result(self, level: ValidationLevel, message: str, 
                   key: str = None, suggestion: str = None):
        """添加验证结果"""
        self.results.append(ValidationResult(
            level=level,
            message=message,
            key=key,
            suggestion=suggestion
        ))
    
    def _validate_config_files(self):
        """验证配置文件存在性"""
        default_config = self.config_dir / "default.yaml"
        
        if not default_config.exists():
            self._add_result(
                ValidationLevel.ERROR,
                "默认配置文件不存在",
                suggestion="请确保default.yaml文件存在"
            )
            return
        
        # 检查配置文件格式
        try:
            with open(default_config, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            self._add_result(
                ValidationLevel.ERROR,
                f"默认配置文件格式错误: {e}",
                suggestion="请检查YAML语法"
            )
        
        # 检查用户配置文件
        user_config = self.config_dir / "user.yaml"
        if user_config.exists():
            try:
                with open(user_config, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                self._add_result(
                    ValidationLevel.INFO,
                    "找到用户配置文件"
                )
            except yaml.YAMLError as e:
                self._add_result(
                    ValidationLevel.ERROR,
                    f"用户配置文件格式错误: {e}",
                    suggestion="请检查user.yaml的YAML语法"
                )
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config = {}
        
        # 加载默认配置
        default_config = self.config_dir / "default.yaml"
        if default_config.exists():
            try:
                with open(default_config, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {}
            except Exception:
                return {}
        
        # 加载用户配置
        user_config = self.config_dir / "user.yaml"
        if user_config.exists():
            try:
                with open(user_config, 'r', encoding='utf-8') as f:
                    user_cfg = yaml.safe_load(f) or {}
                    config.update(user_cfg)
            except Exception:
                pass
        
        return config
    
    def _validate_config_structure(self):
        """验证配置结构"""
        config = self._load_config()
        
        if not config:
            self._add_result(
                ValidationLevel.ERROR,
                "无法加载配置文件"
            )
            return
        
        # 必需的顶级键
        required_keys = [
            'system',
            'ai',
            'search',
            'database',
            'crawler',
            'workflow'
        ]
        
        for key in required_keys:
            if key not in config:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"缺少配置节: {key}",
                    key=key,
                    suggestion=f"请在配置文件中添加{key}节"
                )
    
    def _validate_api_keys(self):
        """验证API密钥"""
        # 检查环境变量中的API密钥
        api_keys = {
            'OPENAI_API_KEY': 'OpenAI',
            'ANTHROPIC_API_KEY': 'Anthropic',
            'GOOGLE_API_KEY': 'Google',
            'TAVILY_API_KEY': 'Tavily',
            'BING_SEARCH_API_KEY': 'Bing Search',
            'GOOGLE_SEARCH_API_KEY': 'Google Search'
        }
        
        found_keys = []
        for env_key, service in api_keys.items():
            if os.getenv(env_key):
                found_keys.append(service)
                self._add_result(
                    ValidationLevel.INFO,
                    f"找到{service} API密钥"
                )
        
        if not found_keys:
            self._add_result(
                ValidationLevel.WARNING,
                "未找到任何API密钥",
                suggestion="请设置至少一个AI服务和搜索服务的API密钥"
            )
    
    def _validate_database_config(self):
        """验证数据库配置"""
        config = self._load_config()
        db_config = config.get('database', {})
        
        # 检查Neo4j配置
        neo4j_config = db_config.get('neo4j', {})
        if neo4j_config:
            required_neo4j = ['uri', 'user', 'password']
            for key in required_neo4j:
                if not neo4j_config.get(key) and not os.getenv(f'NEO4J_{key.upper()}'):
                    self._add_result(
                        ValidationLevel.WARNING,
                        f"Neo4j配置缺少: {key}",
                        key=f"database.neo4j.{key}",
                        suggestion=f"请设置Neo4j的{key}或环境变量NEO4J_{key.upper()}"
                    )
        
        # 检查Elasticsearch配置
        es_config = db_config.get('elasticsearch', {})
        if es_config and not es_config.get('hosts') and not os.getenv('ELASTICSEARCH_URL'):
            self._add_result(
                ValidationLevel.WARNING,
                "Elasticsearch配置缺少hosts",
                key="database.elasticsearch.hosts",
                suggestion="请设置Elasticsearch的hosts或环境变量ELASTICSEARCH_URL"
            )
    
    def _validate_ai_config(self):
        """验证AI配置"""
        config = self._load_config()
        ai_config = config.get('ai', {})
        
        if not ai_config:
            self._add_result(
                ValidationLevel.ERROR,
                "缺少AI配置",
                suggestion="请添加ai配置节"
            )
            return
        
        default_provider = ai_config.get('default_provider', 'openai')
        provider_config = ai_config.get(default_provider, {})
        
        if not provider_config:
            self._add_result(
                ValidationLevel.ERROR,
                f"缺少默认AI提供商配置: {default_provider}",
                key=f"ai.{default_provider}",
                suggestion=f"请添加{default_provider}的配置"
            )
        
        # 检查模型配置
        if provider_config and not provider_config.get('model'):
            self._add_result(
                ValidationLevel.WARNING,
                f"{default_provider}未指定模型",
                key=f"ai.{default_provider}.model",
                suggestion="建议指定具体的模型名称"
            )
    
    def _validate_search_config(self):
        """验证搜索配置"""
        config = self._load_config()
        search_config = config.get('search', {})
        
        if not search_config:
            self._add_result(
                ValidationLevel.ERROR,
                "缺少搜索配置",
                suggestion="请添加search配置节"
            )
            return
        
        default_engine = search_config.get('default_engine', 'tavily')
        engine_config = search_config.get(default_engine, {})
        
        if not engine_config:
            self._add_result(
                ValidationLevel.ERROR,
                f"缺少默认搜索引擎配置: {default_engine}",
                key=f"search.{default_engine}",
                suggestion=f"请添加{default_engine}的配置"
            )
    
    def _validate_crawler_config(self):
        """验证爬虫配置"""
        config = self._load_config()
        crawler_config = config.get('crawler', {})
        
        if not crawler_config:
            self._add_result(
                ValidationLevel.WARNING,
                "缺少爬虫配置",
                suggestion="建议添加crawler配置节以优化爬虫性能"
            )
            return
        
        # 检查并发设置
        max_concurrent = crawler_config.get('max_concurrent_requests', 10)
        if max_concurrent > 50:
            self._add_result(
                ValidationLevel.WARNING,
                f"爬虫并发数过高: {max_concurrent}",
                key="crawler.max_concurrent_requests",
                suggestion="建议将并发数控制在50以下以避免被封禁"
            )
        
        # 检查延迟设置
        delay = crawler_config.get('request_delay', 1.0)
        if delay < 0.5:
            self._add_result(
                ValidationLevel.WARNING,
                f"请求延迟过短: {delay}秒",
                key="crawler.request_delay",
                suggestion="建议设置至少0.5秒的请求延迟"
            )
    
    def _validate_workflow_config(self):
        """验证工作流配置"""
        config = self._load_config()
        workflow_config = config.get('workflow', {})
        
        if not workflow_config:
            self._add_result(
                ValidationLevel.WARNING,
                "缺少工作流配置",
                suggestion="建议添加workflow配置节"
            )
            return
        
        # 检查执行限制
        max_iterations = workflow_config.get('max_plan_iterations', 5)
        if max_iterations > 20:
            self._add_result(
                ValidationLevel.WARNING,
                f"计划迭代次数过高: {max_iterations}",
                key="workflow.max_plan_iterations",
                suggestion="建议将迭代次数控制在20以下"
            )
        
        max_steps = workflow_config.get('max_step_num', 20)
        if max_steps > 100:
            self._add_result(
                ValidationLevel.WARNING,
                f"最大步骤数过高: {max_steps}",
                key="workflow.max_step_num",
                suggestion="建议将步骤数控制在100以下"
            )
    
    def _validate_performance_config(self):
        """验证性能配置"""
        config = self._load_config()
        perf_config = config.get('performance', {})
        
        if perf_config:
            # 检查内存限制
            max_memory = perf_config.get('max_memory_mb', 1024)
            if max_memory < 512:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"内存限制过低: {max_memory}MB",
                    key="performance.max_memory_mb",
                    suggestion="建议至少分配512MB内存"
                )
            
            # 检查缓存设置
            cache_size = perf_config.get('cache_size_mb', 256)
            if cache_size > max_memory * 0.5:
                self._add_result(
                    ValidationLevel.WARNING,
                    f"缓存大小过大: {cache_size}MB",
                    key="performance.cache_size_mb",
                    suggestion="建议缓存大小不超过总内存的50%"
                )
    
    def print_results(self, show_info: bool = True):
        """打印验证结果"""
        if not self.results:
            print("✅ 配置验证通过，未发现问题")
            return
        
        # 按级别分组
        errors = [r for r in self.results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in self.results if r.level == ValidationLevel.WARNING]
        infos = [r for r in self.results if r.level == ValidationLevel.INFO]
        
        # 打印错误
        if errors:
            print("\n❌ 错误:")
            for result in errors:
                print(f"  • {result.message}")
                if result.suggestion:
                    print(f"    建议: {result.suggestion}")
        
        # 打印警告
        if warnings:
            print("\n⚠️  警告:")
            for result in warnings:
                print(f"  • {result.message}")
                if result.suggestion:
                    print(f"    建议: {result.suggestion}")
        
        # 打印信息
        if show_info and infos:
            print("\n💡 信息:")
            for result in infos:
                print(f"  • {result.message}")
        
        # 总结
        print(f"\n📊 验证总结: {len(errors)}个错误, {len(warnings)}个警告, {len(infos)}个信息")
        
        if errors:
            print("\n⚠️  请修复错误后再运行系统")
        elif warnings:
            print("\n💡 建议修复警告以获得更好的体验")
        else:
            print("\n✅ 配置验证通过")

def validate_config(config_dir: Path = None, show_info: bool = True) -> bool:
    """
    验证配置并打印结果
    
    Args:
        config_dir: 配置目录
        show_info: 是否显示信息级别的结果
    
    Returns:
        是否通过验证（无错误）
    """
    validator = ConfigValidator(config_dir)
    results = validator.validate_all()
    validator.print_results(show_info)
    
    # 检查是否有错误
    has_errors = any(r.level == ValidationLevel.ERROR for r in results)
    return not has_errors

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="验证神秘事件研究系统配置")
    parser.add_argument(
        "--config-dir", 
        type=Path, 
        help="配置目录路径"
    )
    parser.add_argument(
        "--no-info", 
        action="store_true", 
        help="不显示信息级别的结果"
    )
    
    args = parser.parse_args()
    
    success = validate_config(
        config_dir=args.config_dir,
        show_info=not args.no_info
    )
    
    exit(0 if success else 1)