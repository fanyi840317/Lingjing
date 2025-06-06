# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

from .crawler import Crawler
from .academic_crawler import AcademicCrawler
from .mystery_crawler import MysteryCrawler
from .news_crawler import NewsCrawler
from .forum_crawler import ForumCrawler
from .documentary_crawler import DocumentaryCrawler


def build_crawler(crawler_type: str = "mystery"):
    """Build a crawler based on the specified type."""
    crawler_map = {
        "mystery": MysteryCrawler,
        "academic": AcademicCrawler,
        "news": NewsCrawler,
        "forum": ForumCrawler,
        "documentary": DocumentaryCrawler,
    }
    
    crawler_class = crawler_map.get(crawler_type.lower(), MysteryCrawler)
    return crawler_class()


def build_specialized_crawlers():
    """Build all specialized crawlers for mystery research."""
    return {
        "mystery": MysteryCrawler(),
        "academic": AcademicCrawler(),
        "news": NewsCrawler(),
        "forum": ForumCrawler(),
        "documentary": DocumentaryCrawler(),
    }


__all__ = [
    "Crawler",
    "AcademicCrawler", 
    "MysteryCrawler",
    "NewsCrawler",
    "ForumCrawler",
    "DocumentaryCrawler",
    "build_crawler",
    "build_specialized_crawlers",
]