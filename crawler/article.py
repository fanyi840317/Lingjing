# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
from markdownify import markdownify as md


class Article:
    """文章类，扩展支持神秘事件信息提取"""
    
    def __init__(
        self, 
        title: str, 
        html_content: str,
        url: str = "",
        author: str = "",
        publication_date: Optional[datetime] = None,
        source_type: str = "unknown",
        credibility_score: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.html_content = html_content
        self.url = url
        self.author = author
        self.publication_date = publication_date
        self.source_type = source_type
        self.credibility_score = credibility_score
        self.metadata = metadata or {}
        
        # 神秘事件相关属性
        self.mystery_keywords = []
        self.event_type = "unknown"
        self.location_mentions = []
        self.date_mentions = []
        self.witness_mentions = []
        self.evidence_mentions = []
        
        # 自动分析内容
        self._analyze_content()

    def to_markdown(self, including_title: bool = True) -> str:
        """转换为Markdown格式"""
        markdown = ""
        if including_title:
            markdown += f"# {self.title}\n\n"
        
        # 添加元数据信息
        if self.author:
            markdown += f"**作者**: {self.author}\n\n"
        if self.publication_date:
            markdown += f"**发布时间**: {self.publication_date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        if self.source_type != "unknown":
            markdown += f"**来源类型**: {self.source_type}\n\n"
        if self.credibility_score != 0.5:
            markdown += f"**可信度评分**: {self.credibility_score:.2f}\n\n"
        
        # 添加神秘事件信息
        if self.event_type != "unknown":
            markdown += f"**事件类型**: {self.event_type}\n\n"
        if self.mystery_keywords:
            markdown += f"**关键词**: {', '.join(self.mystery_keywords)}\n\n"
        if self.location_mentions:
            markdown += f"**地点**: {', '.join(self.location_mentions)}\n\n"
        
        markdown += "---\n\n"
        markdown += md(self.html_content)
        return markdown

    def to_message(self) -> list[dict]:
        """转换为消息格式，支持图片和文本"""
        image_pattern = r"!\[.*?\]\((.*?)\)"

        content: list[dict[str, str]] = []
        parts = re.split(image_pattern, self.to_markdown())

        for i, part in enumerate(parts):
            if i % 2 == 1:
                image_url = urljoin(self.url, part.strip())
                content.append({"type": "image_url", "image_url": {"url": image_url}})
            else:
                if part.strip():
                    content.append({"type": "text", "text": part.strip()})

        return content
    
    def extract_mystery_info(self) -> Dict[str, Any]:
        """提取神秘事件信息"""
        return {
            "event_type": self.event_type,
            "mystery_keywords": self.mystery_keywords,
            "location_mentions": self.location_mentions,
            "date_mentions": self.date_mentions,
            "witness_mentions": self.witness_mentions,
            "evidence_mentions": self.evidence_mentions,
            "credibility_score": self.credibility_score
        }
    
    def _analyze_content(self):
        """分析内容，提取神秘事件相关信息"""
        content_text = self._get_plain_text()
        content_lower = content_text.lower()
        
        # 识别事件类型
        self.event_type = self._identify_event_type(content_lower)
        
        # 提取关键词
        self.mystery_keywords = self._extract_mystery_keywords(content_lower)
        
        # 提取地点信息
        self.location_mentions = self._extract_locations(content_text)
        
        # 提取日期信息
        self.date_mentions = self._extract_dates(content_text)
        
        # 提取目击者信息
        self.witness_mentions = self._extract_witnesses(content_text)
        
        # 提取证据信息
        self.evidence_mentions = self._extract_evidence(content_text)
    
    def _get_plain_text(self) -> str:
        """获取纯文本内容"""
        # 简单的HTML标签移除
        text = re.sub(r'<[^>]+>', ' ', self.html_content)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _identify_event_type(self, content: str) -> str:
        """识别事件类型"""
        event_keywords = {
            "UFO": ["ufo", "不明飞行物", "飞碟", "外星人", "alien", "flying saucer"],
            "cryptid": ["水怪", "神秘生物", "cryptid", "bigfoot", "yeti", "尼斯湖水怪"],
            "paranormal": ["幽灵", "鬼魂", "paranormal", "ghost", "spirit", "supernatural"],
            "disappearance": ["失踪", "消失", "disappearance", "missing", "vanished"],
            "ancient_mystery": ["古代", "文明", "ancient", "civilization", "玛雅", "maya", "金字塔"],
            "natural_anomaly": ["异常现象", "自然异象", "anomaly", "百慕大", "bermuda"]
        }
        
        for event_type, keywords in event_keywords.items():
            if any(keyword in content for keyword in keywords):
                return event_type
        
        return "unknown"
    
    def _extract_mystery_keywords(self, content: str) -> List[str]:
        """提取神秘事件关键词"""
        mystery_keywords = [
            "ufo", "不明飞行物", "飞碟", "外星人", "水怪", "神秘生物", 
            "幽灵", "鬼魂", "失踪", "消失", "古代文明", "金字塔", 
            "百慕大三角", "麦田怪圈", "尼斯湖水怪", "大脚怪", "雪人"
        ]
        
        found_keywords = []
        for keyword in mystery_keywords:
            if keyword in content:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _extract_locations(self, content: str) -> List[str]:
        """提取地点信息"""
        # 简单的地点提取逻辑
        location_patterns = [
            r'在([^，。！？\s]{2,10}[市县区镇村])(?:[，。！？\s])',
            r'位于([^，。！？\s]{2,15})(?:[，。！？\s])',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:,\s*[A-Z]{2})?)',  # 英文地名
        ]
        
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, content)
            locations.extend(matches)
        
        # 去重并过滤
        unique_locations = list(set(locations))
        return [loc for loc in unique_locations if len(loc) > 1 and len(loc) < 50]
    
    def _extract_dates(self, content: str) -> List[str]:
        """提取日期信息"""
        date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{4}年\d{1,2}月',
            r'[A-Za-z]+ \d{1,2}, \d{4}'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            dates.extend(matches)
        
        return list(set(dates))
    
    def _extract_witnesses(self, content: str) -> List[str]:
        """提取目击者信息"""
        witness_patterns = [
            r'目击者([^，。！？\s]{2,10})',
            r'证人([^，。！？\s]{2,10})',
            r'witness\s+([A-Za-z\s]{2,20})',
            r'([^，。！？\s]{2,10})(?:声称|表示|说|报告)'
        ]
        
        witnesses = []
        for pattern in witness_patterns:
            matches = re.findall(pattern, content)
            witnesses.extend(matches)
        
        return list(set(witnesses))[:5]  # 限制数量
    
    def _extract_evidence(self, content: str) -> List[str]:
        """提取证据信息"""
        evidence_keywords = [
            "照片", "视频", "录音", "物证", "痕迹", "足迹", 
            "photo", "video", "recording", "evidence", "trace", "footprint"
        ]
        
        evidence = []
        content_lower = content.lower()
        
        for keyword in evidence_keywords:
            if keyword in content_lower:
                evidence.append(keyword)
        
        return list(set(evidence))
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "url": self.url,
            "author": self.author,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "source_type": self.source_type,
            "credibility_score": self.credibility_score,
            "content": self._get_plain_text(),
            "mystery_info": self.extract_mystery_info(),
            "metadata": self.metadata
        }