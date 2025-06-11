# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics

from langchain_core.tools import BaseTool, tool

from config.mystery_config import MysteryEventConfig, MysteryEventType
from tools.decorators import log_io

logger = logging.getLogger(__name__)


@dataclass
class TimelineEvent:
    """时间线事件"""
    id: str
    title: str
    description: str
    timestamp: datetime
    event_type: str
    location: Optional[Dict[str, float]] = None
    duration_minutes: Optional[int] = None
    witnesses: List[str] = None
    sources: List[str] = None
    
    def __post_init__(self):
        if self.witnesses is None:
            self.witnesses = []
        if self.sources is None:
            self.sources = []


@dataclass
class TimePattern:
    """时间模式"""
    pattern_type: str  # periodic, seasonal, clustered, random
    description: str
    confidence: float  # 0-1
    parameters: Dict[str, Any]
    events: List[str]  # event IDs


@dataclass
class TimePeriod:
    """时间段"""
    start_time: datetime
    end_time: datetime
    event_count: int
    event_ids: List[str]
    intensity: float  # events per day
    dominant_type: str


class TimelineAnalyzer(BaseTool):
    """时间线分析工具"""
    name: str = "timeline_analyzer"
    description: str = "Analyze temporal patterns and trends in mysterious events."
    
    def __init__(self, config: Optional[MysteryEventConfig] = None):
        """初始化时间线分析器
        
        Args:
            config: 神秘事件配置
        """
        super().__init__()
        self.config = config or MysteryEventConfig()
    
    def _run(self, events_data: str, analysis_types: List[str] = None) -> str:
        """运行时间线分析
        
        Args:
            events_data: JSON格式的事件数据列表
            analysis_types: 分析类型列表，可选值：patterns, trends, clusters, cycles
            
        Returns:
            JSON格式的时间线分析结果
        """
        try:
            # 解析事件数据
            events_list = json.loads(events_data)
            events = [self._parse_timeline_event(event_data) for event_data in events_list]
            
            # 筛选有时间信息的事件
            events_with_time = [e for e in events if e.timestamp]
            
            if not events_with_time:
                return json.dumps({"error": "No events with timestamp information"}, ensure_ascii=False)
            
            # 按时间排序
            events_with_time.sort(key=lambda x: x.timestamp)
            
            # 设置默认分析类型
            if analysis_types is None:
                analysis_types = ["patterns", "trends", "clusters", "cycles"]
            
            # 执行各种分析
            results = {
                "timeline": self._build_timeline(events_with_time),
                "summary": self._generate_timeline_summary(events_with_time)
            }
            
            if "patterns" in analysis_types:
                results["patterns"] = self._analyze_time_patterns(events_with_time)
            
            if "trends" in analysis_types:
                results["trends"] = self._analyze_trends(events_with_time)
            
            if "clusters" in analysis_types:
                results["clusters"] = self._analyze_time_clusters(events_with_time)
            
            if "cycles" in analysis_types:
                results["cycles"] = self._analyze_cycles(events_with_time)
            
            return json.dumps(results, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to analyze timeline. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _parse_timeline_event(self, event_data: Dict[str, Any]) -> TimelineEvent:
        """解析时间线事件数据"""
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
        
        return TimelineEvent(
            id=event_data.get("id", ""),
            title=event_data.get("title", ""),
            description=event_data.get("description", ""),
            timestamp=timestamp,
            event_type=event_data.get("event_type", ""),
            location=location,
            duration_minutes=event_data.get("duration_minutes"),
            witnesses=event_data.get("witnesses", []),
            sources=event_data.get("sources", [])
        )
    
    def _build_timeline(self, events: List[TimelineEvent]) -> List[Dict[str, Any]]:
        """构建时间线"""
        timeline = []
        
        for event in events:
            timeline_item = {
                "id": event.id,
                "title": event.title,
                "description": event.description[:200] + "..." if len(event.description) > 200 else event.description,
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "location": event.location,
                "duration_minutes": event.duration_minutes,
                "witness_count": len(event.witnesses),
                "source_count": len(event.sources)
            }
            timeline.append(timeline_item)
        
        return timeline
    
    def _generate_timeline_summary(self, events: List[TimelineEvent]) -> Dict[str, Any]:
        """生成时间线摘要"""
        if not events:
            return {}
        
        # 时间范围
        start_time = events[0].timestamp
        end_time = events[-1].timestamp
        time_span_days = (end_time - start_time).days
        
        # 事件类型统计
        type_counts = Counter(event.event_type for event in events)
        
        # 按年份统计
        yearly_counts = Counter(event.timestamp.year for event in events)
        
        # 按月份统计
        monthly_counts = Counter(event.timestamp.month for event in events)
        
        # 按星期统计
        weekday_counts = Counter(event.timestamp.weekday() for event in events)
        
        # 按小时统计
        hourly_counts = Counter(event.timestamp.hour for event in events)
        
        return {
            "total_events": len(events),
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "span_days": time_span_days
            },
            "event_types": dict(type_counts),
            "yearly_distribution": dict(yearly_counts),
            "monthly_distribution": dict(monthly_counts),
            "weekday_distribution": dict(weekday_counts),
            "hourly_distribution": dict(hourly_counts),
            "average_events_per_day": len(events) / max(time_span_days, 1),
            "most_common_type": type_counts.most_common(1)[0] if type_counts else None
        }
    
    def _analyze_time_patterns(self, events: List[TimelineEvent]) -> List[Dict[str, Any]]:
        """分析时间模式"""
        patterns = []
        
        # 分析周期性模式
        periodic_patterns = self._detect_periodic_patterns(events)
        patterns.extend(periodic_patterns)
        
        # 分析季节性模式
        seasonal_patterns = self._detect_seasonal_patterns(events)
        patterns.extend(seasonal_patterns)
        
        # 分析聚集模式
        cluster_patterns = self._detect_cluster_patterns(events)
        patterns.extend(cluster_patterns)
        
        return [self._pattern_to_dict(pattern) for pattern in patterns]
    
    def _detect_periodic_patterns(self, events: List[TimelineEvent]) -> List[TimePattern]:
        """检测周期性模式"""
        patterns = []
        
        # 按事件类型分组
        events_by_type = defaultdict(list)
        for event in events:
            events_by_type[event.event_type].append(event)
        
        for event_type, type_events in events_by_type.items():
            if len(type_events) < 3:
                continue
            
            # 计算事件间隔
            intervals = []
            for i in range(1, len(type_events)):
                interval = (type_events[i].timestamp - type_events[i-1].timestamp).days
                intervals.append(interval)
            
            if not intervals:
                continue
            
            # 检查是否存在周期性
            avg_interval = statistics.mean(intervals)
            std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
            
            # 如果标准差相对较小，可能存在周期性
            if std_interval < avg_interval * 0.3 and avg_interval > 1:
                confidence = 1.0 - (std_interval / avg_interval)
                
                pattern = TimePattern(
                    pattern_type="periodic",
                    description=f"{event_type}事件平均每{avg_interval:.1f}天发生一次",
                    confidence=confidence,
                    parameters={
                        "average_interval_days": avg_interval,
                        "interval_std_dev": std_interval,
                        "event_type": event_type
                    },
                    events=[e.id for e in type_events]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_seasonal_patterns(self, events: List[TimelineEvent]) -> List[TimePattern]:
        """检测季节性模式"""
        patterns = []
        
        # 按月份统计事件
        monthly_counts = Counter(event.timestamp.month for event in events)
        
        if len(monthly_counts) < 3:
            return patterns
        
        # 计算月份分布的方差
        counts = list(monthly_counts.values())
        avg_count = statistics.mean(counts)
        
        if avg_count == 0:
            return patterns
        
        # 找出明显高于平均值的月份
        peak_months = []
        for month, count in monthly_counts.items():
            if count > avg_count * 1.5:
                peak_months.append(month)
        
        if peak_months:
            month_names = {
                1: "一月", 2: "二月", 3: "三月", 4: "四月", 5: "五月", 6: "六月",
                7: "七月", 8: "八月", 9: "九月", 10: "十月", 11: "十一月", 12: "十二月"
            }
            
            peak_month_names = [month_names[m] for m in peak_months]
            
            # 计算置信度
            max_count = max(counts)
            confidence = min(1.0, (max_count - avg_count) / avg_count)
            
            pattern = TimePattern(
                pattern_type="seasonal",
                description=f"事件在{', '.join(peak_month_names)}较为频繁",
                confidence=confidence,
                parameters={
                    "peak_months": peak_months,
                    "monthly_distribution": dict(monthly_counts),
                    "average_monthly_count": avg_count
                },
                events=[e.id for e in events if e.timestamp.month in peak_months]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _detect_cluster_patterns(self, events: List[TimelineEvent]) -> List[TimePattern]:
        """检测聚集模式"""
        patterns = []
        
        if len(events) < 3:
            return patterns
        
        # 计算事件间的时间间隔
        intervals = []
        for i in range(1, len(events)):
            interval = (events[i].timestamp - events[i-1].timestamp).total_seconds() / 3600  # 小时
            intervals.append(interval)
        
        # 找出短时间间隔（可能的聚集）
        short_intervals = [i for i in intervals if i <= 24]  # 24小时内
        
        if len(short_intervals) >= len(intervals) * 0.3:  # 30%以上的间隔很短
            avg_short_interval = statistics.mean(short_intervals)
            confidence = len(short_intervals) / len(intervals)
            
            pattern = TimePattern(
                pattern_type="clustered",
                description=f"事件倾向于在短时间内聚集发生，平均间隔{avg_short_interval:.1f}小时",
                confidence=confidence,
                parameters={
                    "average_cluster_interval_hours": avg_short_interval,
                    "cluster_ratio": confidence,
                    "total_short_intervals": len(short_intervals)
                },
                events=[e.id for e in events]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _analyze_trends(self, events: List[TimelineEvent]) -> Dict[str, Any]:
        """分析趋势"""
        if len(events) < 2:
            return {"trend_detected": False}
        
        # 按年份统计
        yearly_counts = Counter(event.timestamp.year for event in events)
        years = sorted(yearly_counts.keys())
        
        if len(years) < 2:
            return {"trend_detected": False}
        
        counts = [yearly_counts[year] for year in years]
        
        # 计算线性趋势
        n = len(years)
        sum_x = sum(range(n))
        sum_y = sum(counts)
        sum_xy = sum(i * counts[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))
        
        # 线性回归斜率
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # 判断趋势方向
        if abs(slope) < 0.1:
            trend_type = "stable"
            trend_description = "事件数量保持相对稳定"
        elif slope > 0:
            trend_type = "increasing"
            trend_description = f"事件数量呈上升趋势，年均增长{slope:.1f}起"
        else:
            trend_type = "decreasing"
            trend_description = f"事件数量呈下降趋势，年均减少{abs(slope):.1f}起"
        
        # 计算相关系数
        mean_x = sum_x / n
        mean_y = sum_y / n
        
        numerator = sum((i - mean_x) * (counts[i] - mean_y) for i in range(n))
        denominator_x = sum((i - mean_x) ** 2 for i in range(n))
        denominator_y = sum((counts[i] - mean_y) ** 2 for i in range(n))
        
        correlation = 0
        if denominator_x > 0 and denominator_y > 0:
            correlation = numerator / (denominator_x * denominator_y) ** 0.5
        
        return {
            "trend_detected": True,
            "trend_type": trend_type,
            "description": trend_description,
            "slope": slope,
            "correlation_coefficient": correlation,
            "yearly_data": {
                "years": years,
                "counts": counts
            },
            "confidence": abs(correlation)
        }
    
    def _analyze_time_clusters(self, events: List[TimelineEvent]) -> List[Dict[str, Any]]:
        """分析时间聚集"""
        clusters = []
        
        if len(events) < 2:
            return clusters
        
        # 设置聚集时间窗口（7天）
        cluster_window = timedelta(days=7)
        
        current_cluster = [events[0]]
        
        for i in range(1, len(events)):
            time_diff = events[i].timestamp - current_cluster[-1].timestamp
            
            if time_diff <= cluster_window:
                current_cluster.append(events[i])
            else:
                # 保存当前聚集（如果有多个事件）
                if len(current_cluster) > 1:
                    cluster_info = self._create_cluster_info(current_cluster)
                    clusters.append(cluster_info)
                
                # 开始新的聚集
                current_cluster = [events[i]]
        
        # 处理最后一个聚集
        if len(current_cluster) > 1:
            cluster_info = self._create_cluster_info(current_cluster)
            clusters.append(cluster_info)
        
        return clusters
    
    def _create_cluster_info(self, cluster_events: List[TimelineEvent]) -> Dict[str, Any]:
        """创建聚集信息"""
        start_time = cluster_events[0].timestamp
        end_time = cluster_events[-1].timestamp
        duration_days = (end_time - start_time).days
        
        # 统计事件类型
        type_counts = Counter(event.event_type for event in cluster_events)
        
        # 计算强度
        intensity = len(cluster_events) / max(duration_days, 1)
        
        return {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_days": duration_days,
            "event_count": len(cluster_events),
            "intensity": intensity,
            "event_types": dict(type_counts),
            "dominant_type": type_counts.most_common(1)[0][0] if type_counts else None,
            "event_ids": [event.id for event in cluster_events]
        }
    
    def _analyze_cycles(self, events: List[TimelineEvent]) -> Dict[str, Any]:
        """分析周期性"""
        if len(events) < 4:
            return {"cycles_detected": False}
        
        # 分析不同时间尺度的周期性
        cycles = {}
        
        # 周内周期（星期几）
        weekday_counts = Counter(event.timestamp.weekday() for event in events)
        weekday_variance = statistics.variance(weekday_counts.values()) if len(weekday_counts) > 1 else 0
        
        if weekday_variance > 0:
            cycles["weekly"] = {
                "detected": True,
                "distribution": dict(weekday_counts),
                "variance": weekday_variance,
                "peak_weekday": max(weekday_counts, key=weekday_counts.get)
            }
        
        # 月内周期（日期）
        day_counts = Counter(event.timestamp.day for event in events)
        day_variance = statistics.variance(day_counts.values()) if len(day_counts) > 1 else 0
        
        if day_variance > 0:
            cycles["monthly"] = {
                "detected": True,
                "distribution": dict(day_counts),
                "variance": day_variance,
                "peak_day": max(day_counts, key=day_counts.get)
            }
        
        # 年内周期（月份）
        month_counts = Counter(event.timestamp.month for event in events)
        month_variance = statistics.variance(month_counts.values()) if len(month_counts) > 1 else 0
        
        if month_variance > 0:
            cycles["yearly"] = {
                "detected": True,
                "distribution": dict(month_counts),
                "variance": month_variance,
                "peak_month": max(month_counts, key=month_counts.get)
            }
        
        return {
            "cycles_detected": len(cycles) > 0,
            "cycles": cycles,
            "cycle_count": len(cycles)
        }
    
    def _pattern_to_dict(self, pattern: TimePattern) -> Dict[str, Any]:
        """将模式对象转换为字典"""
        return {
            "pattern_type": pattern.pattern_type,
            "description": pattern.description,
            "confidence": pattern.confidence,
            "parameters": pattern.parameters,
            "event_count": len(pattern.events),
            "event_ids": pattern.events
        }


@tool
@log_io
def analyze_timeline_patterns(
    events_data: str,
    analysis_types: Optional[List[str]] = None
) -> str:
    """分析神秘事件的时间线模式
    
    Args:
        events_data: JSON格式的事件数据列表
        analysis_types: 分析类型列表，可选值：patterns, trends, clusters, cycles
    
    Returns:
        JSON格式的时间线分析结果
    """
    try:
        analyzer = TimelineAnalyzer()
        return analyzer._run(events_data, analysis_types)
    except Exception as e:
        error_msg = f"Failed to analyze timeline patterns. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def generate_timeline_report(
    events_data: str,
    include_predictions: bool = False
) -> str:
    """生成时间线分析报告
    
    Args:
        events_data: JSON格式的事件数据列表
        include_predictions: 是否包含预测分析
    
    Returns:
        JSON格式的时间线报告
    """
    try:
        analyzer = TimelineAnalyzer()
        
        # 执行完整分析
        analysis_result = analyzer._run(events_data, ["patterns", "trends", "clusters", "cycles"])
        analysis_data = json.loads(analysis_result)
        
        if "error" in analysis_data:
            return analysis_result
        
        # 生成报告
        report = {
            "report_title": "神秘事件时间线分析报告",
            "generated_at": datetime.now().isoformat(),
            "executive_summary": _generate_executive_summary(analysis_data),
            "detailed_analysis": analysis_data,
            "key_findings": _extract_key_findings(analysis_data),
            "recommendations": _generate_recommendations(analysis_data)
        }
        
        if include_predictions:
            report["predictions"] = _generate_predictions(analysis_data)
        
        return json.dumps(report, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Failed to generate timeline report. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


def _generate_executive_summary(analysis_data: Dict[str, Any]) -> str:
    """生成执行摘要"""
    summary_parts = []
    
    # 基本统计
    if "summary" in analysis_data:
        summary = analysis_data["summary"]
        total_events = summary.get("total_events", 0)
        time_range = summary.get("time_range", {})
        span_days = time_range.get("span_days", 0)
        
        summary_parts.append(f"本报告分析了{total_events}起神秘事件，时间跨度{span_days}天。")
        
        if "most_common_type" in summary and summary["most_common_type"]:
            most_common = summary["most_common_type"]
            summary_parts.append(f"最常见的事件类型是{most_common[0]}，共{most_common[1]}起。")
    
    # 趋势分析
    if "trends" in analysis_data and analysis_data["trends"].get("trend_detected"):
        trend = analysis_data["trends"]
        summary_parts.append(trend.get("description", ""))
    
    # 模式分析
    if "patterns" in analysis_data and analysis_data["patterns"]:
        pattern_count = len(analysis_data["patterns"])
        summary_parts.append(f"检测到{pattern_count}种时间模式。")
    
    # 聚集分析
    if "clusters" in analysis_data and analysis_data["clusters"]:
        cluster_count = len(analysis_data["clusters"])
        summary_parts.append(f"发现{cluster_count}个时间聚集现象。")
    
    return " ".join(summary_parts)


def _extract_key_findings(analysis_data: Dict[str, Any]) -> List[str]:
    """提取关键发现"""
    findings = []
    
    # 从模式中提取发现
    if "patterns" in analysis_data:
        for pattern in analysis_data["patterns"]:
            if pattern.get("confidence", 0) > 0.7:
                findings.append(f"高置信度模式：{pattern.get('description', '')}")
    
    # 从趋势中提取发现
    if "trends" in analysis_data and analysis_data["trends"].get("trend_detected"):
        trend = analysis_data["trends"]
        if abs(trend.get("correlation_coefficient", 0)) > 0.7:
            findings.append(f"强趋势：{trend.get('description', '')}")
    
    # 从周期中提取发现
    if "cycles" in analysis_data and analysis_data["cycles"].get("cycles_detected"):
        cycles = analysis_data["cycles"].get("cycles", {})
        for cycle_type, cycle_data in cycles.items():
            if cycle_data.get("variance", 0) > 1:
                findings.append(f"检测到{cycle_type}周期性变化")
    
    return findings


def _generate_recommendations(analysis_data: Dict[str, Any]) -> List[str]:
    """生成建议"""
    recommendations = []
    
    # 基于模式的建议
    if "patterns" in analysis_data:
        periodic_patterns = [p for p in analysis_data["patterns"] if p.get("pattern_type") == "periodic"]
        if periodic_patterns:
            recommendations.append("建议重点关注周期性事件的预测和监控")
        
        cluster_patterns = [p for p in analysis_data["patterns"] if p.get("pattern_type") == "clustered"]
        if cluster_patterns:
            recommendations.append("建议在事件聚集期间加强监测和数据收集")
    
    # 基于趋势的建议
    if "trends" in analysis_data and analysis_data["trends"].get("trend_detected"):
        trend_type = analysis_data["trends"].get("trend_type")
        if trend_type == "increasing":
            recommendations.append("事件数量呈上升趋势，建议增加研究资源投入")
        elif trend_type == "decreasing":
            recommendations.append("事件数量呈下降趋势，可能需要调整数据收集策略")
    
    # 基于聚集的建议
    if "clusters" in analysis_data and len(analysis_data["clusters"]) > 0:
        recommendations.append("发现时间聚集现象，建议深入研究聚集期间的共同因素")
    
    return recommendations


def _generate_predictions(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """生成预测分析"""
    predictions = {
        "prediction_confidence": "low",
        "predictions": []
    }
    
    # 基于周期性模式的预测
    if "patterns" in analysis_data:
        periodic_patterns = [p for p in analysis_data["patterns"] 
                           if p.get("pattern_type") == "periodic" and p.get("confidence", 0) > 0.8]
        
        for pattern in periodic_patterns:
            params = pattern.get("parameters", {})
            interval = params.get("average_interval_days")
            if interval:
                next_predicted = datetime.now() + timedelta(days=interval)
                predictions["predictions"].append({
                    "type": "periodic_event",
                    "description": f"基于周期性模式，预测下次{params.get('event_type', '事件')}可能在{next_predicted.strftime('%Y-%m-%d')}左右发生",
                    "confidence": pattern.get("confidence", 0),
                    "predicted_date": next_predicted.isoformat()
                })
    
    if predictions["predictions"]:
        predictions["prediction_confidence"] = "medium"
    
    return predictions