#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

"""
Python REPL tool for mysterious event research.
Provides code execution capabilities for data analysis and processing.
"""

import logging
import sys
import io
import traceback
from typing import Dict, Any, Optional
from contextlib import redirect_stdout, redirect_stderr
from langchain_core.tools import tool

from .decorators import mystery_tool

logger = logging.getLogger(__name__)


class SafePythonREPL:
    """Safe Python REPL for mystery research data analysis."""
    
    def __init__(self):
        self.globals = {
            '__builtins__': {
                # Safe built-ins only
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sorted': sorted,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'print': print,
            }
        }
        
        # Add safe modules for data analysis
        try:
            import json
            import math
            import datetime
            import statistics
            
            self.globals.update({
                'json': json,
                'math': math,
                'datetime': datetime,
                'statistics': statistics,
            })
        except ImportError as e:
            logger.warning(f"Some modules not available: {e}")
    
    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute Python code safely.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Dict containing execution results
        """
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        result = {
            "code": code,
            "success": False,
            "output": "",
            "error": "",
            "result": None,
            "execution_time": 0
        }
        
        try:
            import time
            start_time = time.time()
            
            # Redirect stdout and stderr
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Compile and execute the code
                compiled_code = compile(code, '<string>', 'exec')
                exec(compiled_code, self.globals)
            
            result["success"] = True
            result["output"] = stdout_capture.getvalue()
            result["execution_time"] = time.time() - start_time
            
        except SyntaxError as e:
            result["error"] = f"Syntax Error: {str(e)}"
            result["error_type"] = "SyntaxError"
        except NameError as e:
            result["error"] = f"Name Error: {str(e)}"
            result["error_type"] = "NameError"
        except Exception as e:
            result["error"] = f"Runtime Error: {str(e)}"
            result["error_type"] = type(e).__name__
            result["traceback"] = traceback.format_exc()
        
        # Capture any stderr output
        stderr_output = stderr_capture.getvalue()
        if stderr_output:
            result["error"] += f"\nStderr: {stderr_output}"
        
        return result
    
    def evaluate_expression(self, expression: str) -> Dict[str, Any]:
        """Evaluate a Python expression and return the result.
        
        Args:
            expression: Python expression to evaluate
            
        Returns:
            Dict containing evaluation results
        """
        result = {
            "expression": expression,
            "success": False,
            "result": None,
            "error": "",
            "type": None
        }
        
        try:
            # Evaluate the expression
            eval_result = eval(expression, self.globals)
            result["success"] = True
            result["result"] = eval_result
            result["type"] = type(eval_result).__name__
            
        except Exception as e:
            result["error"] = f"Evaluation Error: {str(e)}"
            result["error_type"] = type(e).__name__
        
        return result


# Global REPL instance
_repl = SafePythonREPL()


@mystery_tool
@tool
def python_repl_tool(
    code: str,
    execution_type: str = "execute",
    timeout: int = 30
) -> Dict[str, Any]:
    """Execute Python code for mystery research data analysis.
    
    Args:
        code: Python code to execute
        execution_type: Type of execution (execute, evaluate)
        timeout: Execution timeout in seconds
        
    Returns:
        Dict containing execution results
    """
    try:
        if execution_type == "evaluate":
            result = _repl.evaluate_expression(code)
        else:
            result = _repl.execute(code, timeout)
        
        logger.info(f"Python REPL execution completed: {result['success']}")
        return result
        
    except Exception as e:
        logger.error(f"Error in python_repl_tool: {str(e)}")
        return {
            "code": code,
            "success": False,
            "error": str(e),
            "output": "",
            "result": None
        }


@mystery_tool
@tool
def data_analysis_tool(
    data: Dict[str, Any],
    analysis_type: str = "basic_stats"
) -> Dict[str, Any]:
    """Perform data analysis on mystery research data.
    
    Args:
        data: Data to analyze
        analysis_type: Type of analysis (basic_stats, correlation, distribution)
        
    Returns:
        Dict containing analysis results
    """
    try:
        if analysis_type == "basic_stats":
            code = f"""
import json
import statistics

data = {json.dumps(data)}
result = {{}}

# Basic statistics
if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
    result['count'] = len(data)
    result['mean'] = statistics.mean(data)
    result['median'] = statistics.median(data)
    result['std_dev'] = statistics.stdev(data) if len(data) > 1 else 0
    result['min'] = min(data)
    result['max'] = max(data)
