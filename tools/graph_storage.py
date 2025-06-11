# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

from langchain_core.tools import BaseTool, tool

from config.mystery_config import MysteryEventConfig
from tools.decorators import log_io

logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """图节点"""
    id: str
    label: str
    properties: Dict[str, Any]
    node_type: str  # event, person, location, organization, concept


@dataclass
class GraphRelationship:
    """图关系"""
    id: str
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any]
    weight: float = 1.0


@dataclass
class GraphData:
    """图数据"""
    nodes: List[GraphNode]
    relationships: List[GraphRelationship]
    metadata: Dict[str, Any]


class Neo4jStorage(BaseTool):
    """Neo4j图数据库存储工具"""
    name: str = "neo4j_storage"
    description: str = "Store and query data in Neo4j graph database."
    
    def __init__(self, config: Optional[MysteryEventConfig] = None):
        """初始化Neo4j存储
        
        Args:
            config: 神秘事件配置
        """
        super().__init__()
        self.config = config or MysteryEventConfig()
        self.driver = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """初始化数据库连接"""
        try:
            # 这里应该使用真实的Neo4j驱动，但为了演示，我们使用模拟
            # from neo4j import GraphDatabase
            # self.driver = GraphDatabase.driver(
            #     self.config.neo4j_config["uri"],
            #     auth=(self.config.neo4j_config["username"], self.config.neo4j_config["password"])
            # )
            
            # 模拟连接
            self.driver = "mock_neo4j_driver"
            logger.info("Neo4j connection initialized (mock)")
            
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j connection: {e}")
            self.driver = None
    
    def _run(self, operation: str, data: str = None, query: str = None) -> str:
        """运行Neo4j操作
        
        Args:
            operation: 操作类型 (store, query, update, delete)
            data: JSON格式的数据
            query: Cypher查询语句
            
        Returns:
            JSON格式的操作结果
        """
        try:
            if not self.driver:
                return json.dumps({"error": "Neo4j connection not available"}, ensure_ascii=False)
            
            if operation == "store":
                return self._store_data(data)
            elif operation == "query":
                return self._query_data(query)
            elif operation == "update":
                return self._update_data(data)
            elif operation == "delete":
                return self._delete_data(data)
            else:
                return json.dumps({"error": f"Unknown operation: {operation}"}, ensure_ascii=False)
                
        except Exception as e:
            error_msg = f"Failed to execute Neo4j operation. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _store_data(self, data: str) -> str:
        """存储数据到Neo4j"""
        try:
            graph_data = json.loads(data)
            
            # 解析图数据
            nodes = graph_data.get("nodes", [])
            relationships = graph_data.get("relationships", [])
            
            # 模拟存储节点
            stored_nodes = []
            for node_data in nodes:
                node = GraphNode(
                    id=node_data.get("id", ""),
                    label=node_data.get("label", ""),
                    properties=node_data.get("properties", {}),
                    node_type=node_data.get("node_type", "unknown")
                )
                
                # 在真实实现中，这里会执行Cypher CREATE语句
                cypher_query = self._generate_create_node_cypher(node)
                logger.info(f"Would execute: {cypher_query}")
                
                stored_nodes.append(asdict(node))
            
            # 模拟存储关系
            stored_relationships = []
            for rel_data in relationships:
                relationship = GraphRelationship(
                    id=rel_data.get("id", ""),
                    source_id=rel_data.get("source_id", ""),
                    target_id=rel_data.get("target_id", ""),
                    relationship_type=rel_data.get("relationship_type", ""),
                    properties=rel_data.get("properties", {}),
                    weight=rel_data.get("weight", 1.0)
                )
                
                # 在真实实现中，这里会执行Cypher MATCH + CREATE语句
                cypher_query = self._generate_create_relationship_cypher(relationship)
                logger.info(f"Would execute: {cypher_query}")
                
                stored_relationships.append(asdict(relationship))
            
            return json.dumps({
                "status": "success",
                "stored_nodes": len(stored_nodes),
                "stored_relationships": len(stored_relationships),
                "nodes": stored_nodes,
                "relationships": stored_relationships
            }, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to store data in Neo4j. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _query_data(self, query: str) -> str:
        """查询Neo4j数据"""
        try:
            # 在真实实现中，这里会执行Cypher查询
            logger.info(f"Would execute query: {query}")
            
            # 模拟查询结果
            mock_results = [
                {
                    "node": {
                        "id": "event_001",
                        "label": "UFO Sighting",
                        "properties": {
                            "title": "UFO目击事件",
                            "date": "2023-01-15",
                            "location": "北京市"
                        }
                    }
                },
                {
                    "relationship": {
                        "type": "OCCURRED_AT",
                        "properties": {
                            "confidence": 0.9
                        }
                    }
                }
            ]
            
            return json.dumps({
                "status": "success",
                "query": query,
                "results": mock_results,
                "count": len(mock_results)
            }, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to query Neo4j data. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _update_data(self, data: str) -> str:
        """更新Neo4j数据"""
        try:
            update_data = json.loads(data)
            
            # 模拟更新操作
            logger.info(f"Would update data: {update_data}")
            
            return json.dumps({
                "status": "success",
                "updated_items": 1,
                "message": "Data updated successfully"
            }, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to update Neo4j data. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _delete_data(self, data: str) -> str:
        """删除Neo4j数据"""
        try:
            delete_data = json.loads(data)
            
            # 模拟删除操作
            logger.info(f"Would delete data: {delete_data}")
            
            return json.dumps({
                "status": "success",
                "deleted_items": 1,
                "message": "Data deleted successfully"
            }, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to delete Neo4j data. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _generate_create_node_cypher(self, node: GraphNode) -> str:
        """生成创建节点的Cypher语句"""
        properties_str = ", ".join([f"{k}: ${k}" for k in node.properties.keys()])
        return f"CREATE (n:{node.label} {{id: '{node.id}', {properties_str}}})"
    
    def _generate_create_relationship_cypher(self, relationship: GraphRelationship) -> str:
        """生成创建关系的Cypher语句"""
        properties_str = ", ".join([f"{k}: ${k}" for k in relationship.properties.keys()])
        return (
            f"MATCH (a {{id: '{relationship.source_id}'}}), (b {{id: '{relationship.target_id}'}}) "
            f"CREATE (a)-[r:{relationship.relationship_type} {{id: '{relationship.id}', {properties_str}}}]->(b)"
        )


class ElasticsearchStorage(BaseTool):
    """Elasticsearch存储工具"""
    name: str = "elasticsearch_storage"
    description: str = "Store and search data in Elasticsearch."
    
    def __init__(self, config: Optional[MysteryEventConfig] = None):
        """初始化Elasticsearch存储
        
        Args:
            config: 神秘事件配置
        """
        super().__init__()
        self.config = config or MysteryEventConfig()
        self.client = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """初始化Elasticsearch连接"""
        try:
            # 这里应该使用真实的Elasticsearch客户端，但为了演示，我们使用模拟
            # from elasticsearch import Elasticsearch
            # self.client = Elasticsearch(
            #     [self.config.elasticsearch_config["host"]],
            #     http_auth=(self.config.elasticsearch_config["username"], 
            #               self.config.elasticsearch_config["password"])
            # )
            
            # 模拟连接
            self.client = "mock_elasticsearch_client"
            logger.info("Elasticsearch connection initialized (mock)")
            
        except Exception as e:
            logger.error(f"Failed to initialize Elasticsearch connection: {e}")
            self.client = None
    
    def _run(self, operation: str, index: str = "mystery_events", data: str = None, query: str = None) -> str:
        """运行Elasticsearch操作
        
        Args:
            operation: 操作类型 (index, search, update, delete)
            index: 索引名称
            data: JSON格式的数据
            query: 查询语句
            
        Returns:
            JSON格式的操作结果
        """
        try:
            if not self.client:
                return json.dumps({"error": "Elasticsearch connection not available"}, ensure_ascii=False)
            
            if operation == "index":
                return self._index_data(index, data)
            elif operation == "search":
                return self._search_data(index, query)
            elif operation == "update":
                return self._update_data(index, data)
            elif operation == "delete":
                return self._delete_data(index, data)
            else:
                return json.dumps({"error": f"Unknown operation: {operation}"}, ensure_ascii=False)
                
        except Exception as e:
            error_msg = f"Failed to execute Elasticsearch operation. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _index_data(self, index: str, data: str) -> str:
        """索引数据到Elasticsearch"""
        try:
            documents = json.loads(data)
            
            if not isinstance(documents, list):
                documents = [documents]
            
            indexed_docs = []
            for doc in documents:
                # 生成文档ID
                doc_id = doc.get("id") or self._generate_doc_id(doc)
                
                # 添加时间戳
                doc["indexed_at"] = datetime.now().isoformat()
                
                # 在真实实现中，这里会调用client.index()
                logger.info(f"Would index document {doc_id} to index {index}")
                
                indexed_docs.append({
                    "id": doc_id,
                    "index": index,
                    "document": doc
                })
            
            return json.dumps({
                "status": "success",
                "indexed_documents": len(indexed_docs),
                "documents": indexed_docs
            }, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to index data in Elasticsearch. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _search_data(self, index: str, query: str) -> str:
        """搜索Elasticsearch数据"""
        try:
            search_query = json.loads(query) if query else {"match_all": {}}
            
            # 在真实实现中，这里会调用client.search()
            logger.info(f"Would search index {index} with query: {search_query}")
            
            # 模拟搜索结果
            mock_hits = [
                {
                    "_id": "doc_001",
                    "_score": 1.0,
                    "_source": {
                        "title": "UFO目击报告",
                        "description": "在北京上空发现不明飞行物",
                        "event_type": "UFO",
                        "location": {"lat": 39.9042, "lon": 116.4074},
                        "timestamp": "2023-01-15T20:30:00Z"
                    }
                },
                {
                    "_id": "doc_002",
                    "_score": 0.8,
                    "_source": {
                        "title": "神秘光球现象",
                        "description": "多名目击者报告看到发光球体",
                        "event_type": "UFO",
                        "location": {"lat": 39.9000, "lon": 116.4000},
                        "timestamp": "2023-01-16T21:00:00Z"
                    }
                }
            ]
            
            return json.dumps({
                "status": "success",
                "total_hits": len(mock_hits),
                "max_score": max(hit["_score"] for hit in mock_hits) if mock_hits else 0,
                "hits": mock_hits
            }, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to search Elasticsearch data. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _update_data(self, index: str, data: str) -> str:
        """更新Elasticsearch数据"""
        try:
            update_data = json.loads(data)
            doc_id = update_data.get("id")
            
            if not doc_id:
                return json.dumps({"error": "Document ID is required for update"}, ensure_ascii=False)
            
            # 在真实实现中，这里会调用client.update()
            logger.info(f"Would update document {doc_id} in index {index}")
            
            return json.dumps({
                "status": "success",
                "updated_document": doc_id,
                "message": "Document updated successfully"
            }, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to update Elasticsearch data. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _delete_data(self, index: str, data: str) -> str:
        """删除Elasticsearch数据"""
        try:
            delete_data = json.loads(data)
            doc_id = delete_data.get("id")
            
            if not doc_id:
                return json.dumps({"error": "Document ID is required for deletion"}, ensure_ascii=False)
            
            # 在真实实现中，这里会调用client.delete()
            logger.info(f"Would delete document {doc_id} from index {index}")
            
            return json.dumps({
                "status": "success",
                "deleted_document": doc_id,
                "message": "Document deleted successfully"
            }, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to delete Elasticsearch data. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _generate_doc_id(self, doc: Dict[str, Any]) -> str:
        """生成文档ID"""
        # 基于文档内容生成哈希ID
        content = json.dumps(doc, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(content.encode('utf-8')).hexdigest()


class GraphStorageManager:
    """图存储管理器"""
    
    def __init__(self, config: Optional[MysteryEventConfig] = None):
        """初始化图存储管理器
        
        Args:
            config: 神秘事件配置
        """
        self.config = config or MysteryEventConfig()
        self.neo4j_storage = Neo4jStorage(config)
        self.elasticsearch_storage = ElasticsearchStorage(config)
    
    def store_mystery_events(self, events_data: str) -> Dict[str, Any]:
        """存储神秘事件数据
        
        Args:
            events_data: JSON格式的事件数据
            
        Returns:
            存储结果
        """
        try:
            events = json.loads(events_data)
            
            # 转换为图数据格式
            graph_data = self._convert_to_graph_data(events)
            
            # 存储到Neo4j
            neo4j_result = self.neo4j_storage._store_data(json.dumps(graph_data, ensure_ascii=False))
            
            # 存储到Elasticsearch
            es_result = self.elasticsearch_storage._index_data("mystery_events", events_data)
            
            return {
                "neo4j_result": json.loads(neo4j_result),
                "elasticsearch_result": json.loads(es_result)
            }
            
        except Exception as e:
            logger.error(f"Failed to store mystery events: {e}")
            return {"error": str(e)}
    
    def _convert_to_graph_data(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """将事件数据转换为图数据格式"""
        nodes = []
        relationships = []
        
        for event in events:
            # 创建事件节点
            event_node = {
                "id": event.get("id", f"event_{len(nodes)}"),
                "label": "Event",
                "node_type": "event",
                "properties": {
                    "title": event.get("title", ""),
                    "description": event.get("description", ""),
                    "event_type": event.get("event_type", ""),
                    "timestamp": event.get("timestamp", ""),
                    "credibility_score": event.get("credibility_score", 0.0)
                }
            }
            nodes.append(event_node)
            
            # 创建位置节点和关系
            if "location" in event and event["location"]:
                location_id = f"location_{event['id']}"
                location_node = {
                    "id": location_id,
                    "label": "Location",
                    "node_type": "location",
                    "properties": {
                        "latitude": event["location"].get("lat", 0),
                        "longitude": event["location"].get("lon", 0),
                        "address": event.get("address", ""),
                        "country": event.get("country", ""),
                        "region": event.get("region", "")
                    }
                }
                nodes.append(location_node)
                
                # 创建事件-位置关系
                location_rel = {
                    "id": f"rel_{event_node['id']}_{location_id}",
                    "source_id": event_node["id"],
                    "target_id": location_id,
                    "relationship_type": "OCCURRED_AT",
                    "properties": {
                        "confidence": 1.0
                    }
                }
                relationships.append(location_rel)
            
            # 创建人物节点和关系
            if "witnesses" in event:
                for witness in event["witnesses"]:
                    witness_id = f"person_{witness.get('name', 'unknown')}"
                    witness_node = {
                        "id": witness_id,
                        "label": "Person",
                        "node_type": "person",
                        "properties": {
                            "name": witness.get("name", ""),
                            "role": "witness",
                            "credibility": witness.get("credibility", 0.5)
                        }
                    }
                    nodes.append(witness_node)
                    
                    # 创建目击关系
                    witness_rel = {
                        "id": f"rel_{witness_id}_{event_node['id']}",
                        "source_id": witness_id,
                        "target_id": event_node["id"],
                        "relationship_type": "WITNESSED",
                        "properties": {
                            "confidence": witness.get("credibility", 0.5)
                        }
                    }
                    relationships.append(witness_rel)
        
        return {
            "nodes": nodes,
            "relationships": relationships,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_nodes": len(nodes),
                "total_relationships": len(relationships)
            }
        }


@tool
@log_io
def store_in_neo4j(
    operation: str,
    data: Optional[str] = None,
    query: Optional[str] = None
) -> str:
    """在Neo4j图数据库中存储或查询数据
    
    Args:
        operation: 操作类型 (store, query, update, delete)
        data: JSON格式的数据
        query: Cypher查询语句
    
    Returns:
        JSON格式的操作结果
    """
    try:
        storage = Neo4jStorage()
        return storage._run(operation, data, query)
    except Exception as e:
        error_msg = f"Failed to execute Neo4j operation. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def store_in_elasticsearch(
    operation: str,
    index: str = "mystery_events",
    data: Optional[str] = None,
    query: Optional[str] = None
) -> str:
    """在Elasticsearch中存储或搜索数据
    
    Args:
        operation: 操作类型 (index, search, update, delete)
        index: 索引名称
        data: JSON格式的数据
        query: 查询语句
    
    Returns:
        JSON格式的操作结果
    """
    try:
        storage = ElasticsearchStorage()
        return storage._run(operation, index, data, query)
    except Exception as e:
        error_msg = f"Failed to execute Elasticsearch operation. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def store_mystery_events_graph(
    events_data: str
) -> str:
    """将神秘事件数据存储到图数据库和搜索引擎
    
    Args:
        events_data: JSON格式的事件数据列表
    
    Returns:
        JSON格式的存储结果
    """
    try:
        manager = GraphStorageManager()
        result = manager.store_mystery_events(events_data)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Failed to store mystery events in graph storage. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def query_related_events(
    event_id: str,
    relationship_types: Optional[List[str]] = None,
    max_depth: int = 2
) -> str:
    """查询与指定事件相关的其他事件
    
    Args:
        event_id: 事件ID
        relationship_types: 关系类型列表
        max_depth: 最大查询深度
    
    Returns:
        JSON格式的相关事件
    """
    try:
        # 构建Cypher查询
        if relationship_types:
            rel_filter = "|".join(relationship_types)
            cypher_query = (
                f"MATCH (e:Event {{id: '{event_id}'}})-[r:{rel_filter}*1..{max_depth}]-(related) "
                "RETURN related, r"
            )
        else:
            cypher_query = (
                f"MATCH (e:Event {{id: '{event_id}'}})-[r*1..{max_depth}]-(related) "
                "RETURN related, r"
            )
        
        storage = Neo4jStorage()
        result = storage._query_data(cypher_query)
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to query related events. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def search_events_by_criteria(
    criteria: str,
    index: str = "mystery_events"
) -> str:
    """根据条件搜索神秘事件
    
    Args:
        criteria: JSON格式的搜索条件
        index: 搜索索引
    
    Returns:
        JSON格式的搜索结果
    """
    try:
        search_criteria = json.loads(criteria)
        
        # 构建Elasticsearch查询
        query = {
            "bool": {
                "must": []
            }
        }
        
        # 添加搜索条件
        if "event_type" in search_criteria:
            query["bool"]["must"].append({
                "term": {"event_type": search_criteria["event_type"]}
            })
        
        if "location" in search_criteria:
            location = search_criteria["location"]
            if "radius_km" in location:
                query["bool"]["must"].append({
                    "geo_distance": {
                        "distance": f"{location['radius_km']}km",
                        "location": {
                            "lat": location["lat"],
                            "lon": location["lon"]
                        }
                    }
                })
        
        if "date_range" in search_criteria:
            date_range = search_criteria["date_range"]
            query["bool"]["must"].append({
                "range": {
                    "timestamp": {
                        "gte": date_range.get("start"),
                        "lte": date_range.get("end")
                    }
                }
            })
        
        if "keywords" in search_criteria:
            query["bool"]["must"].append({
                "multi_match": {
                    "query": search_criteria["keywords"],
                    "fields": ["title", "description"]
                }
            })
        
        storage = ElasticsearchStorage()
        result = storage._search_data(index, json.dumps(query))
        
        return result
        
    except Exception as e:
        error_msg = f"Failed to search events by criteria. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)