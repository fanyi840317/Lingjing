# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

import re
from datetime import datetime
from typing import Optional, Dict, Any
from readabilipy import simple_json_from_html_string
from .article import Article


class ReadabilityExtractor:
    """可读性提取器，扩展支持神秘事件内容分析"""
    
    def __init__(self):
        self.source_credibility_map = {
            # 学术来源
            "cnki.net": {"type": "academic", "score": 0.9},
            "wanfangdata.com": {"type": "academic", "score": 0.9},
            "webofscience.com": {"type": "academic", "score": 0.95},
            "scholar.google.com": {"type": "academic", "score": 0.85},
            "arxiv.org": {"type": "academic", "score": 0.8},
            
            # 新闻媒体
            "bbc.com": {"type": "news", "score": 0.85},
            "cnn.com": {"type": "news", "score": 0.8},
            "reuters.com": {"type": "news", "score": 0.9},
            "xinhuanet.com": {"type": "news", "score": 0.85},
            "people.com.cn": {"type": "news", "score": 0.85},
            
            # 政府机构
            "gov.cn": {"type": "government", "score": 0.9},
            "nasa.gov": {"type": "government", "score": 0.95},
            "faa.gov": {"type": "government", "score": 0.9},
            
            # 研究机构
            "smithsonian.edu": {"type": "research_institute", "score": 0.9},
            "nationalgeographic.com": {"type": "research_institute", "score": 0.8},
            
            # 神秘事件专门网站
            "mufon.com": {"type": "mystery_research", "score": 0.6},
            "nuforc.org": {"type": "mystery_research", "score": 0.6},
            
            # 论坛和博客
            "reddit.com": {"type": "forum", "score": 0.3},
            "zhihu.com": {"type": "forum", "score": 0.4},
            "tieba.baidu.com": {"type": "forum", "score": 0.2},
            "wordpress.com": {"type": "blog", "score": 0.2},
            "blogspot.com": {"type": "blog", "score": 0.2},
        }
    
    def extract_article(self, html: str, url: str = "") -> Article:
        """提取文章内容"""
        try:
            # 使用readabilipy提取主要内容
            article_data = simple_json_from_html_string(html, use_readability=True)
            
            title = article_data.get("title", "")
            content = article_data.get("content", "")
            
            # 提取元数据
            metadata = self._extract_metadata(html, article_data)
            
            # 分析来源可信度
            source_info = self._analyze_source(url)
            
            # 提取作者信息
            author = self._extract_author(html, article_data)
            
            # 提取发布日期
            publication_date = self._extract_publication_date(html, article_data)
            
            # 创建Article对象
            article = Article(
                title=title,
                html_content=content,
                url=url,
                author=author,
                publication_date=publication_date,
                source_type=source_info["type"],
                credibility_score=source_info["score"],
                metadata=metadata
            )
            
            return article
            
        except Exception as e:
            # 如果提取失败，创建基本的Article对象
            return Article(
                title="提取失败",
                html_content=html[:1000],  # 取前1000字符
                url=url,
                source_type="unknown",
                credibility_score=0.1
            )
    
    def _extract_metadata(self, html: str, article_data: dict) -> Dict[str, Any]:
        """提取元数据"""
        metadata = {}
        
        # 提取基本元数据
        metadata.update(article_data)
        
        # 提取Open Graph标签
        og_tags = self._extract_og_tags(html)
        metadata["og_tags"] = og_tags
        
        # 提取JSON-LD结构化数据
        json_ld = self._extract_json_ld(html)
        metadata["json_ld"] = json_ld
        
        # 提取meta标签
        meta_tags = self._extract_meta_tags(html)
        metadata["meta_tags"] = meta_tags
        
        return metadata
    
    def _analyze_source(self, url: str) -> Dict[str, Any]:
        """分析来源可信度"""
        if not url:
            return {"type": "unknown", "score": 0.1}
        
        url_lower = url.lower()
        
        # 检查已知来源
        for domain, info in self.source_credibility_map.items():
            if domain in url_lower:
                return info
        
        # 基于域名特征进行基本判断
        if any(ext in url_lower for ext in [".edu", ".gov"]):
            return {"type": "institutional", "score": 0.8}
        elif any(ext in url_lower for ext in [".org"]):
            return {"type": "organization", "score": 0.6}
        elif any(keyword in url_lower for keyword in ["news", "press", "media"]):
            return {"type": "news", "score": 0.5}
        elif any(keyword in url_lower for keyword in ["blog", "personal"]):
            return {"type": "blog", "score": 0.2}
        elif any(keyword in url_lower for keyword in ["forum", "discussion", "community"]):
            return {"type": "forum", "score": 0.3}
        else:
            return {"type": "unknown", "score": 0.3}
    
    def _extract_author(self, html: str, article_data: dict) -> str:
        """提取作者信息"""
        # 从article_data中获取
        author = article_data.get("byline", "")
        if author:
            return author
        
        # 从HTML中提取
        author_patterns = [
            r'<meta\s+name=["\']author["\']\s+content=["\']([^"\'>]+)["\']',
            r'<span\s+class=["\'][^"\'>]*author[^"\'>]*["\'][^>]*>([^<]+)</span>',
            r'<div\s+class=["\'][^"\'>]*author[^"\'>]*["\'][^>]*>([^<]+)</div>',
            r'作者[：:](\s*[^\n<>]{2,20})',
            r'By\s+([A-Za-z\s]{2,30})'
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                author = match.group(1).strip()
                if len(author) > 1 and len(author) < 50:
                    return author
        
        return ""
    
    def _extract_publication_date(self, html: str, article_data: dict) -> Optional[datetime]:
        """提取发布日期"""
        # 从article_data中获取
        date_published = article_data.get("date_published")
        if date_published:
            try:
                return datetime.fromisoformat(date_published.replace('Z', '+00:00'))
            except:
                pass
        
        # 从HTML中提取
        date_patterns = [
            r'<meta\s+property=["\']article:published_time["\']\s+content=["\']([^"\'>]+)["\']',
            r'<time\s+datetime=["\']([^"\'>]+)["\']',
            r'<meta\s+name=["\']date["\']\s+content=["\']([^"\'>]+)["\']',
            r'发布时间[：:]\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'(\d{4}年\d{1,2}月\d{1,2}日)',
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, html)
            if match:
                date_str = match.group(1)
                try:
                    # 尝试多种日期格式
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y-%m-%dT%H:%M:%S', '%Y年%m月%d日']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except:
                            continue
                except:
                    continue
        
        return None
    
    def _extract_og_tags(self, html: str) -> Dict[str, str]:
        """提取Open Graph标签"""
        og_tags = {}
        og_pattern = r'<meta\s+property=["\']og:([^"\'>]+)["\']\s+content=["\']([^"\'>]*)["\']'
        
        matches = re.findall(og_pattern, html, re.IGNORECASE)
        for prop, content in matches:
            og_tags[prop] = content
        
        return og_tags
    
    def _extract_json_ld(self, html: str) -> list:
        """提取JSON-LD结构化数据"""
        import json
        
        json_ld_data = []
        json_ld_pattern = r'<script\s+type=["\']application/ld\+json["\'][^>]*>([^<]+)</script>'
        
        matches = re.findall(json_ld_pattern, html, re.IGNORECASE | re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match.strip())
                json_ld_data.append(data)
            except:
                continue
        
        return json_ld_data
    
    def _extract_meta_tags(self, html: str) -> Dict[str, str]:
        """提取meta标签"""
        meta_tags = {}
        meta_pattern = r'<meta\s+name=["\']([^"\'>]+)["\']\s+content=["\']([^"\'>]*)["\']'
        
        matches = re.findall(meta_pattern, html, re.IGNORECASE)
        for name, content in matches:
            meta_tags[name] = content
        
        return meta_tags
    
    def analyze_content_quality(self, article: Article) -> Dict[str, Any]:
        """分析内容质量"""
        content = article._get_plain_text()
        
        quality_metrics = {
            "word_count": len(content.split()),
            "character_count": len(content),
            "paragraph_count": len(content.split('\n\n')),
            "has_images": "<img" in article.html_content.lower(),
            "has_links": "<a" in article.html_content.lower(),
            "readability_score": self._calculate_readability_score(content),
            "mystery_keyword_density": self._calculate_mystery_keyword_density(content),
            "technical_term_count": self._count_technical_terms(content)
        }
        
        # 计算综合质量分数
        quality_score = self._calculate_quality_score(quality_metrics)
        quality_metrics["overall_quality_score"] = quality_score
        
        return quality_metrics
    
    def _calculate_readability_score(self, content: str) -> float:
        """计算可读性分数（简化版）"""
        if not content:
            return 0.0
        
        words = content.split()
        sentences = re.split(r'[.!?。！？]', content)
        
        if len(sentences) == 0:
            return 0.0
        
        avg_words_per_sentence = len(words) / len(sentences)
        
        # 简化的可读性评分
        if avg_words_per_sentence < 10:
            return 0.9
        elif avg_words_per_sentence < 20:
            return 0.7
        elif avg_words_per_sentence < 30:
            return 0.5
        else:
            return 0.3
    
    def _calculate_mystery_keyword_density(self, content: str) -> float:
        """计算神秘事件关键词密度"""
        if not content:
            return 0.0
        
        mystery_keywords = [
            "ufo", "不明飞行物", "外星人", "飞碟", "水怪", "神秘生物", 
            "幽灵", "鬼魂", "超自然", "失踪", "消失", "古代文明", 
            "金字塔", "百慕大", "麦田怪圈", "尼斯湖", "大脚怪"
        ]
        
        content_lower = content.lower()
        keyword_count = sum(1 for keyword in mystery_keywords if keyword in content_lower)
        word_count = len(content.split())
        
        return keyword_count / word_count if word_count > 0 else 0.0
    
    def _count_technical_terms(self, content: str) -> int:
        """统计技术术语数量"""
        technical_terms = [
            "雷达", "声纳", "红外", "光谱", "频率", "波长", "磁场", 
            "辐射", "plasma", "electromagnetic", "infrared", "radar", 
            "sonar", "frequency", "wavelength", "magnetic", "radiation"
        ]
        
        content_lower = content.lower()
        return sum(1 for term in technical_terms if term in content_lower)
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> float:
        """计算综合质量分数"""
        score = 0.0
        
        # 基于字数
        word_count = metrics.get("word_count", 0)
        if word_count > 500:
            score += 0.3
        elif word_count > 200:
            score += 0.2
        elif word_count > 50:
            score += 0.1
        
        # 基于可读性
        readability = metrics.get("readability_score", 0)
        score += readability * 0.3
        
        # 基于多媒体内容
        if metrics.get("has_images"):
            score += 0.1
        if metrics.get("has_links"):
            score += 0.1
        
        # 基于神秘事件相关性
        mystery_density = metrics.get("mystery_keyword_density", 0)
        score += min(mystery_density * 10, 0.2)  # 最多加0.2分
        
        return min(score, 1.0)