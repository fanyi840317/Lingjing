# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

import os
import dataclasses
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, Any, List

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_prompt_template(prompt_name: str) -> str:
    """
    Load and return a prompt template using Jinja2.

    Args:
        prompt_name: Name of the prompt template file (without .md extension)

    Returns:
        The template string with proper variable substitution syntax
    """
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render()
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")


def apply_prompt_template(
    prompt_name: str, state: Dict[str, Any], configurable: Dict[str, Any] = None
) -> List[Dict[str, str]]:
    """
    Apply template variables to a prompt template and return formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        state: Current agent state containing variables to substitute
        configurable: Additional configuration variables

    Returns:
        List of messages with the system prompt as the first message
    """
    # Convert state to dict for template rendering
    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state,
    }

    # Add configurable variables
    if configurable:
        if hasattr(configurable, '__dict__'):
            state_vars.update(configurable.__dict__)
        elif isinstance(configurable, dict):
            state_vars.update(configurable)
        else:
            state_vars.update(dataclasses.asdict(configurable))

    try:
        template = env.get_template(f"{prompt_name}.md")
        rendered_content = template.render(**state_vars)
        
        # Return as a list of messages
        return [
            {
                "role": "system",
                "content": rendered_content
            }
        ]
    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {e}")