# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from neo4j import GraphDatabase
from .retriever import Chunk, Document, Resource, Retriever, MysteryEvent


class Neo4jRetriever(Retriever):
    """Neo4j图数据库检索器，专门用于神秘事件研究"""
    
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        
        if not self.password:
            raise ValueError("NEO4J_PASSWORD is not set")
            
        self.driver = GraphDatabase.driver(
            self.uri, 
            auth=(self.username, self.password)
        )
        
        # 初始化数据库结构
        self._initialize_database()
    
    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
    
    def _initialize_database(self):
        """初始化数据库结构"""
        with self.driver.session() as session:
            # 创建索引
            session.run("""
                CREATE INDEX event_id_index IF NOT EXISTS 
                FOR (e:MysteryEvent) ON (e.event_id)
            """)
            
            session.run("""
                CREATE INDEX event_type_index IF NOT EXISTS 
                FOR (e:MysteryEvent) ON (e.event_type)
            """)
            
            session.run("""
                CREATE INDEX location_index IF NOT EXISTS 
                FOR (l:Location) ON (l.name)
            """)
            
            session.run("""
                CREATE INDEX document_id_index IF NOT EXISTS 
                FOR (d:Document) ON (d.id)
            """)
    
    def list_resources(self, query: str | None = None) -> list[Resource]:
        """列出Neo4j中的资源"""
        with self.driver.session() as session:
            if query:
                result = session.run("""
                    MATCH (d:Document)
                    WHERE d.title CONTAINS $query OR d.description CONTAINS $query
                    RETURN d.id as uri, d.title as title, d.description as description,
                           d.source_type as resource_type, d.credibility_score as credibility_score
                    LIMIT 50
                """, query=query)
            else:
                result = session.run("""
                    MATCH (d:Document)
                    RETURN d.id as uri, d.title as title, d.description as description,
                           d.source_type as resource_type, d.credibility_score as credibility_score
                    LIMIT 50
                """)
            
            resources = []
            for record in result:
                resource = Resource(
                    uri=record["uri"],
                    title=record["title"] or "",
                    description=record["description"] or "",
                    resource_type=record["resource_type"] or "unknown",
                    credibility_score=record["credibility_score"] or 0.5
                )
                resources.append(resource)
            
            return resources
    
    def query_relevant_documents(
        self, query: str, resources: list[Resource] = None
    ) -> list[Document]:
        """查询相关文档"""
        with self.driver.session() as session:
            # 构建查询条件
            if resources:
                resource_ids = [r.uri for r in resources]
                result = session.run("""
                    MATCH (d:Document)
                    WHERE d.id IN $resource_ids
                    AND (d.title CONTAINS $query OR d.content CONTAINS $query)
                    OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
                    RETURN d, collect(c) as chunks
                    ORDER BY d.credibility_score DESC
                    LIMIT 20
                """, resource_ids=resource_ids, query=query)
            else:
                result = session.run("""
                    MATCH (d:Document)
                    WHERE d.title CONTAINS $query OR d.content CONTAINS $query
                    OPTIONAL MATCH (d)-[:HAS_CHUNK]->(c:Chunk)
                    RETURN d, collect(c) as chunks
                    ORDER BY d.credibility_score DESC
                    LIMIT 20
                """, query=query)
            
            documents = []
            for record in result:
                doc_node = record["d"]
                chunk_nodes = record["chunks"]
                
                chunks = []
                for chunk_node in chunk_nodes:
                    if chunk_node:
                        chunk = Chunk(
                            content=chunk_node["content"],
                            similarity=chunk_node.get("similarity", 0.0),
                            metadata=dict(chunk_node)
                        )
                        chunks.append(chunk)
                
                document = Document(
                    id=doc_node["id"],
                    url=doc_node.get("url"),
                    title=doc_node.get("title"),
                    chunks=chunks,
                    credibility_score=doc_node.get("credibility_score", 0.5),
                    source_type=doc_node.get("source_type", "unknown"),
                    publication_date=self._parse_date(doc_node.get("publication_date")),
                    author=doc_node.get("author"),
                    metadata=dict(doc_node)
                )
                documents.append(document)
            
            return documents
    
    def query_mystery_events(
        self, 
        query: str, 
        event_type: str | None = None,
        location: str | None = None,
        date_range: tuple[datetime, datetime] | None = None,
        min_credibility: float = 0.0
    ) -> list[MysteryEvent]:
        """查询神秘事件"""
        with self.driver.session() as session:
            # 构建Cypher查询
            cypher_parts = ["MATCH (e:MysteryEvent)"]
            conditions = ["e.credibility_score >= $min_credibility"]
            params = {"min_credibility": min_credibility}
            
            # 添加文本搜索条件
            if query:
                conditions.append("(e.title CONTAINS $query OR e.description CONTAINS $query)")
                params["query"] = query
            
            # 添加事件类型条件
            if event_type:
                conditions.append("e.event_type = $event_type")
                params["event_type"] = event_type
            
            # 添加位置条件
            if location:
                cypher_parts.append("OPTIONAL MATCH (e)-[:OCCURRED_AT]->(l:Location)")
                conditions.append("(e.location CONTAINS $location OR l.name CONTAINS $location)")
                params["location"] = location
            
            # 添加日期范围条件
            if date_range:
                start_date, end_date = date_range
                conditions.append("e.date >= $start_date AND e.date <= $end_date")
                params["start_date"] = start_date.isoformat()
                params["end_date"] = end_date.isoformat()
            
            # 组装完整查询
            if conditions:
                cypher_parts.append("WHERE " + " AND ".join(conditions))
            
            cypher_parts.append("RETURN e ORDER BY e.credibility_score DESC, e.date DESC LIMIT 50")
            
            cypher_query = " ".join(cypher_parts)
            result = session.run(cypher_query, **params)
            
            events = []
            for record in result:
                event_node = record["e"]
                event = self._node_to_mystery_event(event_node)
                events.append(event)
            
            return events
    
    def store_mystery_event(self, event: MysteryEvent) -> bool:
        """存储神秘事件"""
        try:
            with self.driver.session() as session:
                # 创建或更新事件节点
                session.run("""
                    MERGE (e:MysteryEvent {event_id: $event_id})
                    SET e.event_type = $event_type,
                        e.title = $title,
                        e.description = $description,
                        e.location = $location,
                        e.date = $date,
                        e.credibility_score = $credibility_score,
                        e.source_url = $source_url,
                        e.witnesses = $witnesses,
                        e.evidence = $evidence,
                        e.updated_at = datetime()
                """, 
                    event_id=event.event_id,
                    event_type=event.event_type,
                    title=event.title,
                    description=event.description,
                    location=event.location,
                    date=event.date.isoformat() if event.date else None,
                    credibility_score=event.credibility_score,
                    source_url=event.source_url,
                    witnesses=event.witnesses,
                    evidence=event.evidence
                )
                
                # 如果有位置信息，创建位置节点和关系
                if event.location:
                    session.run("""
                        MATCH (e:MysteryEvent {event_id: $event_id})
                        MERGE (l:Location {name: $location})
                        MERGE (e)-[:OCCURRED_AT]->(l)
                    """, event_id=event.event_id, location=event.location)
                
                return True
        except Exception as e:
            print(f"Error storing mystery event: {e}")
            return False
    
    def find_related_events(
        self, 
        event: MysteryEvent, 
        similarity_threshold: float = 0.7
    ) -> list[MysteryEvent]:
        """查找相关事件"""
        with self.driver.session() as session:
            # 查找相同类型的事件
            result = session.run("""
                MATCH (e1:MysteryEvent {event_id: $event_id})
                MATCH (e2:MysteryEvent)
                WHERE e1 <> e2
                AND (
                    e1.event_type = e2.event_type
                    OR e1.location = e2.location
                    OR abs(duration.between(date(e1.date), date(e2.date)).days) <= 30
                )
                RETURN e2, 
                       CASE 
                           WHEN e1.event_type = e2.event_type THEN 0.4
                           ELSE 0.0
                       END +
                       CASE 
                           WHEN e1.location = e2.location THEN 0.3
                           ELSE 0.0
                       END +
                       CASE 
                           WHEN abs(duration.between(date(e1.date), date(e2.date)).days) <= 30 THEN 0.3
                           ELSE 0.0
                       END as similarity_score
                ORDER BY similarity_score DESC
                LIMIT 20
            """, event_id=event.event_id)
            
            related_events = []
            for record in result:
                similarity_score = record["similarity_score"]
                if similarity_score >= similarity_threshold:
                    event_node = record["e2"]
                    related_event = self._node_to_mystery_event(event_node)
                    related_events.append(related_event)
            
            return related_events
    
    def create_event_relationship(self, event1_id: str, event2_id: str, relationship_type: str, properties: Dict[str, Any] = None):
        """创建事件之间的关系"""
        with self.driver.session() as session:
            props_str = ""
            if properties:
                props_list = [f"{k}: ${k}" for k in properties.keys()]
                props_str = "{" + ", ".join(props_list) + "}"
            
            query = f"""
                MATCH (e1:MysteryEvent {{event_id: $event1_id}})
                MATCH (e2:MysteryEvent {{event_id: $event2_id}})
                MERGE (e1)-[r:{relationship_type} {props_str}]->(e2)
                RETURN r
            """
            
            params = {
                "event1_id": event1_id,
                "event2_id": event2_id,
                **(properties or {})
            }
            
            session.run(query, **params)
    
    def get_event_network(self, event_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """获取事件关系网络"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = (e:MysteryEvent {event_id: $event_id})-[*1..$max_depth]-(related:MysteryEvent)
                RETURN path
                LIMIT 100
            """, event_id=event_id, max_depth=max_depth)
            
            nodes = {}
            edges = []
            
            for record in result:
                path = record["path"]
                for node in path.nodes:
                    if "MysteryEvent" in node.labels:
                        nodes[node["event_id"]] = self._node_to_mystery_event(node)
                
                for relationship in path.relationships:
                    edges.append({
                        "source": relationship.start_node["event_id"],
                        "target": relationship.end_node["event_id"],
                        "type": relationship.type,
                        "properties": dict(relationship)
                    })
            
            return {
                "nodes": list(nodes.values()),
                "edges": edges
            }
    
    def _node_to_mystery_event(self, node) -> MysteryEvent:
        """将Neo4j节点转换为MysteryEvent对象"""
        return MysteryEvent(
            event_id=node["event_id"],
            event_type=node.get("event_type", "unknown"),
            title=node.get("title", ""),
            description=node.get("description", ""),
            location=node.get("location"),
            date=self._parse_date(node.get("date")),
            credibility_score=node.get("credibility_score", 0.5),
            source_url=node.get("source_url"),
            witnesses=node.get("witnesses", []),
            evidence=node.get("evidence", []),
            metadata=dict(node)
        )
    
    def _parse_date(self, date_str: str) -> datetime | None:
        """解析日期字符串"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None