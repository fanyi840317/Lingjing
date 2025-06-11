# -*- coding: utf-8 -*-
# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

import json
import logging
import time
import functools
from typing import Any, Callable, Dict, Optional, Type
from datetime import datetime

logger = logging.getLogger(__name__)


def log_io(func: Callable) -> Callable:
    """装饰器：记录工具的输入输出和执行时间
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        function_name = func.__name__
        
        # 记录输入
        logger.info(f"[{function_name}] Starting execution")
        logger.debug(f"[{function_name}] Input args: {args}")
        logger.debug(f"[{function_name}] Input kwargs: {kwargs}")
        
        try:
            # 执行函数
            result = func(*args, **kwargs)
            
            # 计算执行时间
            execution_time = time.time() - start_time
            
            # 记录输出
            logger.info(f"[{function_name}] Completed successfully in {execution_time:.3f}s")
            
            # 如果结果是JSON字符串，尝试解析并记录关键信息
            try:
                if isinstance(result, str):
                    result_data = json.loads(result)
                    if "error" in result_data:
                        logger.warning(f"[{function_name}] Function returned error: {result_data['error']}")
                    else:
                        logger.debug(f"[{function_name}] Result keys: {list(result_data.keys()) if isinstance(result_data, dict) else 'non-dict result'}")
            except (json.JSONDecodeError, TypeError):
                logger.debug(f"[{function_name}] Result type: {type(result).__name__}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"[{function_name}] Failed after {execution_time:.3f}s with error: {repr(e)}")
            
            # 返回错误结果
            error_result = {
                "error": str(e),
                "function": function_name,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            }
            return json.dumps(error_result, ensure_ascii=False)
    
    return wrapper


def create_logged_tool(tool_class: Type) -> Callable:
    """创建带有日志记录功能的工具实例工厂函数
    
    Args:
        tool_class: 要包装的工具类
        
    Returns:
        工具实例工厂函数
    """
    def create_instance(*args, **kwargs):
        """创建带有日志记录的工具实例"""
        # 创建原始工具实例
        instance = tool_class(*args, **kwargs)
        
        # 包装_run方法
        original_run = instance._run
        instance._run = log_io(original_run)
        
        # 包装_arun方法（如果存在）
        if hasattr(instance, '_arun'):
            original_arun = instance._arun
            async def logged_arun(*args, **kwargs):
                return await log_io(original_arun)(*args, **kwargs)
            instance._arun = logged_arun
        
        return instance
    
    return create_instance


def performance_monitor(threshold_seconds: float = 1.0):
    """装饰器：监控函数性能，当执行时间超过阈值时发出警告
    
    Args:
        threshold_seconds: 性能警告阈值（秒）
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            function_name = func.__name__
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold_seconds:
                    logger.warning(
                        f"[PERFORMANCE] {function_name} took {execution_time:.3f}s "
                        f"(threshold: {threshold_seconds}s)"
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"[PERFORMANCE] {function_name} failed after {execution_time:.3f}s: {repr(e)}"
                )
                raise
        
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay_seconds: float = 1.0, backoff_factor: float = 2.0):
    """装饰器：在失败时重试函数执行
    
    Args:
        max_retries: 最大重试次数
        delay_seconds: 初始延迟时间（秒）
        backoff_factor: 退避因子
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            function_name = func.__name__
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        delay = delay_seconds * (backoff_factor ** (attempt - 1))
                        logger.info(f"[RETRY] {function_name} attempt {attempt + 1}/{max_retries + 1} after {delay:.1f}s delay")
                        time.sleep(delay)
                    
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"[RETRY] {function_name} attempt {attempt + 1} failed: {repr(e)}")
                    else:
                        logger.error(f"[RETRY] {function_name} all {max_retries + 1} attempts failed")
            
            # 所有重试都失败了，抛出最后一个异常
            raise last_exception
        
        return wrapper
    return decorator


def validate_input(validation_func: Callable[[Any], bool], error_message: str = "Invalid input"):
    """装饰器：验证函数输入
    
    Args:
        validation_func: 验证函数，返回True表示验证通过
        error_message: 验证失败时的错误消息
        
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            function_name = func.__name__
            
            try:
                # 验证输入
                if not validation_func(*args, **kwargs):
                    logger.error(f"[VALIDATION] {function_name} input validation failed: {error_message}")
                    error_result = {
                        "error": error_message,
                        "function": function_name,
                        "validation_failed": True,
                        "timestamp": datetime.now().isoformat()
                    }
                    return json.dumps(error_result, ensure_ascii=False)
                
                return func(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"[VALIDATION] {function_name} validation error: {repr(e)}")
                error_result = {
                    "error": f"Validation error: {str(e)}",
                    "function": function_name,
                    "validation_error": True,
                    "timestamp": datetime.now().isoformat()
                }
                return json.dumps(error_result, ensure_ascii=False)
        
        return wrapper
    return decorator


