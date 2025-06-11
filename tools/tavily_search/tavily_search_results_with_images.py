# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

import json
import logging
from typing import Any, Dict, List, Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

logger = logging.getLogger(__name__)


class TavilySearchInput(BaseModel):
    """Input for Tavily search tool."""
    query: str = Field(description="The search query")
    max_results: int = Field(default=5, description="Maximum number of results to return")
    include_images: bool = Field(default=True, description="Whether to include images in results")
    include_answer: bool = Field(default=True, description="Whether to include AI-generated answer")
    search_depth: str = Field(default="basic", description="Search depth: 'basic' or 'advanced'")


class TavilySearchResultsWithImages(BaseTool):
    """Tavily search tool with image support."""
    
    name: str = "tavily_search_results_with_images"
    description: str = (
        "A search engine optimized for comprehensive, accurate, and trusted results. "
        "Useful for when you need to answer questions about current events, news, "
        "or general information. Can include images in search results."
    )
    args_schema: Type[BaseModel] = TavilySearchInput
    
    api_key: Optional[str] = Field(default=None, description="Tavily API key")
    client: Optional[Any] = Field(default=None, exclude=True)
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.api_key = api_key
        if TavilyClient and api_key:
            self.client = TavilyClient(api_key=api_key)
        else:
            self.client = None
            logger.warning("Tavily client not available. Install tavily-python or provide API key.")
    
    def _run(
        self,
        query: str,
        max_results: int = 5,
        include_images: bool = True,
        include_answer: bool = True,
        search_depth: str = "basic",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Run the Tavily search tool."""
        if not self.client:
            return json.dumps({
                "error": "Tavily client not available. Please install tavily-python and provide API key.",
                "results": [],
                "images": [],
                "answer": ""
            })
        
        try:
            # Perform the search
            response = self.client.search(
                query=query,
                max_results=max_results,
                include_images=include_images,
                include_answer=include_answer,
                search_depth=search_depth
            )
            
            # Format the response
            formatted_results = {
                "query": query,
                "results": [],
                "images": response.get("images", []) if include_images else [],
                "answer": response.get("answer", "") if include_answer else ""
            }
            
            # Process search results
            for result in response.get("results", []):
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0),
                    "published_date": result.get("published_date", "")
                }
                formatted_results["results"].append(formatted_result)
            
            return json.dumps(formatted_results, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error in Tavily search: {e}")
            return json.dumps({
                "error": f"Search failed: {str(e)}",
                "results": [],
                "images": [],
                "answer": ""
            })
    
    async def _arun(
        self,
        query: str,
        max_results: int = 5,
        include_images: bool = True,
        include_answer: bool = True,
        search_depth: str = "basic",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Async version of the search tool."""
        # For now, just call the sync version
        # In a real implementation, you might want to use aiohttp or similar
        return self._run(
            query=query,
            max_results=max_results,
            include_images=include_images,
            include_answer=include_answer,
            search_depth=search_depth,
            run_manager=run_manager
        )


# Create a default instance for backward compatibility
def create_tavily_search_tool(api_key: Optional[str] = None) -> TavilySearchResultsWithImages:
    """Create a Tavily search tool instance."""
    return TavilySearchResultsWithImages(api_key=api_key)