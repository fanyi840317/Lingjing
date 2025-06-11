# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import json
import logging
import math
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import re

from langchain_core.tools import BaseTool, tool

from config.mystery_config import MysteryEventConfig, MysteryEventType
from tools.decorators import log_io

logger = logging.getLogger(__name__)


@dataclass
class EventCorrelation:
    """事件关联结果"""
    event1_id: str
    event2_id: str
    correlation_type: str  # temporal, geographical, phenomenological, witness, media
    correlation_score: float  # 0-1
    correlation_factors: Dict[str, Any]
    description: str


@dataclass
class MysteryEvent:
    """神秘事件数据结构"""
    id: str
    title: str
    description: str
    event_type: str
    location: Optional[Dict[str, float]] = None  # {"lat": float, "lon": float}
    timestamp: Optional[datetime] = None
    witnesses: List[str] = None
    sources: List[str] = None
    phenomena: List[str] = None
    keywords: List[str] = None
    
    def __post_init__(self):
        if self.witnesses is None:
            self.witnesses = []
        if self.sources is None:
            self.sources = []
        if self.phenomena is None:
            self.phenomena = []
        if self.keywords is None:
            self.keywords = []


class CorrelationAnalyzer(BaseTool):
    """关联分析工具"""
    name: str = "correlation_analyzer"
    description: str = "Analyze correlations between mysterious events based on multiple factors."
    
    def __init__(self, config: Optional[MysteryEventConfig] = None):
        """初始化关联分析器
        
        Args:
            config: 神秘事件配置
        """
        super().__init__()
        self.config = config or MysteryEventConfig()
        
        # 现象特征词典
        self.phenomenon_features = {
            "light": ["光", "发光", "闪光", "光球", "光柱", "light", "glow", "flash", "beam", "orb"],
            "sound": ["声音", "噪音", "嗡嗡声", "轰鸣", "sound", "noise", "hum", "buzz", "roar"],
            "movement": ["移动", "飞行", "悬浮", "消失", "movement", "flying", "hovering", "vanish"],
            "shape": ["圆形", "三角形", "椭圆", "碟形", "圆盘", "circular", "triangular", "oval", "disc"],
            "size": ["巨大", "小型", "中等", "huge", "small", "medium", "large", "tiny"],
            "color": ["红色", "蓝色", "白色", "绿色", "橙色", "red", "blue", "white", "green", "orange"],
            "electromagnetic": ["电磁", "干扰", "静电", "electromagnetic", "interference", "static"],
            "temperature": ["温度", "冷", "热", "temperature", "cold", "hot", "warm", "cool"]
        }
    
    def _run(self, events_data: str, correlation_types: List[str] = None) -> str:
        """运行关联分析
        
        Args:
            events_data: JSON格式的事件数据列表
            correlation_types: 要分析的关联类型列表
            
        Returns:
            JSON格式的关联分析结果
        """
        try:
            # 解析事件数据
            events_list = json.loads(events_data)
            events = [self._parse_event(event_data) for event_data in events_list]
            
            # 设置默认关联类型
            if correlation_types is None:
                correlation_types = ["temporal", "geographical", "phenomenological", "witness", "media"]
            
            # 执行关联分析
            correlations = self.analyze_correlations(events, correlation_types)
            
            # 构建关联网络
            network = self._build_correlation_network(correlations)
            
            # 生成分析报告
            analysis_report = self._generate_analysis_report(events, correlations, network)
            
            return json.dumps({
                "correlations": [self._correlation_to_dict(corr) for corr in correlations],
                "network": network,
                "analysis_report": analysis_report,
                "total_events": len(events),
                "total_correlations": len(correlations)
            }, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to analyze correlations. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _parse_event(self, event_data: Dict[str, Any]) -> MysteryEvent:
        """解析事件数据"""
        # 解析时间戳
        timestamp = None
        if "timestamp" in event_data and event_data["timestamp"]:
            try:
                if isinstance(event_data["timestamp"], str):
                    timestamp = datetime.fromisoformat(event_data["timestamp"].replace('Z', '+00:00'))
                elif isinstance(event_data["timestamp"], (int, float)):
                    timestamp = datetime.fromtimestamp(event_data["timestamp"])
            except (ValueError, TypeError):
                logger.warning(f"Failed to parse timestamp: {event_data.get('timestamp')}")
        
        # 解析地理位置
        location = None
        if "location" in event_data and event_data["location"]:
            loc_data = event_data["location"]
            if isinstance(loc_data, dict) and "lat" in loc_data and "lon" in loc_data:
                location = {"lat": float(loc_data["lat"]), "lon": float(loc_data["lon"])}
        
        return MysteryEvent(
            id=event_data.get("id", ""),
            title=event_data.get("title", ""),
            description=event_data.get("description", ""),
            event_type=event_data.get("event_type", ""),
            location=location,
            timestamp=timestamp,
            witnesses=event_data.get("witnesses", []),
            sources=event_data.get("sources", []),
            phenomena=event_data.get("phenomena", []),
            keywords=event_data.get("keywords", [])
        )
    
    def analyze_correlations(self, events: List[MysteryEvent], 
                           correlation_types: List[str]) -> List[EventCorrelation]:
        """分析事件间的关联关系"""
        correlations = []
        
        # 两两比较所有事件
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                event1, event2 = events[i], events[j]
                
                # 分析各种类型的关联
                for corr_type in correlation_types:
                    correlation = self._analyze_single_correlation(event1, event2, corr_type)
                    if correlation and correlation.correlation_score >= self.config.similarity_threshold:
                        correlations.append(correlation)
        
        # 按关联分数排序
        correlations.sort(key=lambda x: x.correlation_score, reverse=True)
        
        # 限制每个事件的最大关联数
        return self._limit_correlations_per_event(correlations)
    
    def _analyze_single_correlation(self, event1: MysteryEvent, event2: MysteryEvent, 
                                  correlation_type: str) -> Optional[EventCorrelation]:
        """分析两个事件之间的单一类型关联"""
        if correlation_type == "temporal":
            return self._analyze_temporal_correlation(event1, event2)
        elif correlation_type == "geographical":
            return self._analyze_geographical_correlation(event1, event2)
        elif correlation_type == "phenomenological":
            return self._analyze_phenomenological_correlation(event1, event2)
        elif correlation_type == "witness":
            return self._analyze_witness_correlation(event1, event2)
        elif correlation_type == "media":
            return self._analyze_media_correlation(event1, event2)
        else:
            return None
    
    def _analyze_temporal_correlation(self, event1: MysteryEvent, 
                                    event2: MysteryEvent) -> Optional[EventCorrelation]:
        """分析时间关联"""
        if not event1.timestamp or not event2.timestamp:
            return None
        
        time_diff = abs((event1.timestamp - event2.timestamp).total_seconds())
        max_time_diff = self.config.time_window_days * 24 * 3600  # 转换为秒
        
        if time_diff > max_time_diff:
            return None
        
        # 计算时间关联分数（时间越近分数越高）
        score = 1.0 - (time_diff / max_time_diff)
        
        factors = {
            "time_difference_seconds": time_diff,
            "time_difference_days": time_diff / (24 * 3600),
            "event1_time": event1.timestamp.isoformat(),
            "event2_time": event2.timestamp.isoformat()
        }
        
        description = f"事件在{time_diff/(24*3600):.1f}天内发生，存在时间关联"
        
        return EventCorrelation(
            event1_id=event1.id,
            event2_id=event2.id,
            correlation_type="temporal",
            correlation_score=score,
            correlation_factors=factors,
            description=description
        )
    
    def _analyze_geographical_correlation(self, event1: MysteryEvent, 
                                        event2: MysteryEvent) -> Optional[EventCorrelation]:
        """分析地理关联"""
        if not event1.location or not event2.location:
            return None
        
        # 计算两点间距离（使用Haversine公式）
        distance = self._calculate_distance(
            event1.location["lat"], event1.location["lon"],
            event2.location["lat"], event2.location["lon"]
        )
        
        if distance > self.config.location_radius_km:
            return None
        
        # 计算地理关联分数（距离越近分数越高）
        score = 1.0 - (distance / self.config.location_radius_km)
        
        factors = {
            "distance_km": distance,
            "event1_location": event1.location,
            "event2_location": event2.location
        }
        
        description = f"事件相距{distance:.1f}公里，存在地理关联"
        
        return EventCorrelation(
            event1_id=event1.id,
            event2_id=event2.id,
            correlation_type="geographical",
            correlation_score=score,
            correlation_factors=factors,
            description=description
        )
    
    def _analyze_phenomenological_correlation(self, event1: MysteryEvent, 
                                            event2: MysteryEvent) -> Optional[EventCorrelation]:
        """分析现象关联"""
        # 提取现象特征
        features1 = self._extract_phenomenon_features(event1)
        features2 = self._extract_phenomenon_features(event2)
        
        if not features1 or not features2:
            return None
        
        # 计算特征相似度
        similarity = self._calculate_feature_similarity(features1, features2)
        
        if similarity < 0.3:  # 最低相似度阈值
            return None
        
        factors = {
            "event1_features": features1,
            "event2_features": features2,
            "common_features": list(set(features1.keys()) & set(features2.keys())),
            "similarity_score": similarity
        }
        
        common_features = list(set(features1.keys()) & set(features2.keys()))
        description = f"事件具有相似现象特征：{', '.join(common_features)}"
        
        return EventCorrelation(
            event1_id=event1.id,
            event2_id=event2.id,
            correlation_type="phenomenological",
            correlation_score=similarity,
            correlation_factors=factors,
            description=description
        )
    
    def _analyze_witness_correlation(self, event1: MysteryEvent, 
                                   event2: MysteryEvent) -> Optional[EventCorrelation]:
        """分析证人关联"""
        if not event1.witnesses or not event2.witnesses:
            return None
        
        # 查找共同证人
        common_witnesses = set(event1.witnesses) & set(event2.witnesses)
        
        if not common_witnesses:
            return None
        
        # 计算证人关联分数
        total_witnesses = len(set(event1.witnesses) | set(event2.witnesses))
        score = len(common_witnesses) / total_witnesses
        
        factors = {
            "common_witnesses": list(common_witnesses),
            "event1_witnesses": event1.witnesses,
            "event2_witnesses": event2.witnesses,
            "common_count": len(common_witnesses),
            "total_unique_witnesses": total_witnesses
        }
        
        description = f"事件有{len(common_witnesses)}个共同证人"
        
        return EventCorrelation(
            event1_id=event1.id,
            event2_id=event2.id,
            correlation_type="witness",
            correlation_score=score,
            correlation_factors=factors,
            description=description
        )
    
    def _analyze_media_correlation(self, event1: MysteryEvent, 
                                 event2: MysteryEvent) -> Optional[EventCorrelation]:
        """分析媒体来源关联"""
        if not event1.sources or not event2.sources:
            return None
        
        # 查找共同媒体来源
        common_sources = set(event1.sources) & set(event2.sources)
        
        if not common_sources:
            return None
        
        # 计算媒体关联分数
        total_sources = len(set(event1.sources) | set(event2.sources))
        score = len(common_sources) / total_sources
        
        factors = {
            "common_sources": list(common_sources),
            "event1_sources": event1.sources,
            "event2_sources": event2.sources,
            "common_count": len(common_sources),
            "total_unique_sources": total_sources
        }
        
        description = f"事件有{len(common_sources)}个共同媒体来源"
        
        return EventCorrelation(
            event1_id=event1.id,
            event2_id=event2.id,
            correlation_type="media",
            correlation_score=score,
            correlation_factors=factors,
            description=description
        )
    
    def _extract_phenomenon_features(self, event: MysteryEvent) -> Dict[str, List[str]]:
        """提取现象特征"""
        features = defaultdict(list)
        
        # 合并所有文本内容
        text_content = f"{event.title} {event.description} {' '.join(event.phenomena)} {' '.join(event.keywords)}"
        text_lower = text_content.lower()
        
        # 检查各种现象特征
        for feature_type, keywords in self.phenomenon_features.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    features[feature_type].append(keyword)
        
        return dict(features)
    
    def _calculate_feature_similarity(self, features1: Dict[str, List[str]], 
                                    features2: Dict[str, List[str]]) -> float:
        """计算特征相似度"""
        all_features = set(features1.keys()) | set(features2.keys())
        
        if not all_features:
            return 0.0
        
        common_features = set(features1.keys()) & set(features2.keys())
        
        # 基础相似度：共同特征比例
        base_similarity = len(common_features) / len(all_features)
        
        # 详细相似度：考虑每个特征的具体匹配程度
        detailed_similarity = 0.0
        for feature in common_features:
            keywords1 = set(kw.lower() for kw in features1[feature])
            keywords2 = set(kw.lower() for kw in features2[feature])
            common_keywords = keywords1 & keywords2
            all_keywords = keywords1 | keywords2
            
            if all_keywords:
                detailed_similarity += len(common_keywords) / len(all_keywords)
        
        if common_features:
            detailed_similarity /= len(common_features)
        
        # 综合相似度
        return (base_similarity + detailed_similarity) / 2
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """使用Haversine公式计算两点间距离（公里）"""
        R = 6371  # 地球半径（公里）
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _limit_correlations_per_event(self, correlations: List[EventCorrelation]) -> List[EventCorrelation]:
        """限制每个事件的最大关联数"""
        event_correlation_count = defaultdict(int)
        filtered_correlations = []
        
        max_correlations = 10  # 每个事件最多10个关联
        
        for correlation in correlations:
            event1_count = event_correlation_count[correlation.event1_id]
            event2_count = event_correlation_count[correlation.event2_id]
            
            if event1_count < max_correlations and event2_count < max_correlations:
                filtered_correlations.append(correlation)
                event_correlation_count[correlation.event1_id] += 1
                event_correlation_count[correlation.event2_id] += 1
        
        return filtered_correlations
    
    def _build_correlation_network(self, correlations: List[EventCorrelation]) -> Dict[str, Any]:
        """构建关联网络"""
        nodes = set()
        edges = []
        
        for correlation in correlations:
            nodes.add(correlation.event1_id)
            nodes.add(correlation.event2_id)
            
            edges.append({
                "source": correlation.event1_id,
                "target": correlation.event2_id,
                "type": correlation.correlation_type,
                "weight": correlation.correlation_score,
                "description": correlation.description
            })
        
        # 计算网络统计信息
        node_degrees = defaultdict(int)
        for edge in edges:
            node_degrees[edge["source"]] += 1
            node_degrees[edge["target"]] += 1
        
        network_stats = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "average_degree": sum(node_degrees.values()) / len(nodes) if nodes else 0,
            "max_degree": max(node_degrees.values()) if node_degrees else 0,
            "correlation_types": list(set(edge["type"] for edge in edges))
        }
        
        return {
            "nodes": list(nodes),
            "edges": edges,
            "statistics": network_stats
        }
    
    def _generate_analysis_report(self, events: List[MysteryEvent], 
                                correlations: List[EventCorrelation],
                                network: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析报告"""
        # 按类型统计关联
        correlation_by_type = defaultdict(list)
        for correlation in correlations:
            correlation_by_type[correlation.correlation_type].append(correlation)
        
        # 按事件类型统计
        event_by_type = defaultdict(list)
        for event in events:
            event_by_type[event.event_type].append(event)
        
        # 找出关联度最高的事件
        event_correlation_scores = defaultdict(list)
        for correlation in correlations:
            event_correlation_scores[correlation.event1_id].append(correlation.correlation_score)
            event_correlation_scores[correlation.event2_id].append(correlation.correlation_score)
        
        highly_correlated_events = []
        for event_id, scores in event_correlation_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > 0.8:
                highly_correlated_events.append({
                    "event_id": event_id,
                    "average_correlation_score": avg_score,
                    "correlation_count": len(scores)
                })
        
        # 时间模式分析
        temporal_patterns = self._analyze_temporal_patterns(events, correlations)
        
        # 地理模式分析
        geographical_patterns = self._analyze_geographical_patterns(events, correlations)
        
        return {
            "summary": {
                "total_events": len(events),
                "total_correlations": len(correlations),
                "correlation_types": list(correlation_by_type.keys()),
                "event_types": list(event_by_type.keys())
            },
            "correlation_statistics": {
                correlation_type: {
                    "count": len(corrs),
                    "average_score": sum(c.correlation_score for c in corrs) / len(corrs) if corrs else 0,
                    "max_score": max(c.correlation_score for c in corrs) if corrs else 0
                }
                for correlation_type, corrs in correlation_by_type.items()
            },
            "highly_correlated_events": highly_correlated_events,
            "temporal_patterns": temporal_patterns,
            "geographical_patterns": geographical_patterns,
            "network_analysis": network["statistics"]
        }
    
    def _analyze_temporal_patterns(self, events: List[MysteryEvent], 
                                 correlations: List[EventCorrelation]) -> Dict[str, Any]:
        """分析时间模式"""
        temporal_correlations = [c for c in correlations if c.correlation_type == "temporal"]
        
        if not temporal_correlations:
            return {"pattern_detected": False}
        
        # 分析时间间隔分布
        time_intervals = []
        for correlation in temporal_correlations:
            factors = correlation.correlation_factors
            if "time_difference_days" in factors:
                time_intervals.append(factors["time_difference_days"])
        
        if time_intervals:
            avg_interval = sum(time_intervals) / len(time_intervals)
            return {
                "pattern_detected": True,
                "average_time_interval_days": avg_interval,
                "min_interval_days": min(time_intervals),
                "max_interval_days": max(time_intervals),
                "temporal_correlation_count": len(temporal_correlations)
            }
        
        return {"pattern_detected": False}
    
    def _analyze_geographical_patterns(self, events: List[MysteryEvent], 
                                     correlations: List[EventCorrelation]) -> Dict[str, Any]:
        """分析地理模式"""
        geographical_correlations = [c for c in correlations if c.correlation_type == "geographical"]
        
        if not geographical_correlations:
            return {"pattern_detected": False}
        
        # 分析距离分布
        distances = []
        for correlation in geographical_correlations:
            factors = correlation.correlation_factors
            if "distance_km" in factors:
                distances.append(factors["distance_km"])
        
        if distances:
            avg_distance = sum(distances) / len(distances)
            return {
                "pattern_detected": True,
                "average_distance_km": avg_distance,
                "min_distance_km": min(distances),
                "max_distance_km": max(distances),
                "geographical_correlation_count": len(geographical_correlations)
            }
        
        return {"pattern_detected": False}
    
    def _correlation_to_dict(self, correlation: EventCorrelation) -> Dict[str, Any]:
        """将关联对象转换为字典"""
        return {
            "event1_id": correlation.event1_id,
            "event2_id": correlation.event2_id,
            "correlation_type": correlation.correlation_type,
            "correlation_score": correlation.correlation_score,
            "correlation_factors": correlation.correlation_factors,
            "description": correlation.description
        }


@tool
@log_io
def analyze_event_correlations(
    events_data: str,
    correlation_types: Optional[List[str]] = None
) -> str:
    """分析神秘事件之间的关联关系
    
    Args:
        events_data: JSON格式的事件数据列表
        correlation_types: 要分析的关联类型列表，可选值：temporal, geographical, phenomenological, witness, media
    
    Returns:
        JSON格式的关联分析结果
    """
    try:
        analyzer = CorrelationAnalyzer()
        return analyzer._run(events_data, correlation_types)
    except Exception as e:
        error_msg = f"Failed to analyze event correlations. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def build_correlation_timeline(
    events_data: str,
    time_window_days: int = 30
) -> str:
    """构建关联事件时间线
    
    Args:
        events_data: JSON格式的事件数据列表
        time_window_days: 时间窗口（天）
    
    Returns:
        JSON格式的时间线数据
    """
    try:
        events_list = json.loads(events_data)
        analyzer = CorrelationAnalyzer()
        events = [analyzer._parse_event(event_data) for event_data in events_list]
        
        # 按时间排序
        events_with_time = [e for e in events if e.timestamp]
        events_with_time.sort(key=lambda x: x.timestamp)
        
        # 构建时间线
        timeline = []
        for event in events_with_time:
            timeline.append({
                "id": event.id,
                "title": event.title,
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "location": event.location
            })
        
        # 分析时间聚集
        clusters = []
        current_cluster = []
        
        for i, event in enumerate(events_with_time):
            if not current_cluster:
                current_cluster.append(event)
            else:
                time_diff = (event.timestamp - current_cluster[-1].timestamp).days
                if time_diff <= time_window_days:
                    current_cluster.append(event)
                else:
                    if len(current_cluster) > 1:
                        clusters.append({
                            "start_time": current_cluster[0].timestamp.isoformat(),
                            "end_time": current_cluster[-1].timestamp.isoformat(),
                            "event_count": len(current_cluster),
                            "event_ids": [e.id for e in current_cluster]
                        })
                    current_cluster = [event]
        
        # 处理最后一个聚集
        if len(current_cluster) > 1:
            clusters.append({
                "start_time": current_cluster[0].timestamp.isoformat(),
                "end_time": current_cluster[-1].timestamp.isoformat(),
                "event_count": len(current_cluster),
                "event_ids": [e.id for e in current_cluster]
            })
        
        return json.dumps({
            "timeline": timeline,
            "clusters": clusters,
            "total_events": len(timeline),
            "cluster_count": len(clusters)
        }, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Failed to build correlation timeline. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def analyze_location_patterns(
    events_data: str,
    radius_km: float = 100.0
) -> str:
    """分析地理位置模式
    
    Args:
        events_data: JSON格式的事件数据列表
        radius_km: 聚集半径（公里）
    
    Returns:
        JSON格式的地理模式分析结果
    """
    try:
        events_list = json.loads(events_data)
        analyzer = CorrelationAnalyzer()
        events = [analyzer._parse_event(event_data) for event_data in events_list]
        
        # 筛选有位置信息的事件
        events_with_location = [e for e in events if e.location]
        
        if not events_with_location:
            return json.dumps({"error": "No events with location information"}, ensure_ascii=False)
        
        # 地理聚集分析
        clusters = []
        processed_events = set()
        
        for i, event1 in enumerate(events_with_location):
            if event1.id in processed_events:
                continue
            
            cluster_events = [event1]
            processed_events.add(event1.id)
            
            for j, event2 in enumerate(events_with_location):
                if i != j and event2.id not in processed_events:
                    distance = analyzer._calculate_distance(
                        event1.location["lat"], event1.location["lon"],
                        event2.location["lat"], event2.location["lon"]
                    )
                    
                    if distance <= radius_km:
                        cluster_events.append(event2)
                        processed_events.add(event2.id)
            
            if len(cluster_events) > 1:
                # 计算聚集中心
                center_lat = sum(e.location["lat"] for e in cluster_events) / len(cluster_events)
                center_lon = sum(e.location["lon"] for e in cluster_events) / len(cluster_events)
                
                clusters.append({
                    "center": {"lat": center_lat, "lon": center_lon},
                    "event_count": len(cluster_events),
                    "event_ids": [e.id for e in cluster_events],
                    "radius_km": radius_km,
                    "events": [{
                        "id": e.id,
                        "title": e.title,
                        "location": e.location,
                        "event_type": e.event_type
                    } for e in cluster_events]
                })
        
        # 热点区域分析
        hotspots = [cluster for cluster in clusters if cluster["event_count"] >= 3]
        
        return json.dumps({
            "location_clusters": clusters,
            "hotspots": hotspots,
            "total_events_with_location": len(events_with_location),
            "cluster_count": len(clusters),
            "hotspot_count": len(hotspots)
        }, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Failed to analyze location patterns. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)