def cache_result(cache_duration_seconds: int = 300):
    """装饰器：缓存函数结果
    
    Args:
        cache_duration_seconds: 缓存持续时间（秒）
        
    Returns:
        装饰器函数
    """
    cache = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            function_name = func.__name__
            
            # 创建缓存键
            cache_key = f"{function_name}_{hash(str(args) + str(sorted(kwargs.items())))}"
            current_time = time.time()
            
            # 检查缓存
            if cache_key in cache:
                cached_result, cached_time = cache[cache_key]
                if current_time - cached_time < cache_duration_seconds:
                    logger.debug(f"[CACHE] {function_name} returning cached result")
                    return cached_result
                else:
                    # 缓存过期，删除
                    del cache[cache_key]
                    logger.debug(f"[CACHE] {function_name} cache expired")
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache[cache_key] = (result, current_time)
            logger.debug(f"[CACHE] {function_name} result cached")
            
            return result
        
        return wrapper
    return decorator


def rate_limit(calls_per_minute: int = 60):
    """装饰器：限制函数调用频率
    
    Args:
        calls_per_minute: 每分钟允许的调用次数
        
    Returns:
        装饰器函数
    """
    call_times = []
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            function_name = func.__name__
            current_time = time.time()
            
            # 清理过期的调用记录（超过1分钟）
            call_times[:] = [t for t in call_times if current_time - t < 60]
            
            # 检查是否超过限制
            if len(call_times) >= calls_per_minute:
                logger.warning(f"[RATE_LIMIT] {function_name} rate limit exceeded ({calls_per_minute} calls/min)")
                error_result = {
                    "error": f"Rate limit exceeded: {calls_per_minute} calls per minute",
                    "function": function_name,
                    "rate_limited": True,
                    "timestamp": datetime.now().isoformat()
                }
                return json.dumps(error_result, ensure_ascii=False)
            
            # 记录调用时间
            call_times.append(current_time)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def sanitize_output(sanitize_func: Optional[Callable[[Any], Any]] = None):
    """装饰器：清理函数输出
    
    Args:
        sanitize_func: 清理函数，如果为None则使用默认清理
        
    Returns:
        装饰器函数
    """
    def default_sanitize(result: Any) -> Any:
        """默认清理函数"""
        if isinstance(result, str):
            try:
                # 尝试解析JSON并移除敏感信息
                data = json.loads(result)
                if isinstance(data, dict):
                    # 移除可能的敏感字段
                    sensitive_keys = ['password', 'token', 'key', 'secret', 'api_key']
                    for key in sensitive_keys:
                        if key in data:
                            data[key] = "[REDACTED]"
                
                return json.dumps(data, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                return result
        
        return result
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            
            # 应用清理函数
            sanitizer = sanitize_func or default_sanitize
            sanitized_result = sanitizer(result)
            
            return sanitized_result
        
        return wrapper
    return decorator


def measure_memory_usage(func: Callable) -> Callable:
    """装饰器：测量函数内存使用情况
    
    Args:
        func: 要装饰的函数
        
    Returns:
        装饰后的函数
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        function_name = func.__name__
        
        try:
            import psutil
            import os
            
            # 获取当前进程
            process = psutil.Process(os.getpid())
            
            # 记录执行前的内存使用
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 记录执行后的内存使用
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_diff = memory_after - memory_before
            
            if abs(memory_diff) > 10:  # 如果内存变化超过10MB则记录
                logger.info(
                    f"[MEMORY] {function_name} memory usage: "
                    f"before={memory_before:.1f}MB, after={memory_after:.1f}MB, "
                    f"diff={memory_diff:+.1f}MB"
                )
            
            return result
            
        except ImportError:
            # psutil不可用，直接执行函数
            logger.debug(f"[MEMORY] psutil not available for {function_name}")
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"[MEMORY] Failed to measure memory for {function_name}: {repr(e)}")
            return func(*args, **kwargs)
    
    return wrapper


# 组合装饰器
def mystery_tool(max_retries: int = 2, cache_duration: int = 300, rate_limit_per_minute: int = 30):
    """神秘事件工具的组合装饰器
    
    Args:
        max_retries: 最大重试次数
        cache_duration: 缓存持续时间（秒）
        rate_limit_per_minute: 每分钟调用限制
        
    Returns:
        组合装饰器
    """
    def decorator(func: Callable) -> Callable:
        # 应用多个装饰器
        decorated_func = func
        decorated_func = log_io(decorated_func)
        decorated_func = performance_monitor(threshold_seconds=2.0)(decorated_func)
        decorated_func = retry_on_failure(max_retries=max_retries)(decorated_func)
        decorated_func = cache_result(cache_duration_seconds=cache_duration)(decorated_func)
        decorated_func = rate_limit(calls_per_minute=rate_limit_per_minute)(decorated_func)
        decorated_func = sanitize_output()(decorated_func)
        decorated_func = measure_memory_usage(decorated_func)
        
        return decorated_func
    
    return decorator