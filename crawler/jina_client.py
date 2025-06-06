# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

import logging
import os
import time
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class JinaClient:
    """Jina客户端，用于网页内容抓取"""
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key or os.getenv("JINA_API_KEY")
        self.timeout = timeout
        self.max_retries = max_retries
        
        # 配置会话
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        if not self.api_key:
            logger.warning(
                "Jina API key is not set. Provide your own key to access a higher rate limit. "
                "See https://jina.ai/reader for more information."
            )
    
    def crawl(
        self, 
        url: str, 
        return_format: str = "html",
        include_links: bool = False,
        include_images: bool = True,
        target_selector: Optional[str] = None,
        wait_for_selector: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> str:
        """爬取网页内容"""
        request_headers = {
            "Content-Type": "application/json",
            "X-Return-Format": return_format,
        }
        
        if self.api_key:
            request_headers["Authorization"] = f"Bearer {self.api_key}"
        
        # 添加自定义请求头
        if headers:
            request_headers.update(headers)
        
        # 构建请求数据
        data = {"url": url}
        
        if include_links:
            data["include_links"] = True
        if not include_images:
            data["include_images"] = False
        if target_selector:
            data["target_selector"] = target_selector
        if wait_for_selector:
            data["wait_for_selector"] = wait_for_selector
        
        try:
            response = self.session.post(
                "https://r.jina.ai/", 
                headers=request_headers, 
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to crawl {url}: {e}")
            raise
    
    def crawl_multiple(
        self, 
        urls: list[str], 
        return_format: str = "html",
        delay: float = 1.0,
        **kwargs
    ) -> Dict[str, str]:
        """批量爬取多个URL"""
        results = {}
        
        for i, url in enumerate(urls):
            try:
                logger.info(f"Crawling {i+1}/{len(urls)}: {url}")
                content = self.crawl(url, return_format=return_format, **kwargs)
                results[url] = content
                
                # 添加延迟避免频率限制
                if i < len(urls) - 1 and delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Failed to crawl {url}: {e}")
                results[url] = ""
        
        return results
    
    def crawl_with_fallback(
        self, 
        url: str, 
        return_format: str = "html",
        fallback_formats: list[str] = None
    ) -> tuple[str, str]:
        """带回退机制的爬取"""
        fallback_formats = fallback_formats or ["text", "markdown"]
        
        # 首先尝试主要格式
        try:
            content = self.crawl(url, return_format=return_format)
            return content, return_format
        except Exception as e:
            logger.warning(f"Failed to crawl {url} with format {return_format}: {e}")
        
        # 尝试回退格式
        for format_type in fallback_formats:
            try:
                logger.info(f"Trying fallback format {format_type} for {url}")
                content = self.crawl(url, return_format=format_type)
                return content, format_type
            except Exception as e:
                logger.warning(f"Failed to crawl {url} with format {format_type}: {e}")
        
        raise Exception(f"Failed to crawl {url} with all attempted formats")
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            test_url = "https://example.com"
            self.crawl(test_url, return_format="text")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """获取速率限制信息（如果API支持）"""
        # 这是一个示例实现，实际需要根据Jina API的具体响应来调整
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            # 发送一个简单请求来获取响应头中的速率限制信息
            response = self.session.post(
                "https://r.jina.ai/", 
                headers=headers, 
                json={"url": "https://example.com"},
                timeout=10
            )
            
            rate_limit_info = {}
            for header_name in response.headers:
                if "rate" in header_name.lower() or "limit" in header_name.lower():
                    rate_limit_info[header_name] = response.headers[header_name]
            
            return rate_limit_info
        except Exception as e:
            logger.error(f"Failed to get rate limit info: {e}")
            return {}
    
    def close(self):
        """关闭会话"""
        if self.session:
            self.session.close()