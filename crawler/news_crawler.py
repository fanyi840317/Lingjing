# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import quote, urljoin

from crawler.crawler import Crawler
from rag.retriever import Document, Chunk
from config.mystery_config import DataSourceConfig


class NewsCrawler(Crawler):
    """新闻媒体爬虫"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.news_indicators = [
            "breaking news", "reported", "according to", "sources say",
            "investigation reveals", "witnesses report", "officials confirm"
        ]
        
    async def crawl_url(self, url: str) -> Optional[Document]:
        """爬取新闻页面"""
        html = await self._fetch_html(url)
        if not html:
            return None
            
        parsed_data = self._parse_news_html(html, url)
        if not parsed_data:
            return None
            
        doc_id = hashlib.md5(url.encode()).hexdigest()
        document = self._create_news_document(parsed_data, doc_id)
        
        return document
        
    async def search(self, query: str, limit: int = 10) -> List[Document]:
        """搜索新闻报道"""
        documents = []
        
        # 构建新闻搜索查询
        news_query = self._build_news_query(query)
        
        # 生成搜索URL
        search_urls = self._generate_news_search_urls(news_query, limit)
        
        for url in search_urls:
            doc = await self.crawl_url(url)
            if doc:
                documents.append(doc)
                
        return documents[:limit]
        
    def _parse_news_html(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """解析新闻HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取新闻标题
        title = self._extract_news_title(soup)
        if not title:
            return None
            
        # 提取新闻内容
        content = self._extract_news_content(soup)
        
        # 提取发布日期
        publication_date = self._extract_publication_date(soup)
        
        # 提取作者信息
        author = self._extract_author(soup)
        
        # 提取新闻来源
        source = self._extract_news_source(soup, url)
        
        # 提取摘要/导语
        summary = self._extract_news_summary(soup)
        
        # 提取标签/分类
        tags = self._extract_news_tags(soup)
        
        # 计算新闻可信度
        credibility_score = self._calculate_news_credibility(soup, source, author)
        
        metadata = {
            'url': url,
            'crawled_at': datetime.now().isoformat(),
            'source_type': 'news',
            'reliability_score': credibility_score,
            'publication_date': publication_date.isoformat() if publication_date else None,
            'author': author,
            'news_source': source,
            'summary': summary,
            'tags': tags,
            'credibility_score': credibility_score
        }
        
        return {
            'title': title,
            'content': content,
            'metadata': metadata
        }
        
    def _extract_news_title(self, soup) -> Optional[str]:
        """提取新闻标题"""
        # 新闻网站常见的标题选择器
        title_selectors = [
            'h1.headline',
            'h1.article-title',
            'h1.entry-title',
            '.article-headline',
            '.news-title',
            'h1',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if len(title) > 10:  # 确保标题有意义
                    return title
                    
        return None
        
    def _extract_news_content(self, soup) -> str:
        """提取新闻正文内容"""
        # 移除不需要的元素
        for elem in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            elem.decompose()
            
        # 新闻内容选择器
        content_selectors = [
            '.article-body',
            '.entry-content',
            '.post-content',
            '.news-content',
            '.story-body',
            '.article-content',
            '.content',
            'main',
            '.main-content'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 移除广告和相关文章
                for ad in content_elem.select('.ad, .advertisement, .related, .sidebar'):
                    ad.decompose()
                return content_elem.get_text(separator='\n', strip=True)
                
        # 如果没有找到特定内容区域，返回body内容
        body = soup.find('body')
        if body:
            return body.get_text(separator='\n', strip=True)
            
        return soup.get_text(separator='\n', strip=True)
        
    def _extract_publication_date(self, soup) -> Optional[datetime]:
        """提取发布日期"""
        date_selectors = [
            'time[datetime]',
            '.publish-date',
            '.publication-date',
            '.article-date',
            '.news-date',
            '.date',
            '.timestamp'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text()
                parsed_date = self._parse_date(date_text)
                if parsed_date:
                    return parsed_date
                    
        # 尝试从meta标签中提取
        meta_date = soup.find('meta', {'property': 'article:published_time'})
        if meta_date:
            date_text = meta_date.get('content')
            parsed_date = self._parse_date(date_text)
            if parsed_date:
                return parsed_date
                
        return None
        
    def _extract_author(self, soup) -> Optional[str]:
        """提取作者信息"""
        author_selectors = [
            '.author',
            '.byline',
            '.article-author',
            '.news-author',
            '.writer',
            '.journalist'
        ]
        
        for selector in author_selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                author_text = author_elem.get_text().strip()
                # 清理作者信息
                author_text = re.sub(r'^(by|author:?)\s*', '', author_text, flags=re.IGNORECASE)
                if author_text:
                    return author_text
                    
        # 尝试从meta标签中提取
        meta_author = soup.find('meta', {'name': 'author'})
        if meta_author:
            return meta_author.get('content')
            
        return None
        
    def _extract_news_source(self, soup, url: str) -> str:
        """提取新闻来源"""
        # 尝试从网站名称提取
        site_name_selectors = [
            '.site-name',
            '.logo',
            '.brand',
            '.masthead'
        ]
        
        for selector in site_name_selectors:
            site_elem = soup.select_one(selector)
            if site_elem:
                site_name = site_elem.get_text().strip()
                if site_name:
                    return site_name
                    
        # 尝试从meta标签提取
        meta_site = soup.find('meta', {'property': 'og:site_name'})
        if meta_site:
            return meta_site.get('content')
            
        # 从URL提取域名
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # 清理域名
        domain = re.sub(r'^www\.', '', domain)
        return domain
        
    def _extract_news_summary(self, soup) -> str:
        """提取新闻摘要/导语"""
        summary_selectors = [
            '.summary',
            '.excerpt',
            '.lead',
            '.intro',
            '.article-summary',
            '.news-summary'
        ]
        
        for selector in summary_selectors:
            summary_elem = soup.select_one(selector)
            if summary_elem:
                return summary_elem.get_text().strip()
                
        # 尝试从meta描述提取
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc:
            return meta_desc.get('content')
            
        return ""
        
    def _extract_news_tags(self, soup) -> List[str]:
        """提取新闻标签/分类"""
        tags = []
        
        tag_selectors = [
            '.tags',
            '.categories',
            '.keywords',
            '.article-tags',
            '.news-tags'
        ]
        
        for selector in tag_selectors:
            tag_elems = soup.select(f"{selector} a, {selector} span")
            for elem in tag_elems:
                tag_text = elem.get_text().strip()
                if tag_text and tag_text not in tags:
                    tags.append(tag_text)
                    
        # 尝试从meta关键词提取
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content').split(',')
            for keyword in keywords:
                keyword = keyword.strip()
                if keyword and keyword not in tags:
                    tags.append(keyword)
                    
        return tags
        
    def _calculate_news_credibility(self, soup, source: str, author: Optional[str]) -> float:
        """计算新闻可信度分数"""
        score = 0.6  # 新闻基础分数
        
        # 知名新闻源加分
        reputable_sources = [
            'reuters', 'ap', 'bbc', 'cnn', 'nytimes', 'washingtonpost',
            'guardian', 'npr', 'pbs', 'abc', 'cbs', 'nbc'
        ]
        if any(source_name in source.lower() for source_name in reputable_sources):
            score += 0.2
            
        # 有作者署名加分
        if author:
            score += 0.1
            
        # 检查是否有引用和来源
        text = soup.get_text().lower()
        citation_indicators = [
            'according to', 'sources say', 'officials said',
            'spokesperson', 'statement', 'confirmed'
        ]
        if any(indicator in text for indicator in citation_indicators):
            score += 0.1
            
        # 检查是否有多个来源
        if text.count('source') > 1 or text.count('official') > 1:
            score += 0.05
            
        # 确保分数在0-1范围内
        return min(max(score, 0.0), 1.0)
        
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """解析日期字符串"""
        import dateutil.parser
        try:
            return dateutil.parser.parse(date_text)
        except:
            return None
            
    def _create_news_document(self, parsed_data: Dict[str, Any], doc_id: str) -> Document:
        """创建新闻文档对象"""
        # 创建文档块
        chunks = []
        
        content = parsed_data['content']
        if content:
            # 按段落分块
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) > 50:  # 只保留有意义的段落
                    chunks.append(Chunk(
                        content=paragraph,
                        similarity=0.7,
                        metadata={'type': 'content', 'paragraph_index': i}
                    ))
                    
        # 如果有摘要，作为单独的块
        summary = parsed_data['metadata'].get('summary')
        if summary:
            chunks.insert(0, Chunk(
                content=summary,
                similarity=0.9,
                metadata={'type': 'summary'}
            ))
            
        return Document(
            id=doc_id,
            url=parsed_data['metadata']['url'],
            title=parsed_data['title'],
            chunks=chunks,
            credibility_score=parsed_data['metadata']['credibility_score'],
            source_type='news',
            publication_date=self._parse_date(parsed_data['metadata']['publication_date']) if parsed_data['metadata']['publication_date'] else None,
            author=parsed_data['metadata']['author'],
            metadata=parsed_data['metadata']
        )
        
    def _build_news_query(self, query: str) -> str:
        """构建新闻搜索查询"""
        # 添加新闻相关的关键词
        news_terms = ["news", "report", "breaking"]
        
        # 如果查询中没有新闻术语，添加一些
        if not any(term in query.lower() for term in news_terms):
            query += " news report"
            
        return query
        
    def _generate_news_search_urls(self, query: str, limit: int) -> List[str]:
        """生成新闻搜索URL列表（模拟）"""
        # 这里应该根据具体的新闻API生成真实的搜索URL
        news_sites = [
            f"https://news.google.com/search?q={quote(query)}",
            f"https://www.reuters.com/search/news?blob={quote(query)}",
            f"https://www.bbc.com/search?q={quote(query)}",
            f"https://edition.cnn.com/search?q={quote(query)}"
        ]
        
        return news_sites[:limit]