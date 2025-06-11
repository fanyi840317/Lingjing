# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

import abc
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from rag.retriever import Document, MysteryEvent
from config.mystery_config import DataSourceConfig, DataSourceType


class Crawler(abc.ABC):
    """基础爬虫抽象类"""
    
    def __init__(self, config: DataSourceConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers=self.config.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
            
    @abc.abstractmethod
    async def crawl_url(self, url: str) -> Optional[Document]:
        """爬取单个URL"""
        pass
        
    @abc.abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[Document]:
        """搜索相关内容"""
        pass
        
    async def batch_crawl(self, urls: List[str]) -> List[Document]:
        """批量爬取URL"""
        tasks = [self.crawl_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        documents = []
        for result in results:
            if isinstance(result, Document):
                documents.append(result)
            elif isinstance(result, Exception):
                self.logger.error(f"Crawling failed: {result}")
                
        return documents
        
    async def _fetch_html(self, url: str) -> Optional[str]:
        """获取网页HTML内容"""
        try:
            if not self.session:
                raise RuntimeError("Session not initialized. Use async context manager.")
                
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.warning(f"HTTP {response.status} for {url}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return None
            
    def _parse_html(self, html: str, url: str) -> Dict[str, Any]:
        """解析HTML内容"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取基本信息
        title = self._extract_title(soup)
        content = self._extract_content(soup)
        metadata = self._extract_metadata(soup, url)
        
        return {
            'title': title,
            'content': content,
            'metadata': metadata
        }
        
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取标题"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
            
        # 尝试其他标题标签
        for tag in ['h1', 'h2']:
            header = soup.find(tag)
            if header:
                return header.get_text().strip()
                
        return "Untitled"
        
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取正文内容"""
        # 移除脚本和样式标签
        for script in soup(["script", "style"]):
            script.decompose()
            
        # 尝试找到主要内容区域
        content_selectors = [
            'article', '.content', '.post-content', '.entry-content',
            '.article-body', '.story-body', 'main', '.main-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                return content_elem.get_text(separator='\n', strip=True)
                
        # 如果没有找到特定内容区域，返回body内容
        body = soup.find('body')
        if body:
            return body.get_text(separator='\n', strip=True)
            
        return soup.get_text(separator='\n', strip=True)
        
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """提取元数据"""
        metadata = {
            'url': url,
            'crawled_at': datetime.now().isoformat(),
            'source_type': self.config.source_type.value,
            'reliability_score': self.config.reliability_score
        }
        
        # 提取meta标签信息
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                metadata[f'meta_{name}'] = content
                
        # 提取发布日期
        date_selectors = [
            'time[datetime]', '.publish-date', '.date', '.timestamp'
        ]
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text()
                metadata['publication_date'] = date_text
                break
                
        # 提取作者信息
        author_selectors = ['.author', '.byline', '.writer']
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                metadata['author'] = author_elem.get_text().strip()
                break
                
        return metadata
        
    def _create_document(self, parsed_data: Dict[str, Any], doc_id: str) -> Document:
        """创建文档对象"""
        return Document(
            id=doc_id,
            url=parsed_data['metadata']['url'],
            title=parsed_data['title'],
            chunks=[],  # 将在后续处理中分块
            credibility_score=self.config.reliability_score,
            source_type=self.config.source_type.value,
            metadata=parsed_data['metadata']
        )
        
    def _should_crawl_url(self, url: str) -> bool:
        """判断是否应该爬取该URL"""
        parsed = urlparse(url)
        
        # 检查域名是否在允许列表中
        if hasattr(self.config, 'allowed_domains'):
            if parsed.netloc not in self.config.allowed_domains:
                return False
                
        # 检查URL模式
        if hasattr(self.config, 'url_patterns'):
            import re
            for pattern in self.config.url_patterns:
                if re.match(pattern, url):
                    return True
            return False
            
        return True