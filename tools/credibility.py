# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlparse

from langchain_core.tools import BaseTool, tool

from config.mystery_config import MysteryEventConfig, DataSourceConfig, DataSourceType
from tools.decorators import log_io

logger = logging.getLogger(__name__)


@dataclass
class CredibilityScore:
    """可信度评分结果"""
    overall_score: float  # 总体评分 (0-1)
    source_score: float  # 来源评分
    content_score: float  # 内容评分
    temporal_score: float  # 时效性评分
    detail_score: float  # 细节丰富度评分
    logic_score: float  # 逻辑一致性评分
    factors: Dict[str, Any]  # 评分因子详情
    recommendations: List[str]  # 改进建议


class CredibilityAnalyzer(BaseTool):
    """信息可信度分析工具"""
    name: str = "credibility_analyzer"
    description: str = "Analyze the credibility of mystery event information based on multiple criteria."
    
    def __init__(self, config: Optional[MysteryEventConfig] = None):
        """初始化可信度分析器
        
        Args:
            config: 神秘事件配置
        """
        super().__init__()
        self.config = config or MysteryEventConfig()
        
        # 可靠来源域名列表
        self.reliable_domains = {
            # 学术机构
            "nature.com": 0.95,
            "science.org": 0.95,
            "arxiv.org": 0.9,
            "researchgate.net": 0.85,
            "cnki.net": 0.9,
            "wanfangdata.com.cn": 0.85,
            "webofscience.com": 0.95,
            
            # 权威媒体
            "bbc.com": 0.9,
            "cnn.com": 0.85,
            "reuters.com": 0.9,
            "ap.org": 0.9,
            "xinhuanet.com": 0.9,
            "people.com.cn": 0.85,
            "nytimes.com": 0.85,
            "washingtonpost.com": 0.85,
            
            # 政府机构
            "nasa.gov": 0.95,
            "fbi.gov": 0.9,
            "defense.gov": 0.9,
            "noaa.gov": 0.9,
            
            # 专业研究机构
            "mufon.com": 0.7,
            "nuforc.org": 0.75,
            "skepticalinquirer.org": 0.85,
            
            # 低可信度来源
            "dailymail.co.uk": 0.3,
            "infowars.com": 0.1,
            "beforeitsnews.com": 0.1,
        }
        
        # 专业术语词典
        self.professional_terms = {
            "ufo": ["radar", "aircraft", "altitude", "velocity", "trajectory", "electromagnetic", 
                   "雷达", "飞行器", "高度", "速度", "轨迹", "电磁"],
            "paranormal": ["electromagnetic field", "temperature anomaly", "infrared", "frequency",
                          "电磁场", "温度异常", "红外", "频率"],
            "cryptid": ["species", "habitat", "behavior", "taxonomy", "ecosystem", "biodiversity",
                       "物种", "栖息地", "行为", "分类学", "生态系统", "生物多样性"],
            "ancient": ["archaeology", "carbon dating", "stratigraphy", "artifact", "civilization",
                       "考古学", "碳定年", "地层学", "文物", "文明"]
        }
    
    def _run(self, content: str, source_url: str = "", publish_date: str = "") -> str:
        """运行可信度分析
        
        Args:
            content: 要分析的内容
            source_url: 来源URL
            publish_date: 发布日期 (YYYY-MM-DD格式)
            
        Returns:
            JSON格式的可信度分析结果
        """
        try:
            score = self.analyze_credibility(content, source_url, publish_date)
            return json.dumps({
                "credibility_score": score.overall_score,
                "source_score": score.source_score,
                "content_score": score.content_score,
                "temporal_score": score.temporal_score,
                "detail_score": score.detail_score,
                "logic_score": score.logic_score,
                "factors": score.factors,
                "recommendations": score.recommendations,
                "is_reliable": score.overall_score >= self.config.credibility_threshold
            }, ensure_ascii=False)
        except Exception as e:
            error_msg = f"Failed to analyze credibility. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def analyze_credibility(self, content: str, source_url: str = "", publish_date: str = "") -> CredibilityScore:
        """分析内容的可信度
        
        Args:
            content: 要分析的内容
            source_url: 来源URL
            publish_date: 发布日期
            
        Returns:
            CredibilityScore对象
        """
        # 1. 来源可信度评分
        source_score = self._analyze_source_credibility(source_url)
        
        # 2. 内容逻辑性评分
        logic_score = self._analyze_content_logic(content)
        
        # 3. 专业术语使用评分
        term_score = self._analyze_professional_terms(content)
        
        # 4. 细节丰富度评分
        detail_score = self._analyze_detail_richness(content)
        
        # 5. 时效性评分
        temporal_score = self._analyze_temporal_relevance(publish_date)
        
        # 综合内容评分
        content_score = (logic_score * 0.4 + term_score * 0.3 + detail_score * 0.3)
        
        # 计算总体评分
        overall_score = (
            source_score * 0.3 +
            content_score * 0.4 +
            temporal_score * 0.3
        )
        
        # 生成评分因子详情
        factors = {
            "source_analysis": self._get_source_analysis(source_url),
            "content_analysis": {
                "logic_issues": self._detect_logic_issues(content),
                "professional_terms_count": self._count_professional_terms(content),
                "detail_indicators": self._get_detail_indicators(content),
                "word_count": len(content.split()),
                "sentence_count": len(re.split(r'[.!?。！？]', content))
            },
            "temporal_analysis": self._get_temporal_analysis(publish_date)
        }
        
        # 生成改进建议
        recommendations = self._generate_recommendations(
            source_score, logic_score, term_score, detail_score, temporal_score
        )
        
        return CredibilityScore(
            overall_score=overall_score,
            source_score=source_score,
            content_score=content_score,
            temporal_score=temporal_score,
            detail_score=detail_score,
            logic_score=logic_score,
            factors=factors,
            recommendations=recommendations
        )
    
    def _analyze_source_credibility(self, source_url: str) -> float:
        """分析来源可信度"""
        if not source_url:
            return 0.5  # 默认中等可信度
        
        try:
            domain = urlparse(source_url).netloc.lower()
            # 移除www前缀
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # 检查是否在可靠来源列表中
            for reliable_domain, score in self.reliable_domains.items():
                if reliable_domain in domain:
                    return score
            
            # 检查是否是政府域名
            if domain.endswith('.gov'):
                return 0.9
            
            # 检查是否是教育机构域名
            if domain.endswith('.edu'):
                return 0.85
            
            # 检查是否是学术机构域名
            if any(keyword in domain for keyword in ['university', 'institute', 'research', 'academic']):
                return 0.8
            
            return 0.5  # 默认评分
        except Exception:
            return 0.5
    
    def _analyze_content_logic(self, content: str) -> float:
        """分析内容逻辑性"""
        logic_score = 1.0
        
        # 检查矛盾表述
        contradictions = self._detect_contradictions(content)
        logic_score -= len(contradictions) * 0.2
        
        # 检查夸张表述
        exaggerations = self._detect_exaggerations(content)
        logic_score -= len(exaggerations) * 0.1
        
        # 检查逻辑连贯性
        coherence_score = self._analyze_coherence(content)
        logic_score = (logic_score + coherence_score) / 2
        
        return max(0.0, min(1.0, logic_score))
    
    def _detect_contradictions(self, content: str) -> List[str]:
        """检测矛盾表述"""
        contradictions = []
        content_lower = content.lower()
        
        # 常见矛盾模式
        contradiction_patterns = [
            (r'不可能.*但是.*可能', '逻辑矛盾：不可能与可能'),
            (r'从未.*但.*曾经', '时间矛盾：从未与曾经'),
            (r'完全.*部分', '程度矛盾：完全与部分'),
            (r'always.*never', '逻辑矛盾：always与never'),
            (r'impossible.*possible', '逻辑矛盾：impossible与possible')
        ]
        
        for pattern, description in contradiction_patterns:
            if re.search(pattern, content_lower):
                contradictions.append(description)
        
        return contradictions
    
    def _detect_exaggerations(self, content: str) -> List[str]:
        """检测夸张表述"""
        exaggerations = []
        content_lower = content.lower()
        
        # 夸张词汇
        exaggeration_words = [
            '绝对', '完全', '彻底', '史无前例', '前所未有', '震惊世界',
            'absolutely', 'completely', 'totally', 'unprecedented', 'shocking'
        ]
        
        for word in exaggeration_words:
            if word in content_lower:
                exaggerations.append(f'夸张表述：{word}')
        
        return exaggerations
    
    def _analyze_coherence(self, content: str) -> float:
        """分析内容连贯性"""
        sentences = re.split(r'[.!?。！？]', content)
        if len(sentences) < 2:
            return 0.8  # 单句内容给予中等评分
        
        # 简单的连贯性检查：检查句子之间的关联词
        coherence_indicators = [
            '因此', '所以', '然而', '但是', '而且', '另外', '此外',
            'therefore', 'however', 'moreover', 'furthermore', 'additionally'
        ]
        
        coherence_count = 0
        for sentence in sentences:
            if any(indicator in sentence for indicator in coherence_indicators):
                coherence_count += 1
        
        coherence_ratio = coherence_count / len(sentences)
        return min(1.0, coherence_ratio * 2)  # 归一化到0-1
    
    def _analyze_professional_terms(self, content: str) -> float:
        """分析专业术语使用情况"""
        content_lower = content.lower()
        total_terms = 0
        found_terms = 0
        
        for category, terms in self.professional_terms.items():
            for term in terms:
                total_terms += 1
                if term.lower() in content_lower:
                    found_terms += 1
        
        if total_terms == 0:
            return 0.5
        
        term_ratio = found_terms / total_terms
        return min(1.0, term_ratio * 5)  # 放大比例，因为专业术语相对较少
    
    def _count_professional_terms(self, content: str) -> int:
        """统计专业术语数量"""
        content_lower = content.lower()
        count = 0
        
        for category, terms in self.professional_terms.items():
            for term in terms:
                if term.lower() in content_lower:
                    count += 1
        
        return count
    
    def _analyze_detail_richness(self, content: str) -> float:
        """分析细节丰富度"""
        # 基于内容长度、数字、时间、地点等细节指标
        word_count = len(content.split())
        
        # 数字和时间的出现次数
        numbers = len(re.findall(r'\d+', content))
        dates = len(re.findall(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}', content))
        times = len(re.findall(r'\d{1,2}:\d{2}', content))
        
        # 地点指示词
        location_indicators = ['在', '位于', '地点', '地区', '城市', 'at', 'in', 'location', 'place']
        locations = sum(1 for indicator in location_indicators if indicator in content.lower())
        
        # 计算细节评分
        detail_score = 0.0
        
        # 基于字数的评分
        if word_count > 200:
            detail_score += 0.3
        elif word_count > 100:
            detail_score += 0.2
        elif word_count > 50:
            detail_score += 0.1
        
        # 基于具体细节的评分
        detail_score += min(0.3, numbers * 0.05)  # 数字细节
        detail_score += min(0.2, (dates + times) * 0.1)  # 时间细节
        detail_score += min(0.2, locations * 0.1)  # 地点细节
        
        return min(1.0, detail_score)
    
    def _get_detail_indicators(self, content: str) -> Dict[str, int]:
        """获取细节指标"""
        return {
            "numbers": len(re.findall(r'\d+', content)),
            "dates": len(re.findall(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}', content)),
            "times": len(re.findall(r'\d{1,2}:\d{2}', content)),
            "locations": sum(1 for indicator in ['在', '位于', '地点', 'at', 'in', 'location'] 
                           if indicator in content.lower())
        }
    
    def _analyze_temporal_relevance(self, publish_date: str) -> float:
        """分析时效性"""
        if not publish_date:
            return 0.5  # 无日期信息给予中等评分
        
        try:
            pub_date = datetime.strptime(publish_date, "%Y-%m-%d")
            current_date = datetime.now()
            days_diff = (current_date - pub_date).days
            
            # 时效性评分：越新越好
            if days_diff <= 30:  # 1个月内
                return 1.0
            elif days_diff <= 90:  # 3个月内
                return 0.9
            elif days_diff <= 365:  # 1年内
                return 0.8
            elif days_diff <= 365 * 2:  # 2年内
                return 0.6
            elif days_diff <= 365 * 5:  # 5年内
                return 0.4
            else:
                return 0.2
        except ValueError:
            return 0.5
    
    def _get_source_analysis(self, source_url: str) -> Dict[str, Any]:
        """获取来源分析详情"""
        if not source_url:
            return {"domain": "unknown", "type": "unknown", "reliability": "unknown"}
        
        try:
            domain = urlparse(source_url).netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            
            source_type = "unknown"
            if domain.endswith('.gov'):
                source_type = "government"
            elif domain.endswith('.edu'):
                source_type = "educational"
            elif any(keyword in domain for keyword in ['news', 'media', 'times', 'post']):
                source_type = "news_media"
            elif domain in self.reliable_domains:
                source_type = "verified_source"
            
            reliability = self.reliable_domains.get(domain, "unknown")
            
            return {
                "domain": domain,
                "type": source_type,
                "reliability": reliability
            }
        except Exception:
            return {"domain": "unknown", "type": "unknown", "reliability": "unknown"}
    
    def _detect_logic_issues(self, content: str) -> List[str]:
        """检测逻辑问题"""
        issues = []
        issues.extend(self._detect_contradictions(content))
        issues.extend(self._detect_exaggerations(content))
        return issues
    
    def _get_temporal_analysis(self, publish_date: str) -> Dict[str, Any]:
        """获取时效性分析详情"""
        if not publish_date:
            return {"date": "unknown", "age_days": "unknown", "freshness": "unknown"}
        
        try:
            pub_date = datetime.strptime(publish_date, "%Y-%m-%d")
            current_date = datetime.now()
            days_diff = (current_date - pub_date).days
            
            freshness = "very_old"
            if days_diff <= 30:
                freshness = "very_fresh"
            elif days_diff <= 90:
                freshness = "fresh"
            elif days_diff <= 365:
                freshness = "recent"
            elif days_diff <= 365 * 2:
                freshness = "old"
            
            return {
                "date": publish_date,
                "age_days": days_diff,
                "freshness": freshness
            }
        except ValueError:
            return {"date": "invalid", "age_days": "unknown", "freshness": "unknown"}
    
    def _generate_recommendations(self, source_score: float, logic_score: float, 
                                term_score: float, detail_score: float, 
                                temporal_score: float) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if source_score < 0.6:
            recommendations.append("建议寻找更可靠的信息来源，如学术机构、政府部门或权威媒体")
        
        if logic_score < 0.6:
            recommendations.append("内容存在逻辑问题，建议核实信息的一致性和合理性")
        
        if term_score < 0.4:
            recommendations.append("缺乏专业术语，建议补充相关领域的专业描述")
        
        if detail_score < 0.5:
            recommendations.append("细节不够丰富，建议添加具体的时间、地点、数据等信息")
        
        if temporal_score < 0.5:
            recommendations.append("信息较为陈旧，建议寻找更新的相关报道或研究")
        
        if not recommendations:
            recommendations.append("信息质量良好，可以作为可靠参考")
        
        return recommendations


@tool
@log_io
def analyze_information_credibility(
    content: str,
    source_url: str = "",
    publish_date: str = ""
) -> str:
    """分析信息的可信度
    
    Args:
        content: 要分析的内容文本
        source_url: 信息来源URL（可选）
        publish_date: 发布日期，格式为YYYY-MM-DD（可选）
    
    Returns:
        JSON格式的可信度分析结果
    """
    try:
        analyzer = CredibilityAnalyzer()
        return analyzer._run(content, source_url, publish_date)
    except Exception as e:
        error_msg = f"Failed to analyze credibility. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def filter_reliable_information(
    information_list: List[Dict[str, Any]],
    min_credibility: float = 0.6
) -> str:
    """筛选可靠信息
    
    Args:
        information_list: 信息列表，每个元素包含content, source_url, publish_date等字段
        min_credibility: 最小可信度阈值
    
    Returns:
        JSON格式的筛选结果
    """
    try:
        analyzer = CredibilityAnalyzer()
        reliable_info = []
        filtered_info = []
        
        for info in information_list:
            content = info.get('content', '')
            source_url = info.get('source_url', '')
            publish_date = info.get('publish_date', '')
            
            score = analyzer.analyze_credibility(content, source_url, publish_date)
            
            info_with_score = info.copy()
            info_with_score['credibility_score'] = score.overall_score
            info_with_score['credibility_analysis'] = {
                'source_score': score.source_score,
                'content_score': score.content_score,
                'temporal_score': score.temporal_score,
                'recommendations': score.recommendations
            }
            
            if score.overall_score >= min_credibility:
                reliable_info.append(info_with_score)
            else:
                filtered_info.append(info_with_score)
        
        return json.dumps({
            'reliable_information': reliable_info,
            'filtered_information': filtered_info,
            'total_count': len(information_list),
            'reliable_count': len(reliable_info),
            'filtered_count': len(filtered_info)
        }, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Failed to filter reliable information. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)