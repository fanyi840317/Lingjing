# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union, List
from functools import lru_cache

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_community.llms import Ollama
except ImportError:
    Ollama = None

from .types import LLMType, DEFAULT_LLM_CONFIGS
from config.configuration import load_yaml_config

logger = logging.getLogger(__name__)

# Cache for LLM instances
_llm_cache: Dict[str, Any] = {}

# Configuration cache
_config_cache: Optional[Dict] = None

# Available LLM providers
AVAILABLE_PROVIDERS = {
    "openai": "OpenAI GPT models",
    "anthropic": "Anthropic Claude models", 
    "google": "Google Gemini models",
    "ollama": "Local Ollama models",
    "qwen": "Alibaba Qwen models",
    "zhipu": "Zhipu AI GLM models",
    "baidu": "Baidu ERNIE models"
}


def load_llm_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load LLM configuration from YAML file."""
    global _config_cache
    
    if _config_cache is not None:
        return _config_cache
    
    if config_path is None:
        # Try to find config file in common locations
        possible_paths = [
            "config/llm_config.yaml",
            "llm_config.yaml",
            os.path.expanduser("~/.lingjing/llm_config.yaml"),
            "/etc/lingjing/llm_config.yaml"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
    
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                # Expand environment variables
                config = _expand_env_vars(config)
                _config_cache = config
                logger.info(f"Loaded LLM config from {config_path}")
                return config
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
    
    # Fallback to default configuration
    logger.info("Using default LLM configuration")
    _config_cache = _get_default_config()
    return _config_cache


def _expand_env_vars(obj: Any) -> Any:
    """Recursively expand environment variables in configuration."""
    if isinstance(obj, dict):
        return {k: _expand_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_expand_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
        # Handle ${VAR:default} syntax
        var_expr = obj[2:-1]  # Remove ${ and }
        if ':' in var_expr:
            var_name, default_value = var_expr.split(':', 1)
            return os.getenv(var_name, default_value)
        else:
            return os.getenv(var_expr, '')
    else:
        return obj


def _get_default_config() -> Dict[str, Any]:
    """Get default configuration with environment variable overrides."""
    return {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "models": {
                "basic": "gpt-3.5-turbo",
                "reasoning": "gpt-4",
                "vision": "gpt-4-vision-preview",
                "fast": "gpt-3.5-turbo",
                "embedding": "text-embedding-ada-002",
                "code": "gpt-4",
                "research": "gpt-4-turbo",
                "analysis": "gpt-4-turbo"
            }
        },
        "anthropic": {
            "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
            "models": {
                "basic": "claude-3-haiku-20240307",
                "reasoning": "claude-3-opus-20240229",
                "vision": "claude-3-opus-20240229",
                "fast": "claude-3-haiku-20240307",
                "code": "claude-3-sonnet-20240229",
                "research": "claude-3-opus-20240229",
                "analysis": "claude-3-sonnet-20240229"
            }
        },
        "qwen": {
            "api_key": os.getenv("QWEN_API_KEY", ""),
            "base_url": os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1"),
            "models": {
                "basic": "qwen-turbo",
                "reasoning": "qwen-max",
                "vision": "qwen-vl-plus",
                "fast": "qwen-turbo",
                "embedding": "text-embedding-v1",
                "code": "qwen-coder-turbo",
                "research": "qwen-max",
                "analysis": "qwen-plus"
            }
        },
        "ollama": {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "models": {
                "basic": "llama2:7b",
                "reasoning": "llama2:13b",
                "vision": "llava:7b",
                "fast": "llama2:7b",
                "embedding": "nomic-embed-text",
                "code": "codellama:7b",
                "research": "llama2:13b",
                "analysis": "llama2:13b"
            }
        },
        "default_providers": ["openai", "anthropic", "qwen", "ollama"]
    }


def _get_env_llm_conf(llm_type: str, provider: str = "openai") -> Dict[str, Any]:
    """
    Get LLM configuration from environment variables.
    Environment variables should follow the format: {PROVIDER}_{LLM_TYPE}__{KEY}
    e.g., OPENAI_BASIC__api_key, ANTHROPIC_REASONING__api_key
    """
    prefix = f"{provider.upper()}_{llm_type.upper()}__"
    conf = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            conf_key = key[len(prefix):].lower()
            conf[conf_key] = value
    
    # Also check for general provider config
    general_prefix = f"{provider.upper()}__"
    for key, value in os.environ.items():
        if key.startswith(general_prefix) and key not in conf:
            conf_key = key[len(general_prefix):].lower()
            conf[conf_key] = value
    
    return conf


def _create_openai_llm(llm_type: LLMType, config: Dict[str, Any]) -> Optional[Any]:
    """Create OpenAI LLM instance."""
    if ChatOpenAI is None:
        raise ImportError("langchain_openai is required for OpenAI models. Install with: pip install langchain-openai")
    
    return ChatOpenAI(**config)


def _create_anthropic_llm(llm_type: LLMType, config: Dict[str, Any]) -> Optional[Any]:
    """Create Anthropic LLM instance."""
    if ChatAnthropic is None:
        raise ImportError("langchain_anthropic is required for Anthropic models. Install with: pip install langchain-anthropic")
    
    return ChatAnthropic(**config)


def _create_google_llm(llm_type: LLMType, config: Dict[str, Any]) -> Optional[Any]:
    """Create Google LLM instance."""
    if ChatGoogleGenerativeAI is None:
        raise ImportError("langchain_google_genai is required for Google models. Install with: pip install langchain-google-genai")
    
    return ChatGoogleGenerativeAI(**config)


def _create_ollama_llm(llm_type: LLMType, config: Dict[str, Any]) -> Optional[Any]:
    """Create Ollama LLM instance."""
    if Ollama is None:
        raise ImportError("langchain_community is required for Ollama models. Install with: pip install langchain-community")
    
    return Ollama(**config)


def _create_qwen_llm(config: Dict[str, Any]) -> Any:
    """Create Qwen LLM instance."""
    try:
        # This is a placeholder - actual implementation would depend on Qwen SDK
        logger.info("Creating Qwen LLM instance")
        # For now, return a mock object
        class MockQwenLLM:
            def __init__(self, config):
                self.config = config
                self.model = config.get("model", "qwen-turbo")
                self.api_key = config.get("api_key")
                self.base_url = config.get("base_url", "https://dashscope.aliyuncs.com/api/v1")
            
            def generate(self, prompt: str, **kwargs) -> str:
                return f"Mock Qwen response for: {prompt[:50]}..."
        
        return MockQwenLLM(config)
    except Exception as e:
        logger.error(f"Failed to create Qwen LLM: {e}")
        raise


def _create_zhipu_llm(config: Dict[str, Any]) -> Any:
    """Create Zhipu AI LLM instance."""
    try:
        logger.info("Creating Zhipu AI LLM instance")
        # This is a placeholder - actual implementation would depend on Zhipu SDK
        class MockZhipuLLM:
            def __init__(self, config):
                self.config = config
                self.model = config.get("model", "glm-3-turbo")
                self.api_key = config.get("api_key")
                self.base_url = config.get("base_url", "https://open.bigmodel.cn/api/paas/v4")
            
            def generate(self, prompt: str, **kwargs) -> str:
                return f"Mock Zhipu response for: {prompt[:50]}..."
        
        return MockZhipuLLM(config)
    except Exception as e:
        logger.error(f"Failed to create Zhipu LLM: {e}")
        raise


def _create_baidu_llm(config: Dict[str, Any]) -> Any:
    """Create Baidu ERNIE LLM instance."""
    try:
        logger.info("Creating Baidu ERNIE LLM instance")
        # This is a placeholder - actual implementation would depend on Baidu SDK
        class MockBaiduLLM:
            def __init__(self, config):
                self.config = config
                self.model = config.get("model", "ernie-bot-turbo")
                self.api_key = config.get("api_key")
                self.secret_key = config.get("secret_key")
                self.base_url = config.get("base_url", "https://aip.baidubce.com")
            
            def generate(self, prompt: str, **kwargs) -> str:
                return f"Mock Baidu ERNIE response for: {prompt[:50]}..."
        
        return MockBaiduLLM(config)
    except Exception as e:
        logger.error(f"Failed to create Baidu LLM: {e}")
        raise


def _create_llm_from_provider(provider: str, llm_type: LLMType, config: Dict[str, Any]) -> Any:
    """Create LLM instance based on provider."""
    creators = {
        "openai": _create_openai_llm,
        "anthropic": _create_anthropic_llm,
        "google": _create_google_llm,
        "ollama": _create_ollama_llm,
        "qwen": _create_qwen_llm,
        "zhipu": _create_zhipu_llm,
        "baidu": _create_baidu_llm,
    }
    
    creator = creators.get(provider.lower())
    if not creator:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
    if provider in ["qwen", "zhipu", "baidu"]:
        return creator(config)
    else:
        return creator(llm_type, config)


def _load_config_file() -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_path = Path(__file__).parent.parent / "config" / "default.yaml"
    if config_path.exists():
        return load_yaml_config(str(config_path))
    return {}


def create_llm_from_config(
    llm_type: LLMType,
    provider: str = "openai",
    config_override: Optional[Dict[str, Any]] = None
) -> Any:
    """
    Create LLM instance from configuration.
    
    Args:
        llm_type: Type of LLM to create
        provider: LLM provider (openai, anthropic, google, ollama, qwen, zhipu, baidu)
        config_override: Override configuration parameters
    
    Returns:
        LLM instance
    """
    # Load base configuration
    file_config = _load_config_file()
    
    # Get default configuration for provider and type
    default_config = DEFAULT_LLM_CONFIGS.get(provider, {}).get(llm_type, {})
    
    # Get configuration from file
    provider_config = file_config.get("llm", {}).get(provider, {})
    type_config = provider_config.get(llm_type.value, {})
    
    # Get configuration from environment variables
    env_config = _get_env_llm_conf(llm_type.value, provider)
    
    # Merge configurations (priority: override > env > file > default)
    merged_config = {}
    merged_config.update(default_config)
    merged_config.update(type_config)
    merged_config.update(env_config)
    if config_override:
        merged_config.update(config_override)
    
    if not merged_config:
        raise ValueError(f"No configuration found for {provider} {llm_type}")
    
    try:
        return _create_llm_from_provider(provider, llm_type, merged_config)
    except Exception as e:
        logger.error(f"Failed to create LLM with provider {provider}: {e}")
        
        # Try fallback providers
        llm_config = load_llm_config()
        fallback_enabled = llm_config.get("fallback", {}).get("enabled", True)
        
        if fallback_enabled:
            fallback_providers = llm_config.get("default_providers", list(AVAILABLE_PROVIDERS.keys()))
            for fallback_provider in fallback_providers:
                if fallback_provider != provider:
                    try:
                        logger.info(f"Trying fallback provider: {fallback_provider}")
                        return create_llm_from_config(llm_type, fallback_provider, config_override)
                    except Exception as fallback_error:
                        logger.warning(f"Fallback provider {fallback_provider} also failed: {fallback_error}")
                        continue
        
        raise RuntimeError(f"All LLM providers failed. Last error: {e}")


@lru_cache(maxsize=32)
def get_llm_by_type(
    llm_type: LLMType,
    provider: Optional[str] = None,
    use_cache: bool = True
) -> Any:
    """
    Get LLM instance by type. Returns cached instance if available.
    
    Args:
        llm_type: Type of LLM to get
        provider: LLM provider (if None, will try to detect from config)
        use_cache: Whether to use cached instances
    
    Returns:
        LLM instance
    """
    # Auto-detect provider if not specified
    if provider is None:
        provider = _detect_default_provider()
    
    cache_key = f"{provider}_{llm_type.value}"
    
    if use_cache and cache_key in _llm_cache:
        return _llm_cache[cache_key]
    
    llm = create_llm_from_config(llm_type, provider)
    
    if use_cache:
        _llm_cache[cache_key] = llm
    
    return llm


def _detect_default_provider() -> str:
    """Detect the default LLM provider from environment or config."""
    # Check environment variable
    default_provider = os.getenv("DEFAULT_LLM_PROVIDER")
    if default_provider:
        return default_provider.lower()
    
    # Check config file
    config = _load_config_file()
    llm_config = config.get("llm", {})
    if "default_provider" in llm_config:
        return llm_config["default_provider"].lower()
    
    # Load LLM config and check provider priority
    llm_config_data = load_llm_config()
    default_providers = llm_config_data.get("default_providers", ["openai", "anthropic", "qwen", "google", "zhipu", "baidu", "ollama"])
    
    # Check providers in order of preference
    for provider in default_providers:
        if provider in llm_config_data and _is_provider_available(provider, llm_config_data[provider]):
            return provider
    
    # Check which provider has API keys configured
    providers = ["openai", "anthropic", "google", "qwen", "zhipu", "baidu"]
    for provider in providers:
        env_vars = [
            f"{provider.upper()}_API_KEY",
            f"{provider.upper()}__api_key",
        ]
        if any(os.getenv(var) for var in env_vars):
            return provider
    
    # Default to OpenAI
    return "openai"


def _is_provider_available(provider: str, provider_config: Dict[str, Any]) -> bool:
    """Check if a provider is available (has required credentials)."""
    if provider == "ollama":
        # Ollama doesn't require API key, just check if base_url is accessible
        return "base_url" in provider_config
    elif provider in ["openai", "anthropic", "google", "qwen", "zhipu"]:
        return "api_key" in provider_config and provider_config["api_key"]
    elif provider == "baidu":
        return ("api_key" in provider_config and provider_config["api_key"] and
                "secret_key" in provider_config and provider_config["secret_key"])
    
    return False


def list_available_providers() -> Dict[str, bool]:
    """List available LLM providers and their installation status."""
    providers = {
        "openai": ChatOpenAI is not None,
        "anthropic": ChatAnthropic is not None,
        "google": ChatGoogleGenerativeAI is not None,
        "ollama": Ollama is not None,
        "qwen": True,  # Mock implementation available
        "zhipu": True,  # Mock implementation available
        "baidu": True,  # Mock implementation available
    }
    return providers


def clear_llm_cache():
    """Clear the LLM instance cache."""
    global _llm_cache
    _llm_cache.clear()
    # Also clear the lru_cache
    get_llm_by_type.cache_clear()


def get_llm_info(llm_type: LLMType, provider: Optional[str] = None) -> Dict[str, Any]:
    """Get information about an LLM configuration."""
    if provider is None:
        provider = _detect_default_provider()
    
    config = _load_config_file()
    default_config = DEFAULT_LLM_CONFIGS.get(provider, {}).get(llm_type, {})
    env_config = _get_env_llm_conf(llm_type.value, provider)
    
    return {
        "provider": provider,
        "type": llm_type.value,
        "default_config": default_config,
        "env_config": {k: "***" if "key" in k.lower() else v for k, v in env_config.items()},
        "available": provider in list_available_providers() and list_available_providers()[provider],
    }