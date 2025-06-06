# Copyright (c) 2024 Lingjing
# SPDX-License-Identifier: MIT

import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import quote, urljoin

from .crawler import Crawler
from ..rag.retriever import Document, Chunk
from ..config.mystery_config import DataSourceConfig


class ForumCrawler(Crawler):
    """论坛社区爬虫"""
    
    def __init__(self, config: DataSourceConfig):
        super().__init__(config)
        self.forum_indicators = [
            "post", "thread", "reply", "forum", "discussion",
            "member", "user", "joined", "posts:"
        ]
        
    async def crawl_url(self, url: str) -> Optional[Document]:
        """爬取论坛页面"""
        html = await self._fetch_html(url)
        if not html:
            return None
            
        parsed_data = self._parse_forum_html(html, url)
        if not parsed_data:
            return None
            
        doc_id = hashlib.md5(url.encode()).hexdigest()
        document = self._create_forum_document(parsed_data, doc_id)
        
        return document
        
    async def search(self, query: str, limit: int = 10) -> List[Document]:
        """搜索论坛讨论"""
        documents = []
        
        # 构建论坛搜索查询
        forum_query = self._build_forum_query(query)
        
        # 生成搜索URL
        search_urls = self._generate_forum_search_urls(forum_query, limit)
        
        for url in search_urls:
            doc = await self.crawl_url(url)
            if doc:
                documents.append(doc)
                
        return documents[:limit]
        
    def _parse_forum_html(self, html: str, url: str) -> Optional[Dict[str, Any]]:
        """解析论坛HTML"""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # 检查是否为论坛页面
        if not self._is_forum_page(soup):
            return None
            
        # 提取主题标题
        title = self._extract_forum_title(soup)
        if not title:
            return None
            
        # 提取帖子内容
        posts = self._extract_forum_posts(soup)
        if not posts:
            return None
            
        # 提取论坛信息
        forum_info = self._extract_forum_info(soup, url)
        
        # 计算论坛内容可信度
        credibility_score = self._calculate_forum_credibility(soup, posts, forum_info)
        
        # 合并所有帖子内容
        content = self._combine_posts_content(posts)
        
        metadata = {
            'url': url,
            'crawled_at': datetime.now().isoformat(),
            'source_type': 'forum',
            'reliability_score': credibility_score,
            'forum_name': forum_info.get('name'),
            'thread_id': forum_info.get('thread_id'),
            'posts_count': len(posts),
            'credibility_score': credibility_score,
            'posts': posts  # 保存原始帖子数据
        }
        
        return {
            'title': title,
            'content': content,
            'metadata': metadata
        }
        
    def _is_forum_page(self, soup) -> bool:
        """检查是否为论坛页面"""
        text = soup.get_text().lower()
        
        # 检查论坛特征词汇
        forum_keywords = [
            'forum', 'thread', 'post', 'reply', 'member',
            'discussion', 'topic', 'board'
        ]
        
        keyword_count = sum(1 for keyword in forum_keywords if keyword in text)
        
        # 检查论坛特有的HTML结构
        forum_selectors = [
            '.post', '.thread', '.forum-post', '.message',
            '.reply', '.discussion', '.topic'
        ]
        
        structure_count = sum(1 for selector in forum_selectors if soup.select(selector))
        
        return keyword_count >= 2 or structure_count >= 1
        
    def _extract_forum_title(self, soup) -> Optional[str]:
        """提取论坛主题标题"""
        title_selectors = [
            'h1.thread-title',
            'h1.topic-title',
            '.thread-title',
            '.topic-title',
            '.discussion-title',
            'h1',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if len(title) > 5:  # 确保标题有意义
                    return title
                    
        return None
        
    def _extract_forum_posts(self, soup) -> List[Dict[str, Any]]:
        """提取论坛帖子"""
        posts = []
        
        # 常见的帖子选择器
        post_selectors = [
            '.post',
            '.message',
            '.forum-post',
            '.thread-post',
            '.reply',
            '.comment'
        ]
        
        for selector in post_selectors:
            post_elems = soup.select(selector)
            if post_elems:
                for i, post_elem in enumerate(post_elems):
                    post_data = self._parse_single_post(post_elem, i)
                    if post_data:
                        posts.append(post_data)
                break  # 找到帖子后就停止
                
        return posts
        
    def _parse_single_post(self, post_elem, index: int) -> Optional[Dict[str, Any]]:
        """解析单个帖子"""
        # 提取帖子内容
        content_selectors = [
            '.post-content',
            '.message-content',
            '.post-body',
            '.content',
            '.text'
        ]
        
        content = ""
        for selector in content_selectors:
            content_elem = post_elem.select_one(selector)
            if content_elem:
                # 移除引用和签名
                for quote in content_elem.select('.quote, .signature, .sig'):
                    quote.decompose()
                content = content_elem.get_text(separator='\n', strip=True)
                break
                
        if not content or len(content) < 10:
            return None
            
        # 提取用户信息
        user_info = self._extract_user_info(post_elem)
        
        # 提取时间信息
        post_time = self._extract_post_time(post_elem)
        
        # 提取帖子ID
        post_id = self._extract_post_id(post_elem, index)
        
        return {
            'id': post_id,
            'content': content,
            'user': user_info,
            'timestamp': post_time,
            'index': index
        }
        
    def _extract_user_info(self, post_elem) -> Dict[str, Any]:
        """提取用户信息"""
        user_info = {}
        
        # 提取用户名
        username_selectors = [
            '.username',
            '.user-name',
            '.author',
            '.poster',
            '.member-name'
        ]
        
        for selector in username_selectors:
            username_elem = post_elem.select_one(selector)
            if username_elem:
                user_info['username'] = username_elem.get_text().strip()
                break
                
        # 提取用户等级/头衔
        rank_selectors = [
            '.user-rank',
            '.user-title',
            '.member-rank',
            '.rank'
        ]
        
        for selector in rank_selectors:
            rank_elem = post_elem.select_one(selector)
            if rank_elem:
                user_info['rank'] = rank_elem.get_text().strip()
                break
                
        # 提取注册时间
        joined_selectors = [
            '.joined',
            '.member-since',
            '.registration-date'
        ]
        
        for selector in joined_selectors:
            joined_elem = post_elem.select_one(selector)
            if joined_elem:
                user_info['joined'] = joined_elem.get_text().strip()
                break
                
        # 提取帖子数量
        posts_count_selectors = [
            '.post-count',
            '.posts',
            '.message-count'
        ]
        
        for selector in posts_count_selectors:
            posts_elem = post_elem.select_one(selector)
            if posts_elem:
                posts_text = posts_elem.get_text()
                posts_match = re.search(r'(\d+)', posts_text)
                if posts_match:
                    user_info['posts_count'] = int(posts_match.group(1))
                break
                
        return user_info
        
    def _extract_post_time(self, post_elem) -> Optional[datetime]:
        """提取帖子时间"""
        time_selectors = [
            'time[datetime]',
            '.post-time',
            '.timestamp',
            '.date',
            '.post-date'
        ]
        
        for selector in time_selectors:
            time_elem = post_elem.select_one(selector)
            if time_elem:
                time_text = time_elem.get('datetime') or time_elem.get_text()
                parsed_time = self._parse_date(time_text)
                if parsed_time:
                    return parsed_time
                    
        return None
        
    def _extract_post_id(self, post_elem, index: int) -> str:
        """提取帖子ID"""
        # 尝试从元素属性提取ID
        post_id = post_elem.get('id') or post_elem.get('data-post-id')
        if post_id:
            return post_id
            
        # 如果没有ID，使用索引
        return f"post_{index}"
        
    def _extract_forum_info(self, soup, url: str) -> Dict[str, Any]:
        """提取论坛信息"""
        forum_info = {}
        
        # 提取论坛名称
        forum_name_selectors = [
            '.forum-name',
            '.board-name',
            '.site-title',
            '.logo'
        ]
        
        for selector in forum_name_selectors:
            name_elem = soup.select_one(selector)
            if name_elem:
                forum_info['name'] = name_elem.get_text().strip()
                break
                
        # 从URL提取论坛名称
        if 'name' not in forum_info:
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            domain = re.sub(r'^www\.', '', domain)
            forum_info['name'] = domain
            
        # 提取主题ID
        thread_id_match = re.search(r'(?:thread|topic|t)[=/](\d+)', url)
        if thread_id_match:
            forum_info['thread_id'] = thread_id_match.group(1)
            
        return forum_info
        
    def _calculate_forum_credibility(self, soup, posts: List[Dict], forum_info: Dict) -> float:
        """计算论坛内容可信度"""
        score = 0.3  # 论坛基础分数较低
        
        # 帖子数量影响可信度
        if len(posts) > 1:
            score += min(len(posts) * 0.05, 0.2)
            
        # 用户质量影响可信度
        experienced_users = 0
        for post in posts:
            user = post.get('user', {})
            posts_count = user.get('posts_count', 0)
            if posts_count > 100:  # 经验丰富的用户
                experienced_users += 1
                
        if experienced_users > 0:
            score += min(experienced_users * 0.1, 0.2)
            
        # 检查是否有管理员或版主回复
        text = soup.get_text().lower()
        authority_indicators = [
            'moderator', 'admin', 'administrator', 'mod',
            'staff', 'expert', 'verified'
        ]
        if any(indicator in text for indicator in authority_indicators):
            score += 0.1
            
        # 检查是否有引用和链接
        links_count = len(soup.find_all('a', href=True))
        if links_count > 5:
            score += 0.05
            
        # 确保分数在0-1范围内
        return min(max(score, 0.0), 1.0)
        
    def _combine_posts_content(self, posts: List[Dict]) -> str:
        """合并帖子内容"""
        combined_content = []
        
        for post in posts:
            user = post.get('user', {})
            username = user.get('username', 'Anonymous')
            content = post.get('content', '')
            timestamp = post.get('timestamp')
            
            post_header = f"\n--- Post by {username}"
            if timestamp:
                post_header += f" at {timestamp.strftime('%Y-%m-%d %H:%M')}"
            post_header += " ---\n"
            
            combined_content.append(post_header + content)
            
        return "\n\n".join(combined_content)
        
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """解析日期字符串"""
        import dateutil.parser
        try:
            return dateutil.parser.parse(date_text)
        except:
            return None
            
    def _create_forum_document(self, parsed_data: Dict[str, Any], doc_id: str) -> Document:
        """创建论坛文档对象"""
        # 创建文档块
        chunks = []
        
        # 为每个帖子创建一个块
        posts = parsed_data['metadata'].get('posts', [])
        for post in posts:
            if post.get('content'):
                chunks.append(Chunk(
                    content=post['content'],
                    similarity=0.6,
                    metadata={
                        'type': 'forum_post',
                        'post_id': post.get('id'),
                        'user': post.get('user', {}),
                        'timestamp': post.get('timestamp').isoformat() if post.get('timestamp') else None
                    }
                ))
                
        return Document(
            id=doc_id,
            url=parsed_data['metadata']['url'],
            title=parsed_data['title'],
            chunks=chunks,
            credibility_score=parsed_data['metadata']['credibility_score'],
            source_type='forum',
            metadata=parsed_data['metadata']
        )
        
    def _build_forum_query(self, query: str) -> str:
        """构建论坛搜索查询"""
        # 添加论坛相关的关键词
        forum_terms = ["forum", "discussion", "thread"]
        
        # 如果查询中没有论坛术语，添加一些
        if not any(term in query.lower() for term in forum_terms):
            query += " forum discussion"
            
        return query
        
    def _generate_forum_search_urls(self, query: str, limit: int) -> List[str]:
        """生成论坛搜索URL列表（模拟）"""
        # 这里应该根据具体的论坛搜索API生成真实的搜索URL
        forum_sites = [
            f"https://www.reddit.com/search?q={quote(query)}",
            f"https://www.abovetopsecret.com/forum/search.php?q={quote(query)}",
            f"https://www.unexplained-mysteries.com/forum/search/?q={quote(query)}",
            f"https://www.phantomsandmonsters.com/search?q={quote(query)}"
        ]
        
        return forum_sites[:limit]