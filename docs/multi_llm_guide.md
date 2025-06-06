# 多LLM支持指南

## 概述

Lingjing神秘事件研究系统现在支持多种大语言模型(LLM)提供商，包括国内外主流的AI服务。系统提供了统一的接口来管理和使用不同的LLM，支持自动回退、负载均衡和配置管理。

## 支持的LLM提供商

### 国际提供商
- **OpenAI**: GPT-4, GPT-3.5等模型
- **Anthropic**: Claude系列模型
- **Google**: Gemini Pro等模型
- **Ollama**: 本地部署的开源模型

### 国内提供商
- **阿里云通义千问**: Qwen系列模型
- **智谱AI**: GLM系列模型
- **百度文心一言**: ERNIE系列模型

## 配置方法

### 1. 环境变量配置

复制`.env.example`文件为`.env`，并配置相应的API密钥：

```bash
cp .env.example .env
```

编辑`.env`文件，填入你的API密钥：

```env
# OpenAI配置
OPENAI_API_KEY=your_actual_api_key_here

# Anthropic配置
ANTHROPIC_API_KEY=your_actual_api_key_here

# 其他提供商配置...
```

### 2. YAML配置文件

系统会自动加载`config/llm_config.yaml`中的配置。你可以在此文件中：

- 设置不同LLM类型的默认模型
- 配置温度、最大token等参数
- 设置提供商优先级
- 配置回退策略

## 使用方法

### 1. 基本使用

```python
from llms import get_llm_by_type, LLMType

# 获取研究类型的LLM
research_llm = get_llm_by_type(LLMType.RESEARCH)

# 获取分析类型的LLM
analysis_llm = get_llm_by_type(LLMType.ANALYSIS)

# 使用LLM
response = research_llm.invoke("请分析这个神秘事件...")
```

### 2. 指定提供商

```python
from llms import create_llm_from_config

# 创建特定提供商的LLM
openai_llm = create_llm_from_config(
    provider="openai",
    llm_type=LLMType.RESEARCH,
    model="gpt-4",
    temperature=0.3
)

qwen_llm = create_llm_from_config(
    provider="qwen",
    llm_type=LLMType.ANALYSIS,
    model="qwen-max"
)
```

### 3. 在Agent中使用

```python
from agents import create_mystery_agent
from config.agents import get_agent_config

# 创建使用特定LLM类型的Agent
researcher = create_mystery_agent(
    agent_type="academic_researcher",
    llm_type=LLMType.RESEARCH,
    mystery_config={"focus": "科学分析"}
)

# Agent会自动使用配置的LLM
result = researcher.invoke({
    "input": "请研究这个UFO目击事件",
    "mystery_events": [...],
    "academic_resources": [...]
})
```

## LLM类型说明

系统定义了以下LLM类型，每种类型针对不同的使用场景优化：

- **BASIC**: 基础对话和简单任务
- **REASONING**: 复杂推理和逻辑分析
- **VISION**: 图像理解和多模态任务
- **FAST**: 快速响应的轻量级任务
- **EMBEDDING**: 文本嵌入和相似度计算
- **CODE**: 代码生成和分析
- **RESEARCH**: 深度研究和学术分析
- **ANALYSIS**: 数据分析和模式识别

## 回退机制

系统支持自动回退机制，当主要提供商不可用时，会自动切换到备用提供商：

1. **优先级回退**: 按照配置的提供商优先级顺序尝试
2. **错误重试**: 支持配置重试次数和延迟
3. **健康检查**: 定期检查提供商可用性

配置示例：

```env
LLM_PROVIDER_PRIORITY=openai,qwen,anthropic,google
LLM_FALLBACK_ENABLED=true
LLM_MAX_RETRIES=3
LLM_RETRY_DELAY=1.0
```

## 性能优化

### 1. 缓存机制

```env
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL=3600
LLM_CACHE_MAX_SIZE=1000
```

### 2. 速率限制

```env
LLM_RATE_LIMIT_ENABLED=true
LLM_REQUESTS_PER_MINUTE=60
LLM_TOKENS_PER_MINUTE=100000
```

### 3. 并发控制

系统支持并发请求控制，避免超出API限制。

## 监控和日志

系统提供详细的LLM使用监控：

- **请求统计**: 记录每个提供商的请求次数和成功率
- **性能监控**: 跟踪响应时间和token使用量
- **错误日志**: 记录失败请求和错误原因
- **成本跟踪**: 估算API使用成本

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查`.env`文件中的API密钥是否正确
   - 确认API密钥有足够的权限和余额

2. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置
   - 考虑使用代理设置

3. **模型不可用**
   - 检查模型名称是否正确
   - 确认你的账户有权限访问该模型

4. **速率限制**
   - 调整请求频率
   - 配置合适的重试策略

### 调试模式

启用调试模式获取详细日志：

```env
LOG_LEVEL=DEBUG
LLM_DEBUG_ENABLED=true
```

## 最佳实践

1. **选择合适的LLM类型**: 根据任务特点选择最适合的LLM类型
2. **配置回退策略**: 设置多个提供商以确保服务可用性
3. **监控使用情况**: 定期检查API使用量和成本
4. **优化提示词**: 针对不同模型优化提示词以获得最佳效果
5. **缓存策略**: 合理使用缓存减少API调用

## 示例代码

完整的使用示例请参考`examples/llm_usage_example.py`文件。

## 更新日志

- **v1.0.0**: 初始版本，支持基本的多LLM功能
- **v1.1.0**: 添加回退机制和缓存支持
- **v1.2.0**: 增加国内LLM提供商支持
- **v1.3.0**: 添加监控和性能优化功能