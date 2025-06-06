#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

"""
Retriever tool for mysterious event research.
Provides document retrieval and knowledge base search capabilities.
"""

import logging
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool

from .decorators import mystery_tool

logger = logging.getLogger(__name__)


class MysteryRetriever:
    """Retriever for mystery research knowledge base."""
    
    def __init__(self):
        self.knowledge_base = {
            "ufo_sightings": [
                {
                    "id": "ufo_001",
                    "title": "Phoenix Lights Incident",
                    "description": "Mass UFO sighting over Phoenix, Arizona in 1997",
                    "location": "Phoenix, Arizona, USA",
                    "date": "1997-03-13",
                    "witnesses": 1000,
                    "credibility": 0.8,
                    "tags": ["mass_sighting", "lights", "triangle"]
                },
                {
                    "id": "ufo_002",
                    "title": "Roswell Incident",
                    "description": "Alleged UFO crash and recovery in Roswell, New Mexico",
                    "location": "Roswell, New Mexico, USA",
                    "date": "1947-07-08",
                    "witnesses": 50,
                    "credibility": 0.6,
                    "tags": ["crash", "recovery", "government"]
                }
            ],
            "cryptid_encounters": [
                {
                    "id": "cryptid_001",
                    "title": "Bigfoot Sighting in Pacific Northwest",
                    "description": "Large bipedal creature spotted in Washington forest",
                    "location": "Olympic National Forest, Washington, USA",
                    "date": "2020-08-15",
                    "witnesses": 3,
                    "credibility": 0.5,
                    "tags": ["bigfoot", "forest", "footprints"]
                }
            ],
            "paranormal_events": [
                {
                    "id": "paranormal_001",
                    "title": "Amityville Horror",
                    "description": "Alleged haunting of the Lutz family home",
                    "location": "Amityville, New York, USA",
                    "date": "1975-12-18",
                    "witnesses": 6,
                    "credibility": 0.4,
                    "tags": ["haunting", "poltergeist", "family"]
                }
            ]
        }
    
    def search(self, query: str, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant documents.
        
        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of relevant documents
        """
        results = []
        query_lower = query.lower()
        
        # Determine which categories to search
        categories_to_search = [category] if category else self.knowledge_base.keys()
        
        for cat in categories_to_search:
            if cat not in self.knowledge_base:
                continue
                
            for doc in self.knowledge_base[cat]:
                # Simple text matching (in real implementation, use vector similarity)
                score = 0
                
                # Check title
                if query_lower in doc["title"].lower():
                    score += 0.5
                
                # Check description
                if query_lower in doc["description"].lower():
                    score += 0.3
                
                # Check location
                if query_lower in doc["location"].lower():
                    score += 0.2
                
                # Check tags
                for tag in doc.get("tags", []):
                    if query_lower in tag.lower():
                        score += 0.1
                
                if score > 0:
                    result_doc = doc.copy()
                    result_doc["relevance_score"] = score
                    result_doc["category"] = cat
                    results.append(result_doc)
        
        # Sort by relevance score and limit results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]
    
    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a document by its ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        for category, docs in self.knowledge_base.items():
            for doc in docs:
                if doc["id"] == doc_id:
                    result_doc = doc.copy()
                    result_doc["category"] = category
                    return result_doc
        return None
    
    def get_related(self, doc_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get documents related to the given document.
        
        Args:
            doc_id: Reference document ID
            limit: Maximum number of related documents
            
        Returns:
            List of related documents
        """
        reference_doc = self.get_by_id(doc_id)
        if not reference_doc:
            return []
        
        related = []
        ref_location = reference_doc["location"].lower()
        ref_tags = [tag.lower() for tag in reference_doc.get("tags", [])]
        
        for category, docs in self.knowledge_base.items():
            for doc in docs:
                if doc["id"] == doc_id:
                    continue
                
                similarity_score = 0
                
                # Location similarity
                if ref_location in doc["location"].lower():
                    similarity_score += 0.4
                
                # Tag similarity
                doc_tags = [tag.lower() for tag in doc.get("tags", [])]
                common_tags = set(ref_tags) & set(doc_tags)
                similarity_score += len(common_tags) * 0.2
                
                # Date proximity (simplified)
                try:
                    from datetime import datetime
                    ref_date = datetime.fromisoformat(reference_doc["date"])
                    doc_date = datetime.fromisoformat(doc["date"])
                    date_diff = abs((ref_date - doc_date).days)
                    if date_diff < 365:  # Within a year
                        similarity_score += 0.1
                except:
                    pass
                
                if similarity_score > 0:
                    result_doc = doc.copy()
                    result_doc["similarity_score"] = similarity_score
                    result_doc["category"] = category
                    related.append(result_doc)
        
        # Sort by similarity and limit
        related.sort(key=lambda x: x["similarity_score"], reverse=True)
        return related[:limit]


# Global retriever instance
_retriever = MysteryRetriever()


@mystery_tool
@tool
def get_retriever_tool(
    query: str,
    category: Optional[str] = None,
    limit: int = 10,
    min_credibility: float = 0.0
) -> Dict[str, Any]:
    """Retrieve documents from the mystery research knowledge base.
    
    Args:
        query: Search query
        category: Optional category filter (ufo_sightings, cryptid_encounters, paranormal_events)
        limit: Maximum number of results
        min_credibility: Minimum credibility score filter
        
    Returns:
        Dict containing search results
    """
    try:
        results = _retriever.search(query, category, limit)
        
        # Apply credibility filter
        if min_credibility > 0:
            results = [r for r in results if r.get("credibility", 0) >= min_credibility]
        
        logger.info(f"Retrieved {len(results)} documents for query: {query}")
        return {
            "query": query,
            "category": category,
            "total_results": len(results),
            "results": results,
            "filters": {
                "min_credibility": min_credibility,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error in get_retriever_tool: {str(e)}")
        return {
            "query": query,
            "error": str(e),
            "results": []
        }


@mystery_tool
@tool
def get_document_by_id(
    doc_id: str
) -> Dict[str, Any]:
    """Retrieve a specific document by its ID.
    
    Args:
        doc_id: Document ID to retrieve
        
    Returns:
        Dict containing the document or error
    """
    try:
        document = _retriever.get_by_id(doc_id)
        
        if document:
            logger.info(f"Retrieved document: {doc_id}")
            return {
                "success": True,
                "document": document
            }
        else:
            return {
                "success": False,
                "error": f"Document not found: {doc_id}"
            }
            
    except Exception as e:
        logger.error(f"Error retrieving document {doc_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@mystery_tool
@tool
def get_related_documents(
    doc_id: str,
    limit: int = 5
) -> Dict[str, Any]:
    """Get documents related to the specified document.
    
    Args:
        doc_id: Reference document ID
        limit: Maximum number of related documents
        
    Returns:
        Dict containing related documents
    """
    try:
        related_docs = _retriever.get_related(doc_id, limit)
        
        logger.info(f"Found {len(related_docs)} related documents for {doc_id}")
        return {
            "reference_document_id": doc_id,
            "total_related": len(related_docs),
            "related_documents": related_docs
        }
        
    except Exception as e:
        logger.error(f"Error getting related documents for {doc_id}: {str(e)}")
        return {
            "reference_document_id": doc_id,
            "error": str(e),
            "related_documents": []
        }


@mystery_tool
@tool
def advanced_search_tool(
    filters: Dict[str, Any]
) -> Dict[str, Any]:
    """Perform advanced search with multiple filters.
    
    Args:
        filters: Dictionary of search filters
        
    Returns:
        Dict containing filtered search results
    """
    try:
        query = filters.get("query", "")
        category = filters.get("category")
        location = filters.get("location")
        date_range = filters.get("date_range", {})
        min_credibility = filters.get("min_credibility", 0.0)
        min_witnesses = filters.get("min_witnesses", 0)
        tags = filters.get("tags", [])
        limit = filters.get("limit", 10)
        
        # Start with basic search
        results = _retriever.search(query, category, limit * 2)  # Get more to filter
        
        # Apply additional filters
        filtered_results = []
        for result in results:
            # Credibility filter
            if result.get("credibility", 0) < min_credibility:
                continue
            
            # Witnesses filter
            if result.get("witnesses", 0) < min_witnesses:
                continue
            
            # Location filter
            if location and location.lower() not in result.get("location", "").lower():
                continue
            
            # Tags filter
            if tags:
                result_tags = [tag.lower() for tag in result.get("tags", [])]
                if not any(tag.lower() in result_tags for tag in tags):
                    continue
            
            # Date range filter (simplified)
            if date_range:
                start_date = date_range.get("start")
                end_date = date_range.get("end")
                result_date = result.get("date")
                
                if start_date and result_date and result_date < start_date:
                    continue
                if end_date and result_date and result_date > end_date:
                    continue
            
            filtered_results.append(result)
        
        # Limit final results
        filtered_results = filtered_results[:limit]
        
        logger.info(f"Advanced search returned {len(filtered_results)} results")
        return {
            "filters_applied": filters,
            "total_results": len(filtered_results),
            "results": filtered_results
        }
        
    except Exception as e:
        logger.error(f"Error in advanced_search_tool: {str(e)}")
        return {
            "filters_applied": filters,
            "error": str(e),
            "results": []
        }