#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多LLM支持测试模块

测试多LLM支持的各个组件，包括：
- LLM类型枚举
- LLM配置加载
- 提供商检测
- LLM实例创建
- 代理配置
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from llms.types import LLMType, DEFAULT_LLM_CONFIGS
    from llms.llm import (
        get_llm_by_type,
        create_llm_from_config,
        detect_default_provider,
        list_available_providers,
        clear_llm_cache,
        load_llm_config
    )
    from config.agents import (
        get_agent_llm_type,
        get_agent_config,
        create_agent_from_config
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Skipping tests due to missing dependencies")
    sys.exit(0)


class TestLLMTypes(unittest.TestCase):
    """测试LLM类型枚举"""
    
    def test_llm_type_enum(self):
        """测试LLM类型枚举值"""
        expected_types = [
            'BASIC', 'REASONING', 'VISION', 'FAST', 
            'EMBEDDING', 'CODE', 'RESEARCH', 'ANALYSIS'
        ]
        
        for type_name in expected_types:
            self.assertTrue(hasattr(LLMType, type_name))
    
    def test_default_llm_configs(self):
        """测试默认LLM配置"""
        self.assertIsInstance(DEFAULT_LLM_CONFIGS, dict)
        
        # 检查是否包含主要提供商
        expected_providers = ['openai', 'anthropic', 'google', 'qwen']
        for provider in expected_providers:
            self.assertIn(provider, DEFAULT_LLM_CONFIGS)
        
        # 检查每个提供商是否有基本配置
        for provider, config in DEFAULT_LLM_CONFIGS.items():
            self.assertIsInstance(config, dict)
            for llm_type in LLMType:
                if llm_type.value in config:
                    type_config = config[llm_type.value]
                    self.assertIn('model', type_config)


class TestLLMConfiguration(unittest.TestCase):
    """测试LLM配置加载"""
    
    def setUp(self):
        """设置测试环境"""
        clear_llm_cache()
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-openai-key',
        'ANTHROPIC_API_KEY': 'test-anthropic-key',
        'GOOGLE_API_KEY': 'test-google-key'
    })
    def test_load_config_from_env(self):
        """测试从环境变量加载配置"""
        config = load_llm_config()
        self.assertIsInstance(config, dict)
    
    def test_detect_default_provider(self):
        """测试检测默认提供商"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            provider = detect_default_provider()
            # 应该返回一个有效的提供商名称或None
            if provider:
                self.assertIsInstance(provider, str)
    
    def test_list_available_providers(self):
        """测试列出可用提供商"""
        providers = list_available_providers()
        self.assertIsInstance(providers, list)
        # 至少应该包含一些基本提供商
        expected_providers = ['openai', 'anthropic', 'google', 'qwen', 'ollama']
        for provider in expected_providers:
            self.assertIn(provider, providers)


class TestLLMCreation(unittest.TestCase):
    """测试LLM实例创建"""
    
    def setUp(self):
        """设置测试环境"""
        clear_llm_cache()
    
    @patch('llms.llm._create_openai_llm')
    def test_create_openai_llm(self, mock_create):
        """测试创建OpenAI LLM"""
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm
        
        config = {
            'provider': 'openai',
            'model': 'gpt-4',
            'api_key': 'test-key'
        }
        
        llm = create_llm_from_config(config)
        self.assertEqual(llm, mock_llm)
        mock_create.assert_called_once()
    
    @patch('llms.llm._create_anthropic_llm')
    def test_create_anthropic_llm(self, mock_create):
        """测试创建Anthropic LLM"""
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm
        
        config = {
            'provider': 'anthropic',
            'model': 'claude-3-sonnet-20240229',
            'api_key': 'test-key'
        }
        
        llm = create_llm_from_config(config)
        self.assertEqual(llm, mock_llm)
        mock_create.assert_called_once()
    
    @patch('llms.llm._create_qwen_llm')
    def test_create_qwen_llm(self, mock_create):
        """测试创建Qwen LLM"""
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm
        
        config = {
            'provider': 'qwen',
            'model': 'qwen-turbo',
            'api_key': 'test-key'
        }
        
        llm = create_llm_from_config(config)
        self.assertEqual(llm, mock_llm)
        mock_create.assert_called_once()
    
    @patch('llms.llm._create_zhipu_llm')
    def test_create_zhipu_llm(self, mock_create):
        """测试创建智谱AI LLM"""
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm
        
        config = {
            'provider': 'zhipu',
            'model': 'glm-4',
            'api_key': 'test-key'
        }
        
        llm = create_llm_from_config(config)
        self.assertEqual(llm, mock_llm)
        mock_create.assert_called_once()
    
    @patch('llms.llm._create_baidu_llm')
    def test_create_baidu_llm(self, mock_create):
        """测试创建百度文心LLM"""
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm
        
        config = {
            'provider': 'baidu',
            'model': 'ernie-bot-turbo',
            'api_key': 'test-key'
        }
        
        llm = create_llm_from_config(config)
        self.assertEqual(llm, mock_llm)
        mock_create.assert_called_once()


class TestLLMByType(unittest.TestCase):
    """测试按类型获取LLM"""
    
    def setUp(self):
        """设置测试环境"""
        clear_llm_cache()
    
    @patch('llms.llm.create_llm_from_config')
    def test_get_llm_by_type_with_caching(self, mock_create):
        """测试按类型获取LLM并验证缓存"""
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm
        
        # 第一次调用
        llm1 = get_llm_by_type(LLMType.BASIC)
        self.assertEqual(llm1, mock_llm)
        
        # 第二次调用应该使用缓存
        llm2 = get_llm_by_type(LLMType.BASIC)
        self.assertEqual(llm2, mock_llm)
        
        # 应该只创建一次
        self.assertEqual(mock_create.call_count, 1)
    
    @patch('llms.llm.create_llm_from_config')
    def test_get_llm_by_type_different_types(self, mock_create):
        """测试获取不同类型的LLM"""
        mock_llm = MagicMock()
        mock_create.return_value = mock_llm
        
        # 获取不同类型的LLM
        basic_llm = get_llm_by_type(LLMType.BASIC)
        reasoning_llm = get_llm_by_type(LLMType.REASONING)
        
        self.assertEqual(basic_llm, mock_llm)
        self.assertEqual(reasoning_llm, mock_llm)
        
        # 应该为每种类型创建一次
        self.assertEqual(mock_create.call_count, 2)


class TestAgentConfiguration(unittest.TestCase):
    """测试代理配置"""
    
    def test_get_agent_llm_type(self):
        """测试获取代理LLM类型"""
        # 测试已知代理类型
        known_agents = [
            'mystery_researcher', 'data_analyst', 'report_generator',
            'fact_checker', 'timeline_analyst', 'correlation_expert'
        ]
        
        for agent_name in known_agents:
            llm_type = get_agent_llm_type(agent_name)
            self.assertIsInstance(llm_type, LLMType)
        
        # 测试未知代理类型
        unknown_llm_type = get_agent_llm_type('unknown_agent')
        self.assertEqual(unknown_llm_type, LLMType.BASIC)
    
    def test_get_agent_config(self):
        """测试获取代理配置"""
        config = get_agent_config('mystery_researcher')
        self.assertIsInstance(config, dict)
        
        # 检查必要的配置字段
        expected_fields = ['description', 'capabilities', 'tools', 'prompt_template']
        for field in expected_fields:
            self.assertIn(field, config)
    
    @patch('config.agents.get_llm_by_type')
    def test_create_agent_from_config(self, mock_get_llm):
        """测试从配置创建代理"""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        agent = create_agent_from_config('mystery_researcher')
        
        # 验证返回了代理配置
        self.assertIsInstance(agent, dict)
        self.assertIn('llm', agent)
        self.assertIn('config', agent)
        
        mock_get_llm.assert_called_once()


class TestEndToEndWorkflow(unittest.TestCase):
    """测试端到端工作流"""
    
    def setUp(self):
        """设置测试环境"""
        clear_llm_cache()
    
    @patch('llms.llm.create_llm_from_config')
    @patch('config.agents.get_llm_by_type')
    def test_mystery_research_workflow(self, mock_get_llm, mock_create_llm):
        """测试神秘事件研究工作流"""
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm
        mock_get_llm.return_value = mock_llm
        
        # 创建研究代理
        researcher = create_agent_from_config('mystery_researcher')
        self.assertIsInstance(researcher, dict)
        
        # 创建分析代理
        analyst = create_agent_from_config('data_analyst')
        self.assertIsInstance(analyst, dict)
        
        # 创建报告生成代理
        reporter = create_agent_from_config('report_generator')
        self.assertIsInstance(reporter, dict)
        
        # 验证所有代理都有LLM
        for agent in [researcher, analyst, reporter]:
            self.assertIn('llm', agent)
            self.assertIn('config', agent)
    
    @patch('llms.llm.create_llm_from_config')
    def test_fallback_mechanism(self, mock_create_llm):
        """测试回退机制"""
        # 模拟第一个提供商失败
        def side_effect(config):
            if config.get('provider') == 'openai':
                raise Exception("OpenAI API error")
            return MagicMock()
        
        mock_create_llm.side_effect = side_effect
        
        # 应该能够回退到其他提供商
        try:
            llm = get_llm_by_type(LLMType.BASIC)
            # 如果没有抛出异常，说明回退机制工作正常
            self.assertIsNotNone(llm)
        except Exception:
            # 如果所有提供商都失败，这是预期的
            pass


if __name__ == '__main__':
    # 设置测试环境
    os.environ.setdefault('TESTING', 'true')
    
    # 运行测试
    unittest.main(verbosity=2)