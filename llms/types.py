# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

from enum import Enum
from typing import Literal


class LLMType(str, Enum):
    """Supported LLM types for different tasks."""
    
    # Basic models for general tasks
    BASIC = "basic"
    
    # Advanced reasoning models for complex analysis
    REASONING = "reasoning"
    
    # Vision models for image/video analysis
    VISION = "vision"
    
    # Fast models for quick responses
    FAST = "fast"
    
    # Embedding models for vector representations
    EMBEDDING = "embedding"
    
    # Code generation models
    CODE = "code"
    
    # Research-specific models
    RESEARCH = "research"
    
    # Analysis-specific models
    ANALYSIS = "analysis"


# Type alias for better type hints
LLMTypeStr = Literal[
    "basic",
    "reasoning", 
    "vision",
    "fast",
    "embedding",
    "code",
    "research",
    "analysis"
]


# Default LLM configurations for different providers
DEFAULT_LLM_CONFIGS = {
    "openai": {
        LLMType.BASIC: {
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 4000,
        },
        LLMType.REASONING: {
            "model": "gpt-4o",
            "temperature": 0.3,
            "max_tokens": 8000,
        },
        LLMType.VISION: {
            "model": "gpt-4o",
            "temperature": 0.5,
            "max_tokens": 4000,
        },
        LLMType.FAST: {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        LLMType.CODE: {
            "model": "gpt-4o",
            "temperature": 0.1,
            "max_tokens": 6000,
        },
        LLMType.RESEARCH: {
            "model": "gpt-4o",
            "temperature": 0.3,
            "max_tokens": 8000,
        },
        LLMType.ANALYSIS: {
            "model": "gpt-4o",
            "temperature": 0.2,
            "max_tokens": 6000,
        },
    },
    "anthropic": {
        LLMType.BASIC: {
            "model": "claude-3-haiku-20240307",
            "temperature": 0.7,
            "max_tokens": 4000,
        },
        LLMType.REASONING: {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.3,
            "max_tokens": 8000,
        },
        LLMType.VISION: {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.5,
            "max_tokens": 4000,
        },
        LLMType.FAST: {
            "model": "claude-3-haiku-20240307",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        LLMType.CODE: {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.1,
            "max_tokens": 6000,
        },
        LLMType.RESEARCH: {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.3,
            "max_tokens": 8000,
        },
        LLMType.ANALYSIS: {
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.2,
            "max_tokens": 6000,
        },
    },
    "google": {
        LLMType.BASIC: {
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 4000,
        },
        LLMType.REASONING: {
            "model": "gemini-1.5-pro",
            "temperature": 0.3,
            "max_tokens": 8000,
        },
        LLMType.VISION: {
            "model": "gemini-1.5-pro",
            "temperature": 0.5,
            "max_tokens": 4000,
        },
        LLMType.FAST: {
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        LLMType.CODE: {
            "model": "gemini-1.5-pro",
            "temperature": 0.1,
            "max_tokens": 6000,
        },
        LLMType.RESEARCH: {
            "model": "gemini-1.5-pro",
            "temperature": 0.3,
            "max_tokens": 8000,
        },
        LLMType.ANALYSIS: {
            "model": "gemini-1.5-pro",
            "temperature": 0.2,
            "max_tokens": 6000,
        },
    },
    "qwen": {
        LLMType.BASIC: {
            "model": "qwen2.5-7b-instruct",
            "temperature": 0.7,
            "max_tokens": 4000,
        },
        LLMType.REASONING: {
            "model": "qwen2.5-72b-instruct",
            "temperature": 0.3,
            "max_tokens": 8000,
        },
        LLMType.VISION: {
            "model": "qwen2-vl-72b-instruct",
            "temperature": 0.5,
            "max_tokens": 4000,
        },
        LLMType.FAST: {
            "model": "qwen2.5-3b-instruct",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        LLMType.CODE: {
            "model": "qwen2.5-coder-32b-instruct",
            "temperature": 0.1,
            "max_tokens": 6000,
        },
        LLMType.RESEARCH: {
            "model": "qwen2.5-72b-instruct",
            "temperature": 0.3,
            "max_tokens": 8000,
        },
        LLMType.ANALYSIS: {
            "model": "qwen2.5-72b-instruct",
            "temperature": 0.2,
            "max_tokens": 6000,
        },
    },
}