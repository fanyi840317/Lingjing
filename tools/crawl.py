#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

"""
Web crawling tool for mysterious event research.
Provides web content extraction and processing capabilities.
"""

import logging
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse
from langchain_core.tools import tool

from .decorators import mystery_tool

logger = logging.getLogger(__name__)


class MysteryWebCrawler:
    """Web crawler specialized for mysterious event content."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_content(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """Extract content from a web page.
        
        Args:
            url: URL to crawl
            timeout: Request timeout in seconds
            
        Returns:
            Dict containing extracted content and metadata
        """
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Mock content extraction (in real implementation, use BeautifulSoup or similar)
            content = {
                "url": url,
                "title": f"Mystery Content from {urlparse(url).netloc}",
                "text": f"Extracted content from {url}. This would contain the actual web page content in a real implementation.",
                "metadata": {
                    "status_code": response.status_code,
                    "content_type": response.headers.get('content-type', ''),
                    "content_length": len(response.content),
                    "last_modified": response.headers.get('last-modified', ''),
                },
                "links": [],  # Would extract links in real implementation
                "images": [],  # Would extract images in real implementation
                "timestamp": None
            }
            
            from datetime import datetime
            content["timestamp"] = datetime.now().isoformat()
            
            return content
            
        except requests.RequestException as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "timestamp": None
            }
    
    def batch_crawl(self, urls: List[str], max_workers: int = 5) -> List[Dict[str, Any]]:
        """Crawl multiple URLs concurrently.
        
        Args:
            urls: List of URLs to crawl
            max_workers: Maximum number of concurrent workers
            
        Returns:
            List of extracted content dictionaries
        """
        results = []
        
        # Simple sequential implementation (in real implementation, use ThreadPoolExecutor)
        for url in urls:
            try:
                content = self.extract_content(url)
                results.append(content)
            except Exception as e:
                logger.error(f"Error in batch crawl for {url}: {str(e)}")
                results.append({
                    "url": url,
                    "error": str(e),
                    "timestamp": None
                })
        
        return results


# Global crawler instance
_crawler = MysteryWebCrawler()


@mystery_tool
@tool
def crawl_tool(
    url: str,
    extract_links: bool = False,
    extract_images: bool = False,
    timeout: int = 30
) -> Dict[str, Any]:
    """Crawl a web page and extract content for mystery research.
    
    Args:
        url: URL to crawl
        extract_links: Whether to extract links from the page
        extract_images: Whether to extract images from the page
        timeout: Request timeout in seconds
        
    Returns:
        Dict containing extracted content and metadata
    """
    try:
        content = _crawler.extract_content(url, timeout)
        
        # Add extraction flags to metadata
        if "metadata" not in content:
            content["metadata"] = {}
        content["metadata"]["extract_links"] = extract_links
        content["metadata"]["extract_images"] = extract_images
        
        logger.info(f"Successfully crawled: {url}")
        return content
        
    except Exception as e:
        logger.error(f"Error in crawl_tool: {str(e)}")
        return {
            "url": url,
            "error": str(e),
            "timestamp": None
        }


@mystery_tool
@tool
def batch_crawl_tool(
    urls: List[str],
    max_workers: int = 5,
    timeout: int = 30
) -> Dict[str, Any]:
    """Crawl multiple URLs for mystery research.
    
    Args:
        urls: List of URLs to crawl
        max_workers: Maximum number of concurrent workers
        timeout: Request timeout in seconds
        
    Returns:
        Dict containing batch crawl results
    """
    try:
        results = _crawler.batch_crawl(urls, max_workers)
        
        # Calculate statistics
        successful = sum(1 for r in results if "error" not in r)
        failed = len(results) - successful
        
        return {
            "total_urls": len(urls),
            "successful": successful,
            "failed": failed,
            "results": results,
            "timestamp": None
        }
        
    except Exception as e:
        logger.error(f"Error in batch_crawl_tool: {str(e)}")
        return {
            "total_urls": len(urls),
            "successful": 0,
            "failed": len(urls),
            "error": str(e),
            "results": [],
            "timestamp": None
        }


@mystery_tool
@tool
def mystery_site_crawler(
    site_type: str,
    search_terms: List[str],
    max_pages: int = 10
) -> Dict[str, Any]:
    """Specialized crawler for mystery-related websites.
    
    Args:
        site_type: Type of mystery site (ufo, paranormal, cryptid, etc.)
        search_terms: Terms to search for
        max_pages: Maximum number of pages to crawl
        
    Returns:
        Dict containing crawled mystery content
    """
    try:
        # Mock implementation - would integrate with specific mystery sites
        mystery_sites = {
            "ufo": ["https://www.mufon.com", "https://www.nuforc.org"],
            "paranormal": ["https://www.ghostsandgravestones.com"],
            "cryptid": ["https://www.cryptidz.com"],
            "ancient": ["https://www.ancient-origins.net"]
        }
        
        target_sites = mystery_sites.get(site_type, [])
        if not target_sites:
            return {
                "error": f"Unknown site type: {site_type}",
                "results": []
            }
        
        # Mock crawling results
        results = []
        for site in target_sites[:max_pages]:
            for term in search_terms:
                mock_result = {
                    "url": f"{site}/search?q={term}",
                    "title": f"Mystery Research: {term}",
                    "text": f"Content related to {term} from {site}. This would contain actual search results in a real implementation.",
                    "site_type": site_type,
                    "search_term": term,
                    "relevance_score": 0.8,  # Mock relevance score
                    "timestamp": None
                }
                
                from datetime import datetime
                mock_result["timestamp"] = datetime.now().isoformat()
                results.append(mock_result)
        
        logger.info(f"Mystery site crawl completed: {len(results)} results for {site_type}")
        return {
            "site_type": site_type,
            "search_terms": search_terms,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in mystery_site_crawler: {str(e)}")
        return {
            "site_type": site_type,
            "search_terms": search_terms,
            "error": str(e),
            "results": []
        }