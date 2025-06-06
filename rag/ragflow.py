# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from .retriever import Chunk, Document, Resource, Retriever, MysteryEvent


def parse_uri(uri: str) -> tuple[str, str | None]:
    """解析URI获取数据集ID和文档ID"""
    parsed = urlparse(uri)
    path_parts = parsed.path.strip('/').split('/')
    
    if len(path_parts) >= 1:
        dataset_id = path_parts[0]
        document_id = path_parts[1] if len(path_parts) > 1 else None
        return dataset_id, document_id
    
    return uri, None


class RAGFlowRetriever(Retriever):
    """RAGFlow检索器，扩展支持神秘事件研究"""

    def __init__(self):
        api_url = os.getenv("RAGFLOW_API_URL")
        if not api_url:
            raise ValueError("RAGFLOW_API_URL is not set")
        self.api_url = api_url

        api_key = os.getenv("RAGFLOW_API_KEY")
        if not api_key:
            raise ValueError("RAGFLOW_API_KEY is not set")
        self.api_key = api_key

        page_size = os.getenv("RAGFLOW_PAGE_SIZE")
        self.page_size = int(page_size) if page_size else 10

    def query_relevant_documents(
        self, query: str, resources: list[Resource] = None
    ) -> list[Document]:
        """查询相关文档"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        dataset_ids: list[str] = []
        document_ids: list[str] = []

        if resources:
            for resource in resources:
                dataset_id, document_id = parse_uri(resource.uri)
                dataset_ids.append(dataset_id)
                if document_id:
                    document_ids.append(document_id)

        payload = {
            "question": query,
            "dataset_ids": dataset_ids,
            "document_ids": document_ids,
            "page_size": self.page_size,
        }

        response = requests.post(
            f"{self.api_url}/api/v1/retrieval", headers=headers, json=payload
        )

        if response.status_code != 200:
            raise Exception(f"Failed to query documents: {response.text}")

        result = response.json()
        data = result.get("data", {})
        doc_aggs = data.get("doc_aggs", [])
        
        docs: dict[str, Document] = {}
        for doc in doc_aggs:
            doc_id = doc.get("doc_id")
            document = Document(
                id=doc_id,
                title=doc.get("doc_name"),
                chunks=[],
                source_type="ragflow",
                metadata=doc
            )
            # 分析可信度
            document.credibility_score = self.analyze_credibility(document)
            docs[doc_id] = document

        for chunk in data.get("chunks", []):
            doc = docs.get(chunk.get("document_id"))
            if doc:
                chunk_obj = Chunk(
                    content=chunk.get("content"),
                    similarity=chunk.get("similarity"),
                    metadata=chunk
                )
                doc.chunks.append(chunk_obj)

        return list(docs.values())

    def list_resources(self, query: str | None = None) -> list[Resource]:
        """列出资源"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        params = {}
        if query:
            params["name"] = query

        response = requests.get(
            f"{self.api_url}/api/v1/datasets", headers=headers, params=params
        )

        if response.status_code != 200:
            raise Exception(f"Failed to list resources: {response.text}")

        result = response.json()
        data = result.get("data", [])
        
        resources = []
        for dataset in data:
            resource = Resource(
                uri=dataset.get("id"),
                title=dataset.get("name", ""),
                description=dataset.get("description", ""),
                resource_type="dataset",
                credibility_score=0.7,  # RAGFlow数据集默认可信度
                metadata=dataset
            )
            resources.append(resource)
            
        return resources
    
    def query_mystery_events(
        self, 
        query: str, 
        event_type: str | None = None,
        location: str | None = None,
        date_range: tuple[datetime, datetime] | None = None,
        min_credibility: float = 0.0
    ) -> list[MysteryEvent]:
        """查询神秘事件（RAGFlow实现）"""
        # 构建增强查询
        enhanced_query = query
        if event_type:
            enhanced_query += f" {event_type}"
        if location:
            enhanced_query += f" {location}"
            
        # 查询相关文档
        documents = self.query_relevant_documents(enhanced_query)
        
        # 从文档中提取神秘事件
        events = []
        for doc in documents:
            if doc.credibility_score >= min_credibility:
                # 尝试从文档内容中提取事件信息
                event = self._extract_mystery_event_from_document(doc)
                if event and self._matches_criteria(event, event_type, location, date_range):
                    events.append(event)
                    
        return events
    
    def store_mystery_event(self, event: MysteryEvent) -> bool:
        """存储神秘事件（RAGFlow实现）"""
        # RAGFlow主要用于检索，存储功能有限
        # 这里可以将事件转换为文档格式并尝试上传
        try:
            # 将事件转换为文档内容
            content = self._event_to_content(event)
            
            # 这里需要实现具体的RAGFlow文档上传逻辑
            # 由于RAGFlow API的限制，这里返回False表示不支持直接存储
            return False
        except Exception:
            return False
    
    def find_related_events(
        self, 
        event: MysteryEvent, 
        similarity_threshold: float = 0.7
    ) -> list[MysteryEvent]:
        """查找相关事件"""
        # 构建查询字符串
        query_parts = [event.title, event.description]
        if event.location:
            query_parts.append(event.location)
        if event.event_type:
            query_parts.append(event.event_type)
            
        query = " ".join(query_parts)
        
        # 查询相关事件
        related_events = self.query_mystery_events(
            query=query,
            event_type=event.event_type,
            min_credibility=0.3
        )
        
        # 过滤掉自身并按相似度排序
        filtered_events = [
            e for e in related_events 
            if e.event_id != event.event_id
        ]
        
        return filtered_events[:10]  # 返回前10个相关事件
    
    def _extract_mystery_event_from_document(self, doc: Document) -> MysteryEvent | None:
        """从文档中提取神秘事件信息"""
        try:
            # 简单的事件提取逻辑
            content = "\n".join([chunk.content for chunk in doc.chunks])
            
            # 尝试识别事件类型
            event_type = self._identify_event_type(content)
            
            # 创建神秘事件对象
            event = MysteryEvent(
                event_id=f"ragflow_{doc.id}",
                event_type=event_type,
                title=doc.title or "未知事件",
                description=content[:500],  # 取前500字符作为描述
                source_url=doc.url,
                credibility_score=doc.credibility_score,
                metadata={
                    "source": "ragflow",
                    "document_id": doc.id,
                    **doc.metadata
                }
            )
            
            return event
        except Exception:
            return None
    
    def _identify_event_type(self, content: str) -> str:
        """识别事件类型"""
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ["ufo", "不明飞行物", "飞碟"]):
            return "UFO"
        elif any(keyword in content_lower for keyword in ["水怪", "神秘生物", "cryptid"]):
            return "cryptid"
        elif any(keyword in content_lower for keyword in ["幽灵", "鬼魂", "paranormal"]):
            return "paranormal"
        elif any(keyword in content_lower for keyword in ["失踪", "消失", "disappearance"]):
            return "disappearance"
        elif any(keyword in content_lower for keyword in ["古代", "文明", "ancient"]):
            return "ancient_mystery"
        else:
            return "unknown"
    
    def _matches_criteria(
        self, 
        event: MysteryEvent, 
        event_type: str | None, 
        location: str | None, 
        date_range: tuple[datetime, datetime] | None
    ) -> bool:
        """检查事件是否匹配查询条件"""
        if event_type and event.event_type != event_type:
            return False
            
        if location and event.location and location.lower() not in event.location.lower():
            return False
            
        if date_range and event.date:
            start_date, end_date = date_range
            if not (start_date <= event.date <= end_date):
                return False
                
        return True
    
    def _event_to_content(self, event: MysteryEvent) -> str:
        """将事件转换为文档内容"""
        content_parts = [
            f"标题: {event.title}",
            f"类型: {event.event_type}",
            f"描述: {event.description}"
        ]
        
        if event.location:
            content_parts.append(f"地点: {event.location}")
        if event.date:
            content_parts.append(f"日期: {event.date.strftime('%Y-%m-%d')}")
        if event.witnesses:
            content_parts.append(f"目击者: {', '.join(event.witnesses)}")
        if event.evidence:
            content_parts.append(f"证据: {', '.join(event.evidence)}")
            
        return "\n".join(content_parts)