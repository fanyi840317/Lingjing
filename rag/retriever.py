# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

import abc
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Chunk:
    """文档片段类"""
    content: str
    similarity: float
    metadata: Dict[str, Any]
    
    def __init__(self, content: str, similarity: float, metadata: Dict[str, Any] = None):
        self.content = content
        self.similarity = similarity
        self.metadata = metadata or {}


class MysteryEvent:
    """神秘事件类"""
    def __init__(
        self,
        event_id: str,
        event_type: str,
        title: str,
        description: str,
        location: Optional[str] = None,
        date: Optional[datetime] = None,
        credibility_score: float = 0.5,
        source_url: Optional[str] = None,
        witnesses: Optional[list] = None,
        evidence: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.title = title
        self.description = description
        self.location = location
        self.date = date
        self.credibility_score = credibility_score
        self.source_url = source_url
        self.witnesses = witnesses or []
        self.evidence = evidence or []
        self.metadata = metadata or {}
    
    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "date": self.date.isoformat() if self.date else None,
            "credibility_score": self.credibility_score,
            "source_url": self.source_url,
            "witnesses": self.witnesses,
            "evidence": self.evidence,
            "metadata": self.metadata
        }


class Document:
    """文档类，扩展支持神秘事件信息"""
    
    def __init__(
        self,
        id: str,
        url: str | None = None,
        title: str | None = None,
        chunks: list[Chunk] = None,
        mystery_event: MysteryEvent | None = None,
        credibility_score: float = 0.5,
        source_type: str = "unknown",
        publication_date: datetime | None = None,
        author: str | None = None,
        metadata: Dict[str, Any] = None
    ):
        self.id = id
        self.url = url
        self.title = title
        self.chunks = chunks or []
        self.mystery_event = mystery_event
        self.credibility_score = credibility_score
        self.source_type = source_type
        self.publication_date = publication_date
        self.author = author
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        d = {
            "id": self.id,
            "content": "\n\n".join([chunk.content for chunk in self.chunks]),
            "credibility_score": self.credibility_score,
            "source_type": self.source_type,
            "author": self.author,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "metadata": self.metadata
        }
        if self.url:
            d["url"] = self.url
        if self.title:
            d["title"] = self.title
        if self.mystery_event:
            d["mystery_event"] = self.mystery_event.to_dict()
        return d


class Resource(BaseModel):
    """资源类，扩展支持神秘事件研究"""
    
    uri: str = Field(..., description="资源的URI")
    title: str = Field(..., description="资源标题")
    description: str | None = Field("", description="资源描述")
    resource_type: str = Field("unknown", description="资源类型")
    credibility_score: float = Field(0.5, description="可信度评分")
    access_level: str = Field("public", description="访问级别")
    last_updated: datetime | None = Field(None, description="最后更新时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class Retriever(abc.ABC):
    """检索器抽象基类，扩展支持神秘事件研究功能"""

    @abc.abstractmethod
    def list_resources(self, query: str | None = None) -> list[Resource]:
        """列出RAG提供商的资源"""
        pass

    @abc.abstractmethod
    def query_relevant_documents(
        self, query: str, resources: list[Resource] = None
    ) -> list[Document]:
        """从资源中查询相关文档"""
        pass
    
    @abc.abstractmethod
    def query_mystery_events(
        self, 
        query: str, 
        event_type: str | None = None,
        location: str | None = None,
        date_range: tuple[datetime, datetime] | None = None,
        min_credibility: float = 0.0
    ) -> list[MysteryEvent]:
        """查询神秘事件"""
        pass
    
    @abc.abstractmethod
    def store_mystery_event(self, event: MysteryEvent) -> bool:
        """存储神秘事件"""
        pass
    
    @abc.abstractmethod
    def find_related_events(
        self, 
        event: MysteryEvent, 
        similarity_threshold: float = 0.7
    ) -> list[MysteryEvent]:
        """查找相关事件"""
        pass
    
    def analyze_credibility(self, document: Document) -> float:
        """分析文档可信度（默认实现）"""
        # 基础可信度分析逻辑
        score = 0.5
        
        # 根据来源类型调整
        source_scores = {
            "academic": 0.9,
            "news": 0.7,
            "government": 0.8,
            "research_institute": 0.75,
            "forum": 0.3,
            "blog": 0.2,
            "unknown": 0.1
        }
        score = source_scores.get(document.source_type, 0.1)
        
        # 根据内容长度和细节丰富度调整
        content_length = sum(len(chunk.content) for chunk in document.chunks)
        if content_length > 1000:
            score += 0.1
        elif content_length < 100:
            score -= 0.2
            
        # 确保分数在0-1范围内
        return max(0.0, min(1.0, score))