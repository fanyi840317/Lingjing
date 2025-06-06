# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Dict, List, Any, Optional

from langchain_community.tools import BraveSearch, DuckDuckGoSearchResults
from langchain_community.tools.arxiv import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper, BraveSearchWrapper
from langchain_core.tools import BaseTool, tool

from config import SearchEngine, SELECTED_SEARCH_ENGINE, RAGProvider, SELECTED_RAG_PROVIDER
from config.mystery_config import MysteryEventType, DataSourceType, MysteryEventConfig
from tools.tavily_search.tavily_search_results_with_images import (
    TavilySearchResultsWithImages,
)
from tools.decorators import create_logged_tool, log_io

logger = logging.getLogger(__name__)

# Create logged versions of the search tools
LoggedTavilySearch = create_logged_tool(TavilySearchResultsWithImages)
LoggedDuckDuckGoSearch = create_logged_tool(DuckDuckGoSearchResults)
LoggedBraveSearch = create_logged_tool(BraveSearch)
LoggedArxivSearch = create_logged_tool(ArxivQueryRun)


class AcademicSearch(BaseTool):
    """Tool for searching academic databases for mystery research."""
    name = "academic_search"
    description = "Search academic databases for scholarly articles and papers related to mysterious events."
    
    def __init__(self, max_results: int = 5, databases: List[str] = None):
        """Initialize the academic search tool.
        
        Args:
            max_results: Maximum number of results to return
            databases: List of academic databases to search (e.g., "cnki", "wanfang", "webofscience")
        """
        super().__init__()
        self.max_results = max_results
        self.databases = databases or ["arxiv", "cnki", "wanfang"]
        
        # API keys and configurations
        self.api_keys = {
            "cnki": os.getenv("CNKI_API_KEY", ""),
            "wanfang": os.getenv("WANFANG_API_KEY", ""),
            "webofscience": os.getenv("WEBOFSCIENCE_API_KEY", ""),
        }
    
    def _run(self, query: str) -> List[Dict[str, Any]]:
        """Run the academic search.
        
        Args:
            query: The search query
            
        Returns:
            List of academic search results
        """
        logger.info(f"Searching academic databases: {self.databases} for: {query}")
        
        results = []
        
        # Use ArxivQueryRun for arxiv searches
        if "arxiv" in self.databases:
            try:
                arxiv_tool = LoggedArxivSearch(
                    name="arxiv_search",
                    api_wrapper=ArxivAPIWrapper(
                        top_k_results=self.max_results,
                        load_max_docs=self.max_results,
                        load_all_available_meta=True,
                    ),
                )
                arxiv_results = arxiv_tool.invoke(query)
                
                # Parse the results
                if isinstance(arxiv_results, str):
                    try:
                        parsed_results = json.loads(arxiv_results)
                        if isinstance(parsed_results, list):
                            for result in parsed_results:
                                results.append({
                                    "title": result.get("title", ""),
                                    "authors": result.get("authors", ""),
                                    "summary": result.get("summary", ""),
                                    "published": result.get("published", ""),
                                    "url": result.get("entry_id", ""),
                                    "source": "arxiv",
                                    "source_type": "academic"
                                })
                    except json.JSONDecodeError:
                        # Handle as text
                        results.append({
                            "title": "Arxiv Search Results",
                            "content": arxiv_results,
                            "source": "arxiv",
                            "source_type": "academic"
                        })
            except Exception as e:
                logger.error(f"Error searching arxiv: {e}")
        
        # Simulate other academic database searches
        # In a real implementation, these would connect to actual APIs
        for db in self.databases:
            if db == "arxiv":
                continue  # Already handled above
                
            if db == "cnki" and self.api_keys["cnki"]:
                # Simulated CNKI search
                results.append({
                    "title": f"CNKI Search Results for {query}",
                    "content": f"Simulated CNKI academic search results for: {query}",
                    "source": "cnki",
                    "source_type": "academic"
                })
            
            if db == "wanfang" and self.api_keys["wanfang"]:
                # Simulated Wanfang search
                results.append({
                    "title": f"Wanfang Search Results for {query}",
                    "content": f"Simulated Wanfang academic search results for: {query}",
                    "source": "wanfang",
                    "source_type": "academic"
                })
                
            if db == "webofscience" and self.api_keys["webofscience"]:
                # Simulated Web of Science search
                results.append({
                    "title": f"Web of Science Search Results for {query}",
                    "content": f"Simulated Web of Science academic search results for: {query}",
                    "source": "webofscience",
                    "source_type": "academic"
                })
        
        return results[:self.max_results]