elif isinstance(data, dict):
    result['keys'] = list(data.keys())
    result['key_count'] = len(data)
    numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
    if numeric_values:
        result['numeric_count'] = len(numeric_values)
        result['numeric_mean'] = statistics.mean(numeric_values)
else:
    result['type'] = type(data).__name__
    result['length'] = len(data) if hasattr(data, '__len__') else None

print(json.dumps(result, indent=2))
"""
        elif analysis_type == "correlation":
            code = f"""
import json
import math

data = {json.dumps(data)}
result = {{}}

# Simple correlation analysis
if isinstance(data, dict) and len(data) >= 2:
    keys = list(data.keys())
    values = list(data.values())
    
    # Check if values are numeric
    if all(isinstance(v, (int, float)) for v in values):
        # Calculate basic correlation metrics
        mean_val = sum(values) / len(values)
        variance = sum((v - mean_val) ** 2 for v in values) / len(values)
        result['mean'] = mean_val
        result['variance'] = variance
        result['std_dev'] = math.sqrt(variance) if variance > 0 else 0
        
        # Find outliers (simple method)
        outliers = [k for k, v in data.items() if abs(v - mean_val) > 2 * math.sqrt(variance)]
        result['outliers'] = outliers

print(json.dumps(result, indent=2))
"""
        else:
            code = f"""
import json

data = {json.dumps(data)}
result = {{
    'data_type': type(data).__name__,
    'analysis_type': '{analysis_type}',
    'message': 'Analysis type not implemented'
}}

print(json.dumps(result, indent=2))
"""
        
        execution_result = _repl.execute(code)
        
        if execution_result["success"]:
            try:
                import json
                analysis_result = json.loads(execution_result["output"])
                return {
                    "success": True,
                    "analysis_type": analysis_type,
                    "result": analysis_result
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "analysis_type": analysis_type,
                    "result": {"output": execution_result["output"]}
                }
        else:
            return {
                "success": False,
                "analysis_type": analysis_type,
                "error": execution_result["error"]
            }
            
    except Exception as e:
        logger.error(f"Error in data_analysis_tool: {str(e)}")
        return {
            "success": False,
            "analysis_type": analysis_type,
            "error": str(e)
        }


@mystery_tool
@tool
def mystery_data_processor(
    events: list,
    processing_type: str = "summary"
) -> Dict[str, Any]:
    """Process mystery event data using Python.
    
    Args:
        events: List of mystery events to process
        processing_type: Type of processing (summary, filter, transform)
        
    Returns:
        Dict containing processed data
    """
    try:
        if processing_type == "summary":
            code = f"""
import json
from datetime import datetime

events = {json.dumps(events)}
result = {{}}

# Generate summary statistics
result['total_events'] = len(events)
result['event_types'] = {{}}
result['locations'] = {{}}
result['date_range'] = {{}}

for event in events:
    # Count event types
    event_type = event.get('type', 'unknown')
    result['event_types'][event_type] = result['event_types'].get(event_type, 0) + 1
    
    # Count locations
    location = event.get('location', 'unknown')
    result['locations'][location] = result['locations'].get(location, 0) + 1

# Find most common type and location
if result['event_types']:
    result['most_common_type'] = max(result['event_types'], key=result['event_types'].get)
if result['locations']:
    result['most_common_location'] = max(result['locations'], key=result['locations'].get)

print(json.dumps(result, indent=2))
"""
        else:
            code = f"""
import json

events = {json.dumps(events)}
result = {{
    'processing_type': '{processing_type}',
    'total_events': len(events),
    'message': 'Processing type not implemented'
}}

print(json.dumps(result, indent=2))
"""
        
        execution_result = _repl.execute(code)
        
        if execution_result["success"]:
            try:
                import json
                processed_result = json.loads(execution_result["output"])
                return {
                    "success": True,
                    "processing_type": processing_type,
                    "result": processed_result
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "processing_type": processing_type,
                    "result": {"output": execution_result["output"]}
                }
        else:
            return {
                "success": False,
                "processing_type": processing_type,
                "error": execution_result["error"]
            }
            
    except Exception as e:
        logger.error(f"Error in mystery_data_processor: {str(e)}")
        return {
            "success": False,
            "processing_type": processing_type,
            "error": str(e)
        }