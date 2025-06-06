# Copyright (c) 2025 Lingjing Project
# SPDX-License-Identifier: MIT

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class MysteryEventType(Enum):
    """神秘事件类型枚举"""
    UFO = "ufo"
    CRYPTID = "cryptid"  # 神秘生物
    PARANORMAL = "paranormal"  # 超自然现象
    ANCIENT_MYSTERY = "ancient_mystery"  # 古代谜团
    DISAPPEARANCE = "disappearance"  # 神秘失踪
    NATURAL_ANOMALY = "natural_anomaly"  # 自然异象


class DataSourceType(Enum):
    """数据源类型枚举"""
    ACADEMIC = "academic"  # 学术数据库
    NEWS = "news"  # 新闻媒体
    FORUM = "forum"  # 论坛社区
    DOCUMENTARY = "documentary"  # 纪录片
    GOVERNMENT = "government"  # 政府报告
    RESEARCH_INSTITUTE = "research_institute"  # 研究机构


@dataclass
class DataSourceConfig:
    """数据源配置"""
    name: str
    source_type: DataSourceType
    base_url: str
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    rate_limit: int = 10  # 每分钟请求限制
    reliability_score: float = 0.5  # 可靠性评分 0-1
    requires_login: bool = False
    login_config: Optional[Dict[str, str]] = None


@dataclass
class MysteryEventConfig:
    """神秘事件研究配置"""
    
    # UFO相关关键词
    ufo_keywords: List[str] = field(default_factory=lambda: [
        "UFO目击报告", "不明飞行物现象", "飞碟目击", "外星人接触", 
        "UFO sighting", "unidentified flying object", "alien encounter",
        "close encounter", "extraterrestrial", "flying saucer"
    ])
    
    # 其他神秘事件关键词
    mystery_keywords: Dict[MysteryEventType, List[str]] = field(default_factory=lambda: {
        MysteryEventType.CRYPTID: [
            "尼斯湖水怪", "大脚怪", "雪人", "天蛾人", "泽西恶魔",
            "Loch Ness Monster", "Bigfoot", "Yeti", "Mothman", "Jersey Devil",
            "Chupacabra", "Kraken", "神秘生物目击"
        ],
        MysteryEventType.PARANORMAL: [
            "百慕大三角", "麦田怪圈", "幽灵船", "鬼屋现象", "超自然事件",
            "Bermuda Triangle", "crop circles", "ghost ship", "haunted house",
            "paranormal activity", "poltergeist", "supernatural phenomenon"
        ],
        MysteryEventType.ANCIENT_MYSTERY: [
            "玛雅文明神秘现象", "金字塔之谜", "巨石阵", "复活节岛石像", "亚特兰蒂斯",
            "Maya civilization mystery", "pyramid mystery", "Stonehenge", 
            "Easter Island statues", "Atlantis", "ancient aliens", "lost civilization"
        ],
        MysteryEventType.DISAPPEARANCE: [
            "神秘失踪", "飞机失踪", "船只失踪", "人员失踪", "马航MH370",
            "mysterious disappearance", "missing aircraft", "missing ship",
            "missing person", "vanished without trace"
        ],
        MysteryEventType.NATURAL_ANOMALY: [
            "球状闪电", "极光异象", "地震光", "天空异象", "气象异常",
            "ball lightning", "aurora anomaly", "earthquake lights", 
            "sky phenomenon", "weather anomaly", "atmospheric phenomenon"
        ]
    })
    
    # 数据源配置
    data_sources: List[DataSourceConfig] = field(default_factory=lambda: [
        # 学术数据库
        DataSourceConfig(
            name="知网",
            source_type=DataSourceType.ACADEMIC,
            base_url="https://www.cnki.net",
            reliability_score=0.9,
            requires_login=True
        ),
        DataSourceConfig(
            name="万方数据",
            source_type=DataSourceType.ACADEMIC,
            base_url="https://www.wanfangdata.com.cn",
            reliability_score=0.85,
            requires_login=True
        ),
        DataSourceConfig(
            name="Web of Science",
            source_type=DataSourceType.ACADEMIC,
            base_url="https://www.webofscience.com",
            reliability_score=0.95,
            requires_login=True
        ),
        # 权威新闻媒体
        DataSourceConfig(
            name="BBC News",
            source_type=DataSourceType.NEWS,
            base_url="https://www.bbc.com",
            reliability_score=0.9
        ),
        DataSourceConfig(
            name="CNN",
            source_type=DataSourceType.NEWS,
            base_url="https://www.cnn.com",
            reliability_score=0.85
        ),
        DataSourceConfig(
            name="新华网",
            source_type=DataSourceType.NEWS,
            base_url="https://www.xinhuanet.com",
            reliability_score=0.9
        ),
        # 专业研究机构
        DataSourceConfig(
            name="MUFON",
            source_type=DataSourceType.RESEARCH_INSTITUTE,
            base_url="https://www.mufon.com",
            reliability_score=0.7
        ),
        DataSourceConfig(
            name="NUFORC",
            source_type=DataSourceType.RESEARCH_INSTITUTE,
            base_url="https://nuforc.org",
            reliability_score=0.75
        )
    ])
    
    # 信息筛选配置
    credibility_threshold: float = 0.6  # 可信度阈值
    max_age_days: int = 365 * 5  # 信息最大年龄（天）
    min_detail_score: float = 0.5  # 最小细节丰富度评分
    
    # 关联分析配置
    time_window_days: int = 30  # 时间窗口（天）
    location_radius_km: float = 100.0  # 地理位置半径（公里）
    similarity_threshold: float = 0.7  # 相似度阈值
    
    # Neo4j图数据库配置
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    
    def get_all_keywords(self) -> List[str]:
        """获取所有关键词"""
        all_keywords = self.ufo_keywords.copy()
        for keywords in self.mystery_keywords.values():
            all_keywords.extend(keywords)
        return list(set(all_keywords))  # 去重
    
    def get_keywords_by_type(self, event_type: MysteryEventType) -> List[str]:
        """根据事件类型获取关键词"""
        if event_type == MysteryEventType.UFO:
            return self.ufo_keywords
        return self.mystery_keywords.get(event_type, [])
    
    def get_sources_by_type(self, source_type: DataSourceType) -> List[DataSourceConfig]:
        """根据数据源类型获取数据源配置"""
        return [source for source in self.data_sources if source.source_type == source_type]
    
    def get_reliable_sources(self, min_score: float = 0.8) -> List[DataSourceConfig]:
        """获取高可靠性数据源"""
        return [source for source in self.data_sources if source.reliability_score >= min_score]