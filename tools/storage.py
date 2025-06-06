#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

"""
Storage tools for mysterious event research.
Provides Neo4j graph database and Elasticsearch storage tools.
"""

import logging
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool

from .graph_storage import (
    store_in_neo4j,
    store_in_elasticsearch,
    store_mystery_events_graph,
    query_related_events,
    search_events_by_criteria
)
from .decorators import mystery_tool

logger = logging.getLogger(__name__)


@mystery_tool
@tool
def get_graph_storage_tool(
    events: List[Dict[str, Any]],
    storage_type: str = "both"
) -> Dict[str, Any]:
    """Get graph storage tool for storing mystery events in graph databases.
    
    Args:
        events: List of mystery events to store
        storage_type: Type of storage (neo4j, elasticsearch, both)
        
    Returns:
        Dict containing storage operation results
    """
    try:
        if storage_type == "neo4j":
            result = store_in_neo4j(events)
        elif storage_type == "elasticsearch":
            result = store_in_elasticsearch(events)
        else:
            result = store_mystery_events_graph(events)
            
        logger.info(f"Graph storage completed for {len(events)} events using {storage_type}")
        return result
    except Exception as e:
        logger.error(f"Error in graph storage: {str(e)}")
        return {"error": str(e), "stored_count": 0}


@mystery_tool
@tool
def get_neo4j_tool(
    operation: str,
    data: Optional[Dict[str, Any]] = None,
    query_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get Neo4j database tool for graph operations.
    
    Args:
        operation: Operation type (store, query, update, delete)
        data: Data for store/update operations
        query_params: Parameters for query operations
        
    Returns:
        Dict containing operation results
    """
    try:
        if operation == "store" and data:
            events = data.get("events", [])
            result = store_in_neo4j(events)
        elif operation == "query" and query_params:
            result = query_related_events(
                event_id=query_params.get("event_id"),
                event_type=query_params.get("event_type"),
                location=query_params.get("location"),
                time_range=query_params.get("time_range")
            )
        else:
            result = {"error": "Invalid operation or missing parameters"}
            
        logger.info(f"Neo4j operation '{operation}' completed")
        return result
    except Exception as e:
        logger.error(f"Error in Neo4j operation: {str(e)}")
        return {"error": str(e)}


@mystery_tool
@tool
def get_elasticsearch_tool(
    operation: str,
    data: Optional[Dict[str, Any]] = None,
    search_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get Elasticsearch tool for document search and storage.
    
    Args:
        operation: Operation type (store, search, update, delete)
        data: Data for store/update operations
        search_params: Parameters for search operations
        
    Returns:
        Dict containing operation results
    """
    try:
        if operation == "store" and data:
            events = data.get("events", [])
            result = store_in_elasticsearch(events)
        elif operation == "search" and search_params:
            result = search_events_by_criteria(
                keywords=search_params.get("keywords"),
                event_type=search_params.get("event_type"),
                location=search_params.get("location"),
                date_range=search_params.get("date_range"),
                credibility_threshold=search_params.get("credibility_threshold")
            )
        else:
            result = {"error": "Invalid operation or missing parameters"}
            
        logger.info(f"Elasticsearch operation '{operation}' completed")
        return result
    except Exception as e:
        logger.error(f"Error in Elasticsearch operation: {str(e)}")
        return {"error": str(e)}


@mystery_tool
@tool
def batch_storage_tool(
    events: List[Dict[str, Any]],
    storage_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Batch storage tool for efficiently storing large numbers of events.
    
    Args:
        events: List of mystery events to store
        storage_config: Configuration for storage operations
        
    Returns:
        Dict containing batch storage results
    """
    results = {
        "total_events": len(events),
        "neo4j_results": None,
        "elasticsearch_results": None,
        "errors": [],
        "success_count": 0
    }
    
    try:
        batch_size = storage_config.get("batch_size", 100)
        enable_neo4j = storage_config.get("enable_neo4j", True)
        enable_elasticsearch = storage_config.get("enable_elasticsearch", True)
        
        # Process events in batches
        for i in range(0, len(events), batch_size):
            batch = events[i:i + batch_size]
            
            # Store in Neo4j
            if enable_neo4j:
                try:
                    neo4j_result = store_in_neo4j(batch)
                    if results["neo4j_results"] is None:
                        results["neo4j_results"] = {"stored_count": 0, "relationships_count": 0}
                    results["neo4j_results"]["stored_count"] += neo4j_result.get("stored_count", 0)
                    results["neo4j_results"]["relationships_count"] += neo4j_result.get("relationships_count", 0)
                except Exception as e:
                    results["errors"].append(f"Neo4j batch {i//batch_size + 1}: {str(e)}")
            
            # Store in Elasticsearch
            if enable_elasticsearch:
                try:
                    es_result = store_in_elasticsearch(batch)
                    if results["elasticsearch_results"] is None:
                        results["elasticsearch_results"] = {"indexed_count": 0}
                    results["elasticsearch_results"]["indexed_count"] += es_result.get("indexed_count", 0)
                except Exception as e:
                    results["errors"].append(f"Elasticsearch batch {i//batch_size + 1}: {str(e)}")
        
        # Calculate success count
        neo4j_count = results.get("neo4j_results", {}).get("stored_count", 0)
        es_count = results.get("elasticsearch_results", {}).get("indexed_count", 0)
        results["success_count"] = max(neo4j_count, es_count)
        
        logger.info(f"Batch storage completed: {results['success_count']}/{len(events)} events stored")
        return results
        
    except Exception as e:
        logger.error(f"Error in batch storage: {str(e)}")
        results["errors"].append(str(e))
        return results


@mystery_tool
@tool
def query_storage_tool(
    query_type: str,
    query_params: Dict[str, Any]
) -> Dict[str, Any]:
    """Query storage tool for retrieving stored mystery events.
    
    Args:
        query_type: Type of query (related_events, search_events, graph_query)
        query_params: Parameters for the query
        
    Returns:
        Dict containing query results
    """
    try:
        if query_type == "related_events":
            result = query_related_events(
                event_id=query_params.get("event_id"),
                event_type=query_params.get("event_type"),
                location=query_params.get("location"),
                time_range=query_params.get("time_range")
            )
        elif query_type == "search_events":
            result = search_events_by_criteria(
                keywords=query_params.get("keywords"),
                event_type=query_params.get("event_type"),
                location=query_params.get("location"),
                date_range=query_params.get("date_range"),
                credibility_threshold=query_params.get("credibility_threshold")
            )
        else:
            result = {"error": f"Unknown query type: {query_type}"}
            
        logger.info(f"Query '{query_type}' completed")
        return result
    except Exception as e:
        logger.error(f"Error in query storage: {str(e)}")
        return {"error": str(e), "results": []}