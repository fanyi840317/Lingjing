# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

import json
import re
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def repair_json_output(json_str: str) -> Optional[Dict[str, Any]]:
    """修复可能损坏的JSON字符串
    
    Args:
        json_str: 可能损坏的JSON字符串
        
    Returns:
        修复后的JSON对象，如果无法修复则返回None
    """
    if not json_str or not isinstance(json_str, str):
        logger.warning("Invalid input for JSON repair")
        return None
    
    # 尝试直接解析
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # 清理常见问题
    cleaned = json_str.strip()
    
    # 移除可能的markdown代码块标记
    if cleaned.startswith('```json'):
        cleaned = cleaned[7:]
    if cleaned.startswith('```'):
        cleaned = cleaned[3:]
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3]
    
    cleaned = cleaned.strip()
    
    # 尝试修复常见的JSON问题
    repairs = [
        # 修复尾随逗号
        lambda s: re.sub(r',\s*}', '}', s),
        lambda s: re.sub(r',\s*]', ']', s),
        
        # 修复单引号
        lambda s: re.sub(r"'([^']*)':", r'"\1":', s),
        lambda s: re.sub(r":\s*'([^']*)'", r': "\1"', s),
        
        # 修复未引用的键
        lambda s: re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', s),
        
        # 修复换行符
        lambda s: s.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t'),
        
        # 修复未转义的引号
        lambda s: re.sub(r'"([^"]*[^\\])"([^":,}\]\s])', r'"\1\\"\2', s),
    ]
    
    for repair_func in repairs:
        try:
            repaired = repair_func(cleaned)
            result = json.loads(repaired)
            logger.debug(f"JSON repaired successfully with repair function: {repair_func.__name__}")
            return result
        except (json.JSONDecodeError, Exception) as e:
            logger.debug(f"Repair attempt failed: {e}")
            continue
    
    # 尝试提取JSON对象
    json_match = re.search(r'{.*}', cleaned, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    # 尝试提取JSON数组
    json_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
    
    logger.error(f"Unable to repair JSON: {json_str[:100]}...")
    return None


def validate_json_schema(data: Dict[str, Any], required_fields: list) -> bool:
    """验证JSON数据是否包含必需字段
    
    Args:
        data: JSON数据
        required_fields: 必需字段列表
        
    Returns:
        是否包含所有必需字段
    """
    if not isinstance(data, dict):
        return False
    
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return False
    
    return True


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """安全地解析JSON字符串
    
    Args:
        json_str: JSON字符串
        default: 解析失败时的默认值
        
    Returns:
        解析结果或默认值
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"JSON parsing failed: {e}")
        return default


def safe_json_dumps(data: Any, **kwargs) -> str:
    """安全地序列化为JSON字符串
    
    Args:
        data: 要序列化的数据
        **kwargs: json.dumps的额外参数
        
    Returns:
        JSON字符串
    """
    try:
        return json.dumps(data, ensure_ascii=False, **kwargs)
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization failed: {e}")
        return json.dumps({"error": f"Serialization failed: {str(e)}"}, ensure_ascii=False)