class MysterySearch(BaseTool):
    """Tool for searching mystery-specific sources and databases."""
    name = "mystery_search"
    description = "Search for information about mysterious events from specialized sources."
    
    def __init__(self, max_results: int = 5, event_types: List[str] = None):
        """Initialize the mystery search tool.
        
        Args:
            max_results: Maximum number of results to return
            event_types: List of mystery event types to focus on
        """
        super().__init__()
        self.max_results = max_results
        self.event_types = event_types or list(MysteryEventType.__members__.keys())
        self.config = MysteryEventConfig()
        
        # API keys and configurations
        self.api_keys = {
            "mufon": os.getenv("MUFON_API_KEY", ""),
            "paranormal_db": os.getenv("PARANORMAL_DB_API_KEY", ""),
        }
    
    def _run(self, query: str) -> List[Dict[str, Any]]:
        """Run the mystery search.
        
        Args:
            query: The search query
            
        Returns:
            List of mystery search results
        """
        logger.info(f"Searching mystery sources for: {query}")
        
        results = []
        
        # Enhance query with mystery keywords based on detected event type
        enhanced_query = self._enhance_query(query)
        
        # First use regular web search as fallback
        web_results = get_web_search_tool(self.max_results).invoke(enhanced_query)
        
        # Parse web results
        if isinstance(web_results, str):
            try:
                parsed_results = json.loads(web_results)
                if isinstance(parsed_results, list):
                    for result in parsed_results:
                        results.append({
                            "title": result.get("title", ""),
                            "content": result.get("content", ""),
                            "url": result.get("url", ""),
                            "source": "web_search",
                            "source_type": "web"
                        })
            except json.JSONDecodeError:
                # Handle as text
                results.append({
                    "title": "Web Search Results",
                    "content": web_results,
                    "source": "web_search",
                    "source_type": "web"
                })
        
        # Simulate specialized mystery database searches
        # In a real implementation, these would connect to actual APIs
        
        # Check if query is related to UFOs
        if any(keyword in query.lower() for keyword in self.config.keywords.get("UFO", [])):
            if self.api_keys["mufon"]:
                # Simulated MUFON database search
                results.append({
                    "title": "MUFON UFO Sighting Report",
                    "content": f"Simulated MUFON database search results for UFO query: {query}",
                    "source": "mufon",
                    "source_type": "specialized_database"
                })
        
        # Check if query is related to paranormal events
        if any(keyword in query.lower() for keyword in self.config.keywords.get("PARANORMAL", [])):
            if self.api_keys["paranormal_db"]:
                # Simulated paranormal database search
                results.append({
                    "title": "Paranormal Activity Database Report",
                    "content": f"Simulated paranormal database search results for: {query}",
                    "source": "paranormal_db",
                    "source_type": "specialized_database"
                })
        
        return results[:self.max_results]
    
    def _enhance_query(self, query: str) -> str:
        """Enhance the query with mystery-specific keywords."""
        # Detect event type
        event_type = None
        for et, keywords in self.config.keywords.items():
            if any(keyword.lower() in query.lower() for keyword in keywords):
                event_type = et
                break
        
        if not event_type:
            return query
        
        # Add relevant keywords to the query
        enhanced_terms = []
        if event_type in self.config.keywords:
            # Add up to 2 additional keywords
            enhanced_terms = self.config.keywords[event_type][:2]
        
        enhanced_query = f"{query} {' '.join(enhanced_terms)}"
        logger.info(f"Enhanced query: {enhanced_query}")
        return enhanced_query


# Get the selected search tool
def get_web_search_tool(max_search_results: int):
    """Get the configured web search tool."""
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        return LoggedTavilySearch(
            name="web_search",
            max_results=max_search_results,
            include_raw_content=True,
            include_images=True,
            include_image_descriptions=True,
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.DUCKDUCKGO.value:
        return LoggedDuckDuckGoSearch(name="web_search", max_results=max_search_results)
    elif SELECTED_SEARCH_ENGINE == SearchEngine.BRAVE_SEARCH.value:
        return LoggedBraveSearch(
            name="web_search",
            search_wrapper=BraveSearchWrapper(
                api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
                search_kwargs={"count": max_search_results},
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.ARXIV.value:
        return LoggedArxivSearch(
            name="web_search",
            api_wrapper=ArxivAPIWrapper(
                top_k_results=max_search_results,
                load_max_docs=max_search_results,
                load_all_available_meta=True,
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.MYSTERY_SEARCH.value:
        return MysterySearch(max_results=max_search_results)
    elif SELECTED_SEARCH_ENGINE == SearchEngine.ACADEMIC_SEARCH.value:
        return AcademicSearch(max_results=max_search_results)
    else:
        raise ValueError(f"Unsupported search engine: {SELECTED_SEARCH_ENGINE}")


def get_academic_search_tool(max_search_results: int = 5, databases: List[str] = None):
    """Get the academic search tool."""
    return AcademicSearch(max_results=max_search_results, databases=databases)


def get_mystery_search_tool(max_search_results: int = 5, event_types: List[str] = None):
    """Get the mystery search tool."""
    return MysterySearch(max_results=max_search_results, event_types=event_types)


@tool
@log_io
def search_academic_databases(
    query: str,
    databases: Optional[List[str]] = None,
    max_results: int = 5
) -> str:
    """Search academic databases for scholarly articles and papers."""
    try:
        academic_search = AcademicSearch(max_results=max_results, databases=databases)
        results = academic_search._run(query)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Failed to search academic databases. Error: {repr(e)}"
        logger.error(error_msg)
        return error_msg


@tool
@log_io
def search_mystery_sources(
    query: str,
    event_types: Optional[List[str]] = None,
    max_results: int = 5
) -> str:
    """Search mystery-specific sources and databases."""
    try:
        mystery_search = MysterySearch(max_results=max_results, event_types=event_types)
        results = mystery_search._run(query)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        error_msg = f"Failed to search mystery sources. Error: {repr(e)}"
        logger.error(error_msg)
        return error_msg