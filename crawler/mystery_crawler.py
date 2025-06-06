# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import quote, urljoin

from .crawler import Crawler
from ..rag.retriever import Document, Chunk, MysteryEvent
from ..config.mystery_config import DataSourceConfig, MysteryEventType


class MysteryCrawler(Crawler):
    """神秘事件专用爬虫"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.mystery_keywords = {
            MysteryEventType.UFO: [
                "UFO", "unidentified flying object", "flying saucer", "alien",
                "extraterrestrial", "close encounter", "abduction", "sighting"
            ],
            MysteryEventType.CRYPTID: [
                "bigfoot", "sasquatch", "yeti", "chupacabra", "loch ness monster",
                "cryptid", "unknown creature", "mysterious animal"
            ],
            MysteryEventType.PARANORMAL: [
                "ghost", "spirit", "haunting", "poltergeist", "supernatural",
                "paranormal", "psychic", "telepathy", "precognition"
            ],
            MysteryEventType.ANCIENT_MYSTERY: [
                "ancient mystery", "archaeological anomaly", "lost civilization",
                "ancient technology", "megalith", "pyramid mystery"
            ],
            MysteryEventType.DISAPPEARANCE: [
                "mysterious disappearance", "vanished", "missing person",
                "bermuda triangle", "unexplained absence"
            ],
            MysteryEventType.NATURAL_ANOMALY: [
                "ball lightning", "earthquake lights", "atmospheric anomaly",
                "geophysical anomaly", "unexplained phenomenon"
            ]
        }
        
    async def crawl_url(self, url: str) -> Optional[Document]:
        """爬取神秘事件页面"""
        html = await self._fetch_html(url)
        if not html:
            return None
            
        parsed_data = self._parse_mystery_html(html, url)
        if not parsed_data:
            return None
            
        doc_id = hashlib.md5(url.encode()).hexdigest()
        document = self._create_mystery_document(parsed_data, doc_id)
        
        return document
        
    async def search(self, query: str, limit: int = 10) -> List[Document]:
        """搜索神秘事件"""
        documents = []
        
        # 识别查询的神秘事件类型
        event_type = self._identify_event_type(query)
        
        # 构建神秘事件搜索查询
        mystery_query = self._build_mystery_query(query, event_type)
        
        # 生成搜索URL
        search_urls = self._generate_mystery_search_urls(mystery_query, limit)
        
        for url in search_urls:
            doc = await self.crawl_url(url)
            if doc:
                documents.append(doc)
                
        return documents[:limit]
        
    def _parse_mystery_html(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """解析神秘事件HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = self._extract_title(soup)
        if not title:
            return None
            
        # 提取事件描述
        description = self._extract_mystery_description(soup)
        
        # 提取事件类型
        event_type = self._detect_event_type(title + " " + description)
        
        # 提取位置信息
        location = self._extract_location(soup)
        
        # 提取时间信息
        event_date = self._extract_event_date(soup)
        
        # 提取目击者信息
        witnesses = self._extract_witnesses(soup)
        
        # 提取证据信息
        evidence = self._extract_evidence(soup)
        
        # 计算可信度分数
        credibility_score = self._calculate_credibility(soup, witnesses, evidence)
        
        # 创建神秘事件对象
        mystery_event = MysteryEvent(
            event_id=hashlib.md5((url + title).encode()).hexdigest()[:16],
            event_type=event_type.value if event_type else "unknown",
            title=title,
            description=description,
            location=location,
            date=event_date,
            credibility_score=credibility_score,
            source_url=url,
            witnesses=witnesses,
            evidence=evidence
        )
        
        metadata = {
            'url': url,
            'crawled_at': datetime.now().isoformat(),
            'source_type': 'mystery',
            'reliability_score': self.config.reliability_score,
            'event_type': event_type.value if event_type else "unknown",
            'location': location,
            'event_date': event_date.isoformat() if event_date else None,
            'witnesses_count': len(witnesses),
            'evidence_count': len(evidence),
            'credibility_score': credibility_score
        }
        
        return {
            'title': title,
            'content': description,
            'mystery_event': mystery_event,
            'metadata': metadata
        }
        
    def _extract_mystery_description(self, soup) -> str:
        """提取神秘事件描述"""
        # 神秘事件网站常见的内容选择器
        content_selectors = [
            '.story-content',
            '.event-description',
            '.case-details',
            '.incident-report',
            '.sighting-details',
            '.article-content',
            '.post-content',
            '.content',
            'main'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # 移除不需要的元素
                for unwanted in content_elem(['script', 'style', 'nav', 'aside']):
                    unwanted.decompose()
                return content_elem.get_text(separator='\n', strip=True)
                
        # 如果没有找到特定内容，尝试提取body内容
        body = soup.find('body')
        if body:
            return body.get_text(separator='\n', strip=True)
            
        return ""
        
    def _detect_event_type(self, text: str) -> Optional[MysteryEventType]:
        """检测神秘事件类型"""
        text_lower = text.lower()
        
        # 计算每种类型的关键词匹配分数
        type_scores = {}
        for event_type, keywords in self.mystery_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if score > 0:
                type_scores[event_type] = score
                
        # 返回得分最高的类型
        if type_scores:
            return max(type_scores, key=type_scores.get)
            
        return None
        
    def _extract_location(self, soup) -> Optional[str]:
        """提取事件位置"""
        location_selectors = [
            '.location',
            '.place',
            '.address',
            '.coordinates',
            '.where'
        ]
        
        for selector in location_selectors:
            location_elem = soup.select_one(selector)
            if location_elem:
                location_text = location_elem.get_text().strip()
                if location_text:
                    return location_text
                    
        # 尝试从文本中提取位置信息
        text = soup.get_text()
        location_patterns = [
            r'(?:in|at|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*[A-Z]{2})?)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)',
            r'coordinates?:?\s*([\d.-]+,\s*[\d.-]+)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
                
        return None
        
    def _extract_event_date(self, soup) -> Optional[datetime]:
        """提取事件日期"""
        date_selectors = [
            '.event-date',
            '.incident-date',
            '.sighting-date',
            '.when',
            'time[datetime]',
            '.date'
        ]
        
        for selector in date_selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text()
                parsed_date = self._parse_date(date_text)
                if parsed_date:
                    return parsed_date
                    
        # 尝试从文本中提取日期
        text = soup.get_text()
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\w+\s+\d{1,2},\s+\d{4})',
            r'(\d{1,2}\s+\w+\s+\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                parsed_date = self._parse_date(match.group(1))
                if parsed_date:
                    return parsed_date
                    
        return None
        
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """解析日期字符串"""
        import dateutil.parser
        try:
            return dateutil.parser.parse(date_text)
        except:
            return None
            
    def _extract_witnesses(self, soup) -> List[str]:
        """提取目击者信息"""
        witnesses = []
        
        witness_selectors = [
            '.witness',
            '.witnesses',
            '.eyewitness',
            '.reporter',
            '.observer'
        ]
        
        for selector in witness_selectors:
            witness_elems = soup.select(selector)
            for elem in witness_elems:
                witness_text = elem.get_text().strip()
                if witness_text and witness_text not in witnesses:
                    witnesses.append(witness_text)
                    
        # 尝试从文本中提取目击者信息
        text = soup.get_text()
        witness_patterns = [
            r'witness(?:es)?:?\s*([^.\n]+)',
            r'reported by\s+([^.\n]+)',
            r'observed by\s+([^.\n]+)',
            r'seen by\s+([^.\n]+)'
        ]
        
        for pattern in witness_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                witness = match.group(1).strip()
                if witness and witness not in witnesses:
                    witnesses.append(witness)
                    
        return witnesses
        
    def _extract_evidence(self, soup) -> List[str]:
        """提取证据信息"""
        evidence = []
        
        evidence_selectors = [
            '.evidence',
            '.proof',
            '.documentation',
            '.photos',
            '.videos',
            '.recordings'
        ]
        
        for selector in evidence_selectors:
            evidence_elems = soup.select(selector)
            for elem in evidence_elems:
                evidence_text = elem.get_text().strip()
                if evidence_text and evidence_text not in evidence:
                    evidence.append(evidence_text)
                    
        # 查找图片和视频链接
        media_elements = soup.find_all(['img', 'video', 'audio'])
        for elem in media_elements:
            src = elem.get('src')
            if src:
                evidence.append(f"Media: {src}")
                
        return evidence
        
    def _calculate_credibility(self, soup, witnesses: List[str], evidence: List[str]) -> float:
        """计算可信度分数"""
        score = 0.5  # 基础分数
        
        # 目击者数量影响可信度
        if witnesses:
            score += min(len(witnesses) * 0.1, 0.2)
            
        # 证据数量影响可信度
        if evidence:
            score += min(len(evidence) * 0.1, 0.2)
            
        # 检查是否有官方来源
        text = soup.get_text().lower()
        official_indicators = [
            'police report', 'government', 'official', 'military',
            'faa', 'nasa', 'noaa', 'usgs'
        ]
        if any(indicator in text for indicator in official_indicators):
            score += 0.2
            
        # 检查是否有科学分析
        scientific_indicators = [
            'analysis', 'research', 'study', 'investigation',
            'scientist', 'expert', 'laboratory'
        ]
        if any(indicator in text for indicator in scientific_indicators):
            score += 0.1
            
        # 确保分数在0-1范围内
        return min(max(score, 0.0), 1.0)
        
    def _create_mystery_document(self, parsed_data: Dict[str, Any], doc_id: str) -> Document:
        """创建神秘事件文档对象"""
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
                        similarity=0.8,
                        metadata={'type': 'content', 'paragraph_index': i}
                    ))
                    
        return Document(
            id=doc_id,
            url=parsed_data['metadata']['url'],
            title=parsed_data['title'],
            chunks=chunks,
            mystery_event=parsed_data['mystery_event'],
            credibility_score=parsed_data['metadata']['credibility_score'],
            source_type='mystery',
            metadata=parsed_data['metadata']
        )
        
    def _identify_event_type(self, query: str) -> Optional[MysteryEventType]:
        """识别查询的神秘事件类型"""
        return self._detect_event_type(query)
        
    def _build_mystery_query(self, query: str, event_type: Optional[MysteryEventType]) -> str:
        """构建神秘事件搜索查询"""
        if event_type and event_type in self.mystery_keywords:
            # 添加相关关键词
            keywords = self.mystery_keywords[event_type][:3]  # 取前3个关键词
            query += " " + " ".join(keywords)
            
        return query
        
    def _generate_mystery_search_urls(self, query: str, limit: int) -> List[str]:
        """生成神秘事件搜索URL列表（模拟）"""
        # 这里应该根据具体的神秘事件网站API生成真实的搜索URL
        mystery_sites = [
            f"https://www.mufon.com/search?q={quote(query)}",
            f"https://nuforc.org/search?q={quote(query)}",
            f"https://cryptidz.fandom.com/search?q={quote(query)}",
            f"https://paranormal.about.com/search?q={quote(query)}"
        ]
        
        return mystery_sites[:limit]