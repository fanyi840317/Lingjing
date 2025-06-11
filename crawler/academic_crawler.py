# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import quote, urljoin

from crawler.crawler import Crawler
from rag.retriever import Document, Chunk
from config.mystery_config import DataSourceConfig, DataSourceType


class AcademicCrawler(Crawler):
    """学术数据库爬虫"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.academic_keywords = [
            "anomalous phenomena", "unexplained events", "atmospheric anomalies",
            "geophysical anomalies", "electromagnetic anomalies", "plasma phenomena",
            "ball lightning", "earthquake lights", "atmospheric optics",
            "meteorological phenomena", "ionospheric disturbances"
        ]
        
    async def crawl_url(self, url: str) -> Optional[Document]:
        """爬取学术论文页面"""
        html = await self._fetch_html(url)
        if not html:
            return None
            
        parsed_data = self._parse_academic_html(html, url)
        if not parsed_data:
            return None
            
        doc_id = hashlib.md5(url.encode()).hexdigest()
        document = self._create_academic_document(parsed_data, doc_id)
        
        return document
        
    async def search(self, query: str, limit: int = 10) -> List[Document]:
        """搜索学术论文"""
        documents = []
        
        # 构建学术搜索查询
        academic_query = self._build_academic_query(query)
        
        # 模拟不同学术数据库的搜索
        search_urls = self._generate_search_urls(academic_query, limit)
        
        for url in search_urls:
            doc = await self.crawl_url(url)
            if doc:
                documents.append(doc)
                
        return documents[:limit]
        
    def _parse_academic_html(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """解析学术论文HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取论文标题
        title = self._extract_academic_title(soup)
        if not title:
            return None
            
        # 提取摘要
        abstract = self._extract_abstract(soup)
        
        # 提取作者信息
        authors = self._extract_authors(soup)
        
        # 提取期刊信息
        journal_info = self._extract_journal_info(soup)
        
        # 提取DOI
        doi = self._extract_doi(soup)
        
        # 提取关键词
        keywords = self._extract_keywords(soup)
        
        # 提取正文内容
        content = self._extract_academic_content(soup)
        
        # 提取引用信息
        citations = self._extract_citations(soup)
        
        metadata = {
            'url': url,
            'crawled_at': datetime.now().isoformat(),
            'source_type': 'academic',
            'reliability_score': 0.9,  # 学术论文可靠性较高
            'authors': authors,
            'journal': journal_info.get('name'),
            'publication_year': journal_info.get('year'),
            'volume': journal_info.get('volume'),
            'issue': journal_info.get('issue'),
            'pages': journal_info.get('pages'),
            'doi': doi,
            'keywords': keywords,
            'citations_count': len(citations),
            'abstract': abstract
        }
        
        return {
            'title': title,
            'content': content,
            'abstract': abstract,
            'metadata': metadata
        }
        
    def _extract_academic_title(self, soup) -> Optional[str]:
        """提取学术论文标题"""
        # 常见的学术论文标题选择器
        title_selectors = [
            'h1.article-title',
            '.article-title',
            'h1.title',
            '.paper-title',
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
        
    def _extract_abstract(self, soup) -> str:
        """提取摘要"""
        abstract_selectors = [
            '.abstract',
            '#abstract',
            '.summary',
            '[data-testid="abstract"]',
            '.article-abstract'
        ]
        
        for selector in abstract_selectors:
            abstract_elem = soup.select_one(selector)
            if abstract_elem:
                return abstract_elem.get_text().strip()
                
        return ""
        
    def _extract_authors(self, soup) -> List[str]:
        """提取作者信息"""
        authors = []
        
        author_selectors = [
            '.author',
            '.authors',
            '.author-name',
            '.contributor'
        ]
        
        for selector in author_selectors:
            author_elems = soup.select(selector)
            for elem in author_elems:
                author_name = elem.get_text().strip()
                if author_name and author_name not in authors:
                    authors.append(author_name)
                    
        return authors
        
    def _extract_journal_info(self, soup) -> Dict[str, Any]:
        """提取期刊信息"""
        journal_info = {}
        
        # 期刊名称
        journal_selectors = ['.journal-title', '.publication-title', '.source']
        for selector in journal_selectors:
            journal_elem = soup.select_one(selector)
            if journal_elem:
                journal_info['name'] = journal_elem.get_text().strip()
                break
                
        # 发表年份
        year_pattern = r'\b(19|20)\d{2}\b'
        year_selectors = ['.publication-date', '.year', '.date']
        for selector in year_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get_text()
                year_match = re.search(year_pattern, date_text)
                if year_match:
                    journal_info['year'] = int(year_match.group())
                    break
                    
        # 卷期页码信息
        citation_elem = soup.select_one('.citation')
        if citation_elem:
            citation_text = citation_elem.get_text()
            
            # 提取卷号
            volume_match = re.search(r'Vol\.?\s*(\d+)', citation_text, re.I)
            if volume_match:
                journal_info['volume'] = volume_match.group(1)
                
            # 提取期号
            issue_match = re.search(r'No\.?\s*(\d+)', citation_text, re.I)
            if issue_match:
                journal_info['issue'] = issue_match.group(1)
                
            # 提取页码
            pages_match = re.search(r'pp?\.?\s*(\d+(?:-\d+)?)', citation_text, re.I)
            if pages_match:
                journal_info['pages'] = pages_match.group(1)
                
        return journal_info
        
    def _extract_doi(self, soup) -> Optional[str]:
        """提取DOI"""
        # 查找DOI链接
        doi_selectors = [
            'a[href*="doi.org"]',
            '.doi',
            '[data-doi]'
        ]
        
        for selector in doi_selectors:
            doi_elem = soup.select_one(selector)
            if doi_elem:
                doi_text = doi_elem.get('href') or doi_elem.get('data-doi') or doi_elem.get_text()
                doi_match = re.search(r'10\.\d+/[^\s]+', doi_text)
                if doi_match:
                    return doi_match.group()
                    
        return None
        
    def _extract_keywords(self, soup) -> List[str]:
        """提取关键词"""
        keywords = []
        
        keyword_selectors = [
            '.keywords',
            '.keyword',
            '.tags',
            '.subject'
        ]
        
        for selector in keyword_selectors:
            keyword_elems = soup.select(selector)
            for elem in keyword_elems:
                keyword_text = elem.get_text().strip()
                # 分割关键词
                if ';' in keyword_text:
                    keywords.extend([k.strip() for k in keyword_text.split(';')])
                elif ',' in keyword_text:
                    keywords.extend([k.strip() for k in keyword_text.split(',')])
                else:
                    keywords.append(keyword_text)
                    
        return [k for k in keywords if k]
        
    def _extract_academic_content(self, soup) -> str:
        """提取学术论文正文内容"""
        # 移除不需要的元素
        for elem in soup(['script', 'style', 'nav', 'header', 'footer']):
            elem.decompose()
            
        # 学术论文内容选择器
        content_selectors = [
            '.article-body',
            '.paper-content',
            '.full-text',
            '.content',
            'main',
            '.article'
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
        
    def _extract_citations(self, soup) -> List[Dict[str, str]]:
        """提取引用文献"""
        citations = []
        
        citation_selectors = [
            '.reference',
            '.citation',
            '.bibliography li',
            '.ref-list li'
        ]
        
        for selector in citation_selectors:
            citation_elems = soup.select(selector)
            for elem in citation_elems:
                citation_text = elem.get_text().strip()
                if citation_text:
                    citations.append({'text': citation_text})
                    
        return citations
        
    def _create_academic_document(self, parsed_data: Dict[str, Any], doc_id: str) -> Document:
        """创建学术文档对象"""
        # 创建文档块
        chunks = []
        
        # 摘要作为一个块
        if parsed_data['abstract']:
            chunks.append(Chunk(
                content=parsed_data['abstract'],
                similarity=1.0,
                metadata={'type': 'abstract'}
            ))
            
        # 正文内容分块
        content = parsed_data['content']
        if content:
            # 简单的段落分块
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) > 100:  # 只保留有意义的段落
                    chunks.append(Chunk(
                        content=paragraph,
                        similarity=0.8,
                        metadata={'type': 'content', 'paragraph_index': i}
                    ))
                    
        return Document(
            id=doc_id,
            url=parsed_data['metadata']['url'],
            title=parsed_data['title'],
            chunks=chunks,
            credibility_score=0.9,  # 学术论文可靠性高
            source_type='academic',
            metadata=parsed_data['metadata']
        )
        
    def _build_academic_query(self, query: str) -> str:
        """构建学术搜索查询"""
        # 添加学术相关的关键词
        academic_terms = ["research", "study", "analysis", "investigation"]
        
        # 如果查询中没有学术术语，添加一些
        if not any(term in query.lower() for term in academic_terms):
            query += " research study"
            
        return query
        
    def _generate_search_urls(self, query: str, limit: int) -> List[str]:
        """生成搜索URL列表（模拟）"""
        # 这里应该根据具体的学术数据库API生成真实的搜索URL
        # 目前返回模拟的URL
        base_urls = [
            f"https://scholar.google.com/scholar?q={quote(query)}",
            f"https://pubmed.ncbi.nlm.nih.gov/?term={quote(query)}",
            f"https://arxiv.org/search/?query={quote(query)}",
            f"https://www.researchgate.net/search?q={quote(query)}"
        ]
        
        return base_urls[:limit]