#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神秘事件研究系统 - 安装配置文件
Mystery Event Research System - Setup Configuration
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# 确保Python版本兼容性
if sys.version_info < (3, 8):
    raise RuntimeError("神秘事件研究系统需要Python 3.8或更高版本")

# 获取项目根目录
HERE = Path(__file__).parent.absolute()

# 读取README文件
def read_readme():
    readme_path = HERE / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "神秘事件研究系统 - 基于AI的综合性神秘现象研究平台"

# 读取requirements文件
def read_requirements(filename="requirements.txt"):
    requirements_path = HERE / filename
    if not requirements_path.exists():
        return []
    
    with open(requirements_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    requirements = []
    for line in lines:
        line = line.strip()
        # 跳过注释和空行
        if line and not line.startswith("#"):
            # 移除行内注释
            if "#" in line:
                line = line.split("#")[0].strip()
            if line:
                requirements.append(line)
    
    return requirements

# 读取版本信息
def get_version():
    version_file = HERE / "mystery_research" / "__version__.py"
    if version_file.exists():
        with open(version_file, "r", encoding="utf-8") as f:
            exec(f.read())
            return locals().get("__version__", "0.1.0")
    return "0.1.0"

# 项目元数据
NAME = "mystery-research-system"
DESCRIPTION = "基于AI的综合性神秘现象研究平台"
LONG_DESCRIPTION = read_readme()
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"
URL = "https://github.com/your-username/mystery-research-system"
AUTHOR = "Mystery Research Team"
AUTHOR_EMAIL = "research@mystery-system.com"
LICENSE = "MIT"
VERSION = get_version()

# 分类信息
CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    "Topic :: Text Processing :: Linguistic",
    "Topic :: Database :: Database Engines/Servers",
    "Natural Language :: Chinese (Simplified)",
    "Natural Language :: English",
    "Natural Language :: Japanese",
    "Natural Language :: Korean",
]

# 关键词
KEYWORDS = [
    "mystery", "research", "ai", "artificial intelligence",
    "ufo", "paranormal", "cryptid", "unexplained phenomena",
    "data mining", "web scraping", "natural language processing",
    "graph database", "correlation analysis", "credibility assessment",
    "langchain", "langgraph", "neo4j", "elasticsearch",
    "academic research", "data analysis", "pattern recognition"
]

# Python版本要求
PYTHON_REQUIRES = ">=3.8"

# 安装依赖
INSTALL_REQUIRES = read_requirements("requirements.txt")

# 可选依赖
EXTRAS_REQUIRE = {
    "dev": [
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-mock>=3.12.0",
        "black>=23.11.0",
        "flake8>=6.1.0",
        "mypy>=1.7.0",
        "isort>=5.12.0",
        "pre-commit>=3.5.0",
    ],
    "docs": [
        "sphinx>=7.2.0",
        "sphinx-rtd-theme>=1.3.0",
        "myst-parser>=2.0.0",
        "sphinx-autodoc-typehints>=1.25.0",
    ],
    "jupyter": [
        "jupyter>=1.0.0",
        "ipykernel>=6.26.0",
        "matplotlib>=3.8.0",
        "seaborn>=0.13.0",
        "plotly>=5.17.0",
    ],
    "full": [
        "neo4j>=5.15.0",
        "elasticsearch>=8.11.0",
        "selenium>=4.15.0",
        "playwright>=1.40.0",
    ],
}

# 命令行入口点
ENTRY_POINTS = {
    "console_scripts": [
        "mystery-research=main:main",
        "mystery-crawler=crawler.main:main",
        "mystery-analyzer=analyzer.main:main",
    ],
}

# 包数据
PACKAGE_DATA = {
    "mystery_research": [
        "config/*.yaml",
        "config/*.json",
        "templates/*.html",
        "templates/*.md",
        "static/css/*.css",
        "static/js/*.js",
        "data/*.json",
        "data/*.csv",
    ],
}

# 数据文件
DATA_FILES = [
    ("config", ["config/default.yaml"]),
    ("templates", ["templates/report_template.md"]),
]

# 项目URL
PROJECT_URLS = {
    "Bug Reports": "https://github.com/your-username/mystery-research-system/issues",
    "Source": "https://github.com/your-username/mystery-research-system",
    "Documentation": "https://mystery-research-system.readthedocs.io/",
    "Funding": "https://github.com/sponsors/your-username",
}

# 设置配置
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    keywords=" ".join(KEYWORDS),
    
    # 包配置
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    package_data=PACKAGE_DATA,
    data_files=DATA_FILES,
    include_package_data=True,
    zip_safe=False,
    
    # 依赖配置
    python_requires=PYTHON_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    
    # 入口点
    entry_points=ENTRY_POINTS,
    
    # 项目URL
    project_urls=PROJECT_URLS,
    
    # 其他配置
    platforms=["any"],
    test_suite="tests",
)

# 安装后的提示信息
print("""
🔍 神秘事件研究系统安装完成！

快速开始：
1. 配置环境变量：cp .env.example .env
2. 编辑 .env 文件，设置API密钥
3. 运行交互模式：mystery-research --interactive
4. 查看帮助信息：mystery-research --help

更多信息请参考 README.md 文件。

⚠️  免责声明：
本系统仅用于学术研究和教育目的。
请保持科学和理性的态度对待研究结果。
""")