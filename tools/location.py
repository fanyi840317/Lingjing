# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import json
import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics

from langchain_core.tools import BaseTool, tool

from config.mystery_config import MysteryEventConfig, MysteryEventType
from tools.decorators import log_io

logger = logging.getLogger(__name__)


@dataclass
class LocationEvent:
    """地理位置事件"""
    id: str
    title: str
    description: str
    location: Dict[str, float]  # {"lat": float, "lon": float}
    event_type: str
    timestamp: Optional[str] = None
    altitude: Optional[float] = None
    accuracy: Optional[float] = None  # 位置精度（米）
    address: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None


@dataclass
class LocationCluster:
    """地理聚集"""
    id: str
    center: Dict[str, float]
    radius_km: float
    event_count: int
    event_ids: List[str]
    dominant_type: str
    density: float  # events per km²
    bounding_box: Dict[str, float]  # {"min_lat", "max_lat", "min_lon", "max_lon"}


@dataclass
class LocationPattern:
    """地理模式"""
    pattern_type: str  # linear, circular, grid, random, coastal, mountain
    description: str
    confidence: float
    parameters: Dict[str, Any]
    event_ids: List[str]


class LocationAnalyzer(BaseTool):
    """地理位置分析工具"""
    name = "location_analyzer"
    description = "Analyze geographical patterns and distributions of mysterious events."
    
    def __init__(self, config: Optional[MysteryEventConfig] = None):
        """初始化地理位置分析器
        
        Args:
            config: 神秘事件配置
        """
        super().__init__()
        self.config = config or MysteryEventConfig()
        
        # 地理特征关键词
        self.geographical_features = {
            "water": ["海", "湖", "河", "江", "溪", "海洋", "湖泊", "river", "lake", "sea", "ocean", "stream"],
            "mountain": ["山", "峰", "岭", "丘", "高原", "mountain", "hill", "peak", "ridge", "plateau"],
            "forest": ["森林", "树林", "丛林", "林区", "forest", "woods", "jungle", "woodland"],
            "desert": ["沙漠", "戈壁", "荒漠", "desert", "wasteland"],
            "urban": ["城市", "市区", "城镇", "都市", "city", "urban", "town", "metropolitan"],
            "rural": ["农村", "乡村", "田野", "郊区", "rural", "countryside", "farmland", "suburban"],
            "coastal": ["海岸", "海滨", "沿海", "海边", "coast", "coastal", "seaside", "shore"]
        }
    
    def _run(self, events_data: str, analysis_types: List[str] = None) -> str:
        """运行地理位置分析
        
        Args:
            events_data: JSON格式的事件数据列表
            analysis_types: 分析类型列表，可选值：clusters, patterns, hotspots, distribution
            
        Returns:
            JSON格式的地理分析结果
        """
        try:
            # 解析事件数据
            events_list = json.loads(events_data)
            events = [self._parse_location_event(event_data) for event_data in events_list]
            
            # 筛选有位置信息的事件
            events_with_location = [e for e in events if e.location]
            
            if not events_with_location:
                return json.dumps({"error": "No events with location information"}, ensure_ascii=False)
            
            # 设置默认分析类型
            if analysis_types is None:
                analysis_types = ["clusters", "patterns", "hotspots", "distribution"]
            
            # 执行各种分析
            results = {
                "summary": self._generate_location_summary(events_with_location)
            }
            
            if "clusters" in analysis_types:
                results["clusters"] = self._analyze_location_clusters(events_with_location)
            
            if "patterns" in analysis_types:
                results["patterns"] = self._analyze_location_patterns(events_with_location)
            
            if "hotspots" in analysis_types:
                results["hotspots"] = self._analyze_hotspots(events_with_location)
            
            if "distribution" in analysis_types:
                results["distribution"] = self._analyze_distribution(events_with_location)
            
            return json.dumps(results, ensure_ascii=False)
            
        except Exception as e:
            error_msg = f"Failed to analyze locations. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _parse_location_event(self, event_data: Dict[str, Any]) -> LocationEvent:
        """解析地理位置事件数据"""
        location = None
        if "location" in event_data and event_data["location"]:
            loc_data = event_data["location"]
            if isinstance(loc_data, dict) and "lat" in loc_data and "lon" in loc_data:
                location = {"lat": float(loc_data["lat"]), "lon": float(loc_data["lon"])}
        
        return LocationEvent(
            id=event_data.get("id", ""),
            title=event_data.get("title", ""),
            description=event_data.get("description", ""),
            location=location,
            event_type=event_data.get("event_type", ""),
            timestamp=event_data.get("timestamp"),
            altitude=event_data.get("altitude"),
            accuracy=event_data.get("accuracy"),
            address=event_data.get("address"),
            country=event_data.get("country"),
            region=event_data.get("region"),
            city=event_data.get("city")
        )
    
    def _generate_location_summary(self, events: List[LocationEvent]) -> Dict[str, Any]:
        """生成地理位置摘要"""
        if not events:
            return {}
        
        # 计算边界框
        lats = [event.location["lat"] for event in events]
        lons = [event.location["lon"] for event in events]
        
        bounding_box = {
            "min_lat": min(lats),
            "max_lat": max(lats),
            "min_lon": min(lons),
            "max_lon": max(lons)
        }
        
        # 计算中心点
        center = {
            "lat": sum(lats) / len(lats),
            "lon": sum(lons) / len(lons)
        }
        
        # 计算覆盖范围
        max_distance = 0
        for i, event1 in enumerate(events):
            for j, event2 in enumerate(events[i+1:], i+1):
                distance = self._calculate_distance(
                    event1.location["lat"], event1.location["lon"],
                    event2.location["lat"], event2.location["lon"]
                )
                max_distance = max(max_distance, distance)
        
        # 按事件类型统计
        type_counts = Counter(event.event_type for event in events)
        
        # 按国家/地区统计
        country_counts = Counter(event.country for event in events if event.country)
        region_counts = Counter(event.region for event in events if event.region)
        city_counts = Counter(event.city for event in events if event.city)
        
        return {
            "total_events": len(events),
            "bounding_box": bounding_box,
            "center_point": center,
            "max_distance_km": max_distance,
            "coverage_area_km2": self._calculate_area(bounding_box),
            "event_types": dict(type_counts),
            "countries": dict(country_counts),
            "regions": dict(region_counts),
            "cities": dict(city_counts),
            "density_per_1000km2": len(events) / max(self._calculate_area(bounding_box) / 1000, 1)
        }
    
    def _analyze_location_clusters(self, events: List[LocationEvent]) -> List[Dict[str, Any]]:
        """分析地理聚集"""
        if len(events) < 2:
            return []
        
        # 使用DBSCAN类似的聚集算法
        clusters = []
        processed_events = set()
        cluster_radius = self.config.location_radius_km
        
        for i, event in enumerate(events):
            if event.id in processed_events:
                continue
            
            # 找到邻近事件
            cluster_events = [event]
            processed_events.add(event.id)
            
            for j, other_event in enumerate(events):
                if i != j and other_event.id not in processed_events:
                    distance = self._calculate_distance(
                        event.location["lat"], event.location["lon"],
                        other_event.location["lat"], other_event.location["lon"]
                    )
                    
                    if distance <= cluster_radius:
                        cluster_events.append(other_event)
                        processed_events.add(other_event.id)
            
            # 如果聚集包含多个事件，创建聚集对象
            if len(cluster_events) > 1:
                cluster = self._create_location_cluster(cluster_events, len(clusters))
                clusters.append(self._cluster_to_dict(cluster))
        
        # 按事件数量排序
        clusters.sort(key=lambda x: x["event_count"], reverse=True)
        
        return clusters
    
    def _create_location_cluster(self, events: List[LocationEvent], cluster_id: int) -> LocationCluster:
        """创建地理聚集对象"""
        # 计算中心点
        center_lat = sum(event.location["lat"] for event in events) / len(events)
        center_lon = sum(event.location["lon"] for event in events) / len(events)
        center = {"lat": center_lat, "lon": center_lon}
        
        # 计算半径（到中心点的最大距离）
        max_radius = 0
        for event in events:
            distance = self._calculate_distance(
                center_lat, center_lon,
                event.location["lat"], event.location["lon"]
            )
            max_radius = max(max_radius, distance)
        
        # 计算边界框
        lats = [event.location["lat"] for event in events]
        lons = [event.location["lon"] for event in events]
        bounding_box = {
            "min_lat": min(lats),
            "max_lat": max(lats),
            "min_lon": min(lons),
            "max_lon": max(lons)
        }
        
        # 统计主要事件类型
        type_counts = Counter(event.event_type for event in events)
        dominant_type = type_counts.most_common(1)[0][0] if type_counts else "unknown"
        
        # 计算密度
        area = math.pi * (max_radius ** 2) if max_radius > 0 else 1
        density = len(events) / area
        
        return LocationCluster(
            id=f"cluster_{cluster_id}",
            center=center,
            radius_km=max_radius,
            event_count=len(events),
            event_ids=[event.id for event in events],
            dominant_type=dominant_type,
            density=density,
            bounding_box=bounding_box
        )
    
    def _analyze_location_patterns(self, events: List[LocationEvent]) -> List[Dict[str, Any]]:
        """分析地理模式"""
        patterns = []
        
        if len(events) < 3:
            return patterns
        
        # 分析线性模式
        linear_patterns = self._detect_linear_patterns(events)
        patterns.extend(linear_patterns)
        
        # 分析圆形模式
        circular_patterns = self._detect_circular_patterns(events)
        patterns.extend(circular_patterns)
        
        # 分析地理特征关联
        feature_patterns = self._detect_feature_patterns(events)
        patterns.extend(feature_patterns)
        
        return [self._pattern_to_dict(pattern) for pattern in patterns]
    
    def _detect_linear_patterns(self, events: List[LocationEvent]) -> List[LocationPattern]:
        """检测线性模式"""
        patterns = []
        
        if len(events) < 3:
            return patterns
        
        # 尝试拟合直线
        points = [(event.location["lat"], event.location["lon"]) for event in events]
        
        # 计算最佳拟合直线
        n = len(points)
        sum_x = sum(p[0] for p in points)
        sum_y = sum(p[1] for p in points)
        sum_xy = sum(p[0] * p[1] for p in points)
        sum_x2 = sum(p[0] ** 2 for p in points)
        
        # 线性回归
        if n * sum_x2 - sum_x ** 2 != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            intercept = (sum_y - slope * sum_x) / n
            
            # 计算拟合度（R²）
            mean_y = sum_y / n
            ss_tot = sum((p[1] - mean_y) ** 2 for p in points)
            ss_res = sum((p[1] - (slope * p[0] + intercept)) ** 2 for p in points)
            
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # 如果拟合度较高，认为存在线性模式
            if r_squared > 0.7:
                pattern = LocationPattern(
                    pattern_type="linear",
                    description=f"事件呈线性分布，拟合度R²={r_squared:.3f}",
                    confidence=r_squared,
                    parameters={
                        "slope": slope,
                        "intercept": intercept,
                        "r_squared": r_squared,
                        "direction": "northeast" if slope > 0 else "southeast"
                    },
                    event_ids=[event.id for event in events]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_circular_patterns(self, events: List[LocationEvent]) -> List[LocationPattern]:
        """检测圆形模式"""
        patterns = []
        
        if len(events) < 4:
            return patterns
        
        # 计算几何中心
        center_lat = sum(event.location["lat"] for event in events) / len(events)
        center_lon = sum(event.location["lon"] for event in events) / len(events)
        
        # 计算每个点到中心的距离
        distances = []
        for event in events:
            distance = self._calculate_distance(
                center_lat, center_lon,
                event.location["lat"], event.location["lon"]
            )
            distances.append(distance)
        
        # 检查距离的一致性
        if distances:
            mean_distance = statistics.mean(distances)
            std_distance = statistics.stdev(distances) if len(distances) > 1 else 0
            
            # 如果标准差相对较小，可能存在圆形模式
            if mean_distance > 0 and std_distance / mean_distance < 0.3:
                confidence = 1.0 - (std_distance / mean_distance)
                
                pattern = LocationPattern(
                    pattern_type="circular",
                    description=f"事件围绕中心点({center_lat:.4f}, {center_lon:.4f})呈圆形分布",
                    confidence=confidence,
                    parameters={
                        "center_lat": center_lat,
                        "center_lon": center_lon,
                        "average_radius_km": mean_distance,
                        "radius_std_dev": std_distance
                    },
                    event_ids=[event.id for event in events]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_feature_patterns(self, events: List[LocationEvent]) -> List[LocationPattern]:
        """检测地理特征模式"""
        patterns = []
        
        # 分析事件描述中的地理特征
        feature_events = defaultdict(list)
        
        for event in events:
            text_content = f"{event.title} {event.description} {event.address or ''}".lower()
            
            for feature_type, keywords in self.geographical_features.items():
                for keyword in keywords:
                    if keyword.lower() in text_content:
                        feature_events[feature_type].append(event)
                        break
        
        # 为每种地理特征创建模式
        for feature_type, feature_event_list in feature_events.items():
            if len(feature_event_list) >= 3:  # 至少3个事件
                total_events = len(events)
                feature_ratio = len(feature_event_list) / total_events
                
                if feature_ratio > 0.3:  # 30%以上的事件与该特征相关
                    pattern = LocationPattern(
                        pattern_type="geographical_feature",
                        description=f"{len(feature_event_list)}个事件与{feature_type}地理特征相关",
                        confidence=feature_ratio,
                        parameters={
                            "feature_type": feature_type,
                            "event_count": len(feature_event_list),
                            "feature_ratio": feature_ratio
                        },
                        event_ids=[event.id for event in feature_event_list]
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _analyze_hotspots(self, events: List[LocationEvent]) -> List[Dict[str, Any]]:
        """分析热点区域"""
        hotspots = []
        
        if len(events) < 3:
            return hotspots
        
        # 使用网格方法识别热点
        grid_size = 0.1  # 0.1度网格（约11km）
        grid_events = defaultdict(list)
        
        # 将事件分配到网格
        for event in events:
            grid_lat = round(event.location["lat"] / grid_size) * grid_size
            grid_lon = round(event.location["lon"] / grid_size) * grid_size
            grid_key = (grid_lat, grid_lon)
            grid_events[grid_key].append(event)
        
        # 找出事件密度高的网格
        avg_events_per_grid = len(events) / len(grid_events) if grid_events else 0
        
        for grid_key, grid_event_list in grid_events.items():
            if len(grid_event_list) >= max(3, avg_events_per_grid * 2):  # 高于平均密度2倍
                grid_lat, grid_lon = grid_key
                
                # 计算热点统计信息
                type_counts = Counter(event.event_type for event in grid_event_list)
                
                hotspot = {
                    "id": f"hotspot_{len(hotspots)}",
                    "center": {"lat": grid_lat, "lon": grid_lon},
                    "grid_size_degrees": grid_size,
                    "event_count": len(grid_event_list),
                    "density_score": len(grid_event_list) / avg_events_per_grid if avg_events_per_grid > 0 else 0,
                    "event_types": dict(type_counts),
                    "dominant_type": type_counts.most_common(1)[0][0] if type_counts else None,
                    "event_ids": [event.id for event in grid_event_list]
                }
                hotspots.append(hotspot)
        
        # 按密度分数排序
        hotspots.sort(key=lambda x: x["density_score"], reverse=True)
        
        return hotspots
    
    def _analyze_distribution(self, events: List[LocationEvent]) -> Dict[str, Any]:
        """分析地理分布"""
        if not events:
            return {}
        
        # 计算分布统计
        lats = [event.location["lat"] for event in events]
        lons = [event.location["lon"] for event in events]
        
        lat_stats = {
            "mean": statistics.mean(lats),
            "median": statistics.median(lats),
            "std_dev": statistics.stdev(lats) if len(lats) > 1 else 0,
            "range": max(lats) - min(lats)
        }
        
        lon_stats = {
            "mean": statistics.mean(lons),
            "median": statistics.median(lons),
            "std_dev": statistics.stdev(lons) if len(lons) > 1 else 0,
            "range": max(lons) - min(lons)
        }
        
        # 计算分布类型
        distribution_type = self._classify_distribution(events)
        
        # 计算最近邻距离
        nearest_distances = []
        for i, event1 in enumerate(events):
            min_distance = float('inf')
            for j, event2 in enumerate(events):
                if i != j:
                    distance = self._calculate_distance(
                        event1.location["lat"], event1.location["lon"],
                        event2.location["lat"], event2.location["lon"]
                    )
                    min_distance = min(min_distance, distance)
            if min_distance != float('inf'):
                nearest_distances.append(min_distance)
        
        nearest_neighbor_stats = {}
        if nearest_distances:
            nearest_neighbor_stats = {
                "mean": statistics.mean(nearest_distances),
                "median": statistics.median(nearest_distances),
                "std_dev": statistics.stdev(nearest_distances) if len(nearest_distances) > 1 else 0,
                "min": min(nearest_distances),
                "max": max(nearest_distances)
            }
        
        return {
            "distribution_type": distribution_type,
            "latitude_statistics": lat_stats,
            "longitude_statistics": lon_stats,
            "nearest_neighbor_statistics": nearest_neighbor_stats,
            "spatial_autocorrelation": self._calculate_spatial_autocorrelation(events)
        }
    
    def _classify_distribution(self, events: List[LocationEvent]) -> str:
        """分类分布类型"""
        if len(events) < 3:
            return "insufficient_data"
        
        # 计算最近邻距离的变异系数
        nearest_distances = []
        for i, event1 in enumerate(events):
            min_distance = float('inf')
            for j, event2 in enumerate(events):
                if i != j:
                    distance = self._calculate_distance(
                        event1.location["lat"], event1.location["lon"],
                        event2.location["lat"], event2.location["lon"]
                    )
                    min_distance = min(min_distance, distance)
            if min_distance != float('inf'):
                nearest_distances.append(min_distance)
        
        if not nearest_distances:
            return "unknown"
        
        mean_distance = statistics.mean(nearest_distances)
        std_distance = statistics.stdev(nearest_distances) if len(nearest_distances) > 1 else 0
        
        if mean_distance == 0:
            return "clustered"
        
        cv = std_distance / mean_distance  # 变异系数
        
        if cv < 0.5:
            return "regular"  # 规律分布
        elif cv > 1.5:
            return "clustered"  # 聚集分布
        else:
            return "random"  # 随机分布
    
    def _calculate_spatial_autocorrelation(self, events: List[LocationEvent]) -> float:
        """计算空间自相关性（简化版Moran's I）"""
        if len(events) < 3:
            return 0.0
        
        n = len(events)
        
        # 构建权重矩阵（基于距离的倒数）
        weights = []
        for i in range(n):
            weight_row = []
            for j in range(n):
                if i == j:
                    weight_row.append(0)
                else:
                    distance = self._calculate_distance(
                        events[i].location["lat"], events[i].location["lon"],
                        events[j].location["lat"], events[j].location["lon"]
                    )
                    weight = 1 / (distance + 1)  # 避免除零
                    weight_row.append(weight)
            weights.append(weight_row)
        
        # 计算Moran's I（简化版）
        # 这里使用事件类型的数值编码作为属性值
        type_to_num = {event_type: i for i, event_type in enumerate(set(event.event_type for event in events))}
        values = [type_to_num[event.event_type] for event in events]
        
        mean_value = sum(values) / n
        
        numerator = 0
        denominator = 0
        weight_sum = 0
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    numerator += weights[i][j] * (values[i] - mean_value) * (values[j] - mean_value)
                    weight_sum += weights[i][j]
            denominator += (values[i] - mean_value) ** 2
        
        if denominator == 0 or weight_sum == 0:
            return 0.0
        
        moran_i = (n / weight_sum) * (numerator / denominator)
        
        # 标准化到[-1, 1]范围
        return max(-1, min(1, moran_i))
    
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
    
    def _calculate_area(self, bounding_box: Dict[str, float]) -> float:
        """计算边界框面积（平方公里）"""
        lat_diff = bounding_box["max_lat"] - bounding_box["min_lat"]
        lon_diff = bounding_box["max_lon"] - bounding_box["min_lon"]
        
        # 简化计算：在中纬度地区，1度纬度约111km，1度经度约111*cos(纬度)km
        avg_lat = (bounding_box["max_lat"] + bounding_box["min_lat"]) / 2
        lat_km = lat_diff * 111
        lon_km = lon_diff * 111 * math.cos(math.radians(avg_lat))
        
        return lat_km * lon_km
    
    def _cluster_to_dict(self, cluster: LocationCluster) -> Dict[str, Any]:
        """将聚集对象转换为字典"""
        return {
            "id": cluster.id,
            "center": cluster.center,
            "radius_km": cluster.radius_km,
            "event_count": cluster.event_count,
            "event_ids": cluster.event_ids,
            "dominant_type": cluster.dominant_type,
            "density": cluster.density,
            "bounding_box": cluster.bounding_box
        }
    
    def _pattern_to_dict(self, pattern: LocationPattern) -> Dict[str, Any]:
        """将模式对象转换为字典"""
        return {
            "pattern_type": pattern.pattern_type,
            "description": pattern.description,
            "confidence": pattern.confidence,
            "parameters": pattern.parameters,
            "event_count": len(pattern.event_ids),
            "event_ids": pattern.event_ids
        }


@tool
@log_io
def analyze_location_patterns(
    events_data: str,
    analysis_types: Optional[List[str]] = None
) -> str:
    """分析神秘事件的地理位置模式
    
    Args:
        events_data: JSON格式的事件数据列表
        analysis_types: 分析类型列表，可选值：clusters, patterns, hotspots, distribution
    
    Returns:
        JSON格式的地理分析结果
    """
    try:
        analyzer = LocationAnalyzer()
        return analyzer._run(events_data, analysis_types)
    except Exception as e:
        error_msg = f"Failed to analyze location patterns. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def find_location_clusters(
    events_data: str,
    radius_km: float = 50.0,
    min_events: int = 2
) -> str:
    """查找地理位置聚集
    
    Args:
        events_data: JSON格式的事件数据列表
        radius_km: 聚集半径（公里）
        min_events: 最小事件数量
    
    Returns:
        JSON格式的聚集结果
    """
    try:
        events_list = json.loads(events_data)
        analyzer = LocationAnalyzer()
        analyzer.config.location_radius_km = radius_km
        
        events = [analyzer._parse_location_event(event_data) for event_data in events_list]
        events_with_location = [e for e in events if e.location]
        
        if not events_with_location:
            return json.dumps({"error": "No events with location information"}, ensure_ascii=False)
        
        clusters = analyzer._analyze_location_clusters(events_with_location)
        
        # 过滤最小事件数量
        filtered_clusters = [cluster for cluster in clusters if cluster["event_count"] >= min_events]
        
        return json.dumps({
            "clusters": filtered_clusters,
            "total_clusters": len(filtered_clusters),
            "total_events_in_clusters": sum(cluster["event_count"] for cluster in filtered_clusters)
        }, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Failed to find location clusters. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def generate_location_heatmap_data(
    events_data: str,
    grid_size_degrees: float = 0.1
) -> str:
    """生成地理位置热力图数据
    
    Args:
        events_data: JSON格式的事件数据列表
        grid_size_degrees: 网格大小（度）
    
    Returns:
        JSON格式的热力图数据
    """
    try:
        events_list = json.loads(events_data)
        analyzer = LocationAnalyzer()
        events = [analyzer._parse_location_event(event_data) for event_data in events_list]
        events_with_location = [e for e in events if e.location]
        
        if not events_with_location:
            return json.dumps({"error": "No events with location information"}, ensure_ascii=False)
        
        # 创建网格
        grid_data = defaultdict(int)
        
        for event in events_with_location:
            grid_lat = round(event.location["lat"] / grid_size_degrees) * grid_size_degrees
            grid_lon = round(event.location["lon"] / grid_size_degrees) * grid_size_degrees
            grid_key = f"{grid_lat},{grid_lon}"
            grid_data[grid_key] += 1
        
        # 转换为热力图格式
        heatmap_points = []
        for grid_key, count in grid_data.items():
            lat_str, lon_str = grid_key.split(',')
            heatmap_points.append({
                "lat": float(lat_str),
                "lon": float(lon_str),
                "intensity": count,
                "weight": count / len(events_with_location)  # 归一化权重
            })
        
        # 按强度排序
        heatmap_points.sort(key=lambda x: x["intensity"], reverse=True)
        
        return json.dumps({
            "heatmap_points": heatmap_points,
            "grid_size_degrees": grid_size_degrees,
            "total_grid_cells": len(heatmap_points),
            "max_intensity": max(point["intensity"] for point in heatmap_points) if heatmap_points else 0
        }, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Failed to generate heatmap data. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)