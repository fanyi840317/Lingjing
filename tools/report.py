# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import base64

from langchain_core.tools import BaseTool, tool

from config.mystery_config import MysteryEventConfig, MysteryEventType
from tools.decorators import log_io

logger = logging.getLogger(__name__)


@dataclass
class ReportSection:
    """报告章节"""
    title: str
    content: str
    subsections: List['ReportSection'] = None
    charts: List[Dict[str, Any]] = None
    tables: List[Dict[str, Any]] = None


@dataclass
class ReportMetadata:
    """报告元数据"""
    title: str
    author: str
    created_at: datetime
    version: str
    summary: str
    keywords: List[str]
    event_count: int
    analysis_period: Dict[str, str]


class ReportGenerator(BaseTool):
    """报告生成器"""
    name: str = "report_generator"
    description: str = "Generate comprehensive reports for mysterious event research."
    
    def __init__(self, config: Optional[MysteryEventConfig] = None):
        """初始化报告生成器
        
        Args:
            config: 神秘事件配置
        """
        super().__init__()
        self.config = config or MysteryEventConfig()
    
    def _run(self, report_data: str, format_type: str = "markdown", output_path: str = None) -> str:
        """生成报告
        
        Args:
            report_data: JSON格式的报告数据
            format_type: 报告格式 (markdown, pdf, html)
            output_path: 输出路径
            
        Returns:
            生成的报告内容或文件路径
        """
        try:
            data = json.loads(report_data)
            
            if format_type.lower() == "markdown":
                return self._generate_markdown_report(data, output_path)
            elif format_type.lower() == "pdf":
                return self._generate_pdf_report(data, output_path)
            elif format_type.lower() == "html":
                return self._generate_html_report(data, output_path)
            else:
                return json.dumps({"error": f"Unsupported format: {format_type}"}, ensure_ascii=False)
                
        except Exception as e:
            error_msg = f"Failed to generate report. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _generate_markdown_report(self, data: Dict[str, Any], output_path: str = None) -> str:
        """生成Markdown格式报告"""
        try:
            # 构建报告内容
            markdown_content = self._build_markdown_content(data)
            
            if output_path:
                # 保存到文件
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                return json.dumps({
                    "status": "success",
                    "format": "markdown",
                    "output_path": output_path,
                    "content_length": len(markdown_content)
                }, ensure_ascii=False)
            else:
                # 直接返回内容
                return json.dumps({
                    "status": "success",
                    "format": "markdown",
                    "content": markdown_content
                }, ensure_ascii=False)
                
        except Exception as e:
            error_msg = f"Failed to generate Markdown report. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _generate_pdf_report(self, data: Dict[str, Any], output_path: str = None) -> str:
        """生成PDF格式报告"""
        try:
            # 首先生成HTML内容
            html_content = self._build_html_content(data)
            
            # 在真实实现中，这里会使用库如weasyprint或reportlab生成PDF
            # from weasyprint import HTML
            # pdf_bytes = HTML(string=html_content).write_pdf()
            
            # 模拟PDF生成
            pdf_content = f"PDF Report Generated at {datetime.now().isoformat()}\n\nContent: {html_content[:500]}..."
            
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(pdf_content)
                
                return json.dumps({
                    "status": "success",
                    "format": "pdf",
                    "output_path": output_path,
                    "file_size": len(pdf_content)
                }, ensure_ascii=False)
            else:
                # 返回base64编码的PDF内容
                pdf_base64 = base64.b64encode(pdf_content.encode('utf-8')).decode('utf-8')
                return json.dumps({
                    "status": "success",
                    "format": "pdf",
                    "content_base64": pdf_base64
                }, ensure_ascii=False)
                
        except Exception as e:
            error_msg = f"Failed to generate PDF report. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _generate_html_report(self, data: Dict[str, Any], output_path: str = None) -> str:
        """生成HTML格式报告"""
        try:
            html_content = self._build_html_content(data)
            
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                return json.dumps({
                    "status": "success",
                    "format": "html",
                    "output_path": output_path,
                    "content_length": len(html_content)
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    "status": "success",
                    "format": "html",
                    "content": html_content
                }, ensure_ascii=False)
                
        except Exception as e:
            error_msg = f"Failed to generate HTML report. Error: {repr(e)}"
            logger.error(error_msg)
            return json.dumps({"error": error_msg}, ensure_ascii=False)
    
    def _build_markdown_content(self, data: Dict[str, Any]) -> str:
        """构建Markdown内容"""
        content = []
        
        # 标题和元数据
        metadata = data.get("metadata", {})
        content.append(f"# {metadata.get('title', '神秘事件研究报告')}")
        content.append("")
        content.append(f"**作者**: {metadata.get('author', '神秘事件研究助手')}")
        content.append(f"**生成时间**: {metadata.get('created_at', datetime.now().isoformat())}")
        content.append(f"**版本**: {metadata.get('version', '1.0')}")
        content.append("")
        
        # 执行摘要
        if "summary" in data:
            content.append("## 执行摘要")
            content.append("")
            content.append(data["summary"])
            content.append("")
        
        # 关键发现
        if "key_findings" in data:
            content.append("## 关键发现")
            content.append("")
            for i, finding in enumerate(data["key_findings"], 1):
                content.append(f"{i}. {finding}")
            content.append("")
        
        # 事件概览
        if "events_overview" in data:
            overview = data["events_overview"]
            content.append("## 事件概览")
            content.append("")
            content.append(f"- **总事件数**: {overview.get('total_events', 0)}")
            content.append(f"- **分析时间段**: {overview.get('time_range', 'N/A')}")
            content.append(f"- **涉及地区**: {overview.get('regions', 'N/A')}")
            content.append(f"- **主要事件类型**: {overview.get('main_types', 'N/A')}")
            content.append("")
        
        # 详细分析
        if "analysis" in data:
            content.append("## 详细分析")
            content.append("")
            
            analysis = data["analysis"]
            
            # 时间线分析
            if "timeline" in analysis:
                content.append("### 时间线分析")
                content.append("")
                timeline = analysis["timeline"]
                
                if "patterns" in timeline:
                    content.append("#### 时间模式")
                    for pattern in timeline["patterns"]:
                        content.append(f"- **{pattern.get('pattern_type', 'Unknown')}**: {pattern.get('description', '')}")
                        content.append(f"  - 置信度: {pattern.get('confidence', 0):.2f}")
                        content.append(f"  - 涉及事件: {len(pattern.get('event_ids', []))}个")
                    content.append("")
                
                if "trends" in timeline:
                    content.append("#### 趋势分析")
                    trends = timeline["trends"]
                    content.append(f"- **总体趋势**: {trends.get('overall_trend', 'N/A')}")
                    content.append(f"- **增长率**: {trends.get('growth_rate', 0):.2f}%")
                    content.append(f"- **峰值期间**: {trends.get('peak_period', 'N/A')}")
                    content.append("")
            
            # 地理分析
            if "location" in analysis:
                content.append("### 地理分布分析")
                content.append("")
                location = analysis["location"]
                
                if "clusters" in location:
                    content.append("#### 地理聚集")
                    for cluster in location["clusters"][:5]:  # 显示前5个聚集
                        content.append(f"- **聚集 {cluster.get('id', '')}**")
                        content.append(f"  - 中心位置: ({cluster.get('center', {}).get('lat', 0):.4f}, {cluster.get('center', {}).get('lon', 0):.4f})")
                        content.append(f"  - 事件数量: {cluster.get('event_count', 0)}")
                        content.append(f"  - 半径: {cluster.get('radius_km', 0):.2f}公里")
                        content.append(f"  - 主要类型: {cluster.get('dominant_type', 'N/A')}")
                    content.append("")
                
                if "hotspots" in location:
                    content.append("#### 热点区域")
                    for hotspot in location["hotspots"][:3]:  # 显示前3个热点
                        content.append(f"- **热点 {hotspot.get('id', '')}**")
                        content.append(f"  - 密度分数: {hotspot.get('density_score', 0):.2f}")
                        content.append(f"  - 事件数量: {hotspot.get('event_count', 0)}")
                        content.append(f"  - 主要类型: {hotspot.get('dominant_type', 'N/A')}")
                    content.append("")
            
            # 可信度分析
            if "credibility" in analysis:
                content.append("### 可信度分析")
                content.append("")
                credibility = analysis["credibility"]
                
                content.append(f"- **平均可信度分数**: {credibility.get('average_score', 0):.2f}")
                content.append(f"- **高可信度事件**: {credibility.get('high_credibility_count', 0)}个")
                content.append(f"- **中等可信度事件**: {credibility.get('medium_credibility_count', 0)}个")
                content.append(f"- **低可信度事件**: {credibility.get('low_credibility_count', 0)}个")
                content.append("")
                
                if "reliability_factors" in credibility:
                    content.append("#### 可信度影响因素")
                    for factor, impact in credibility["reliability_factors"].items():
                        content.append(f"- **{factor}**: {impact}")
                    content.append("")
            
            # 关联分析
            if "correlation" in analysis:
                content.append("### 关联分析")
                content.append("")
                correlation = analysis["correlation"]
                
                if "strong_correlations" in correlation:
                    content.append("#### 强关联事件")
                    for corr in correlation["strong_correlations"][:5]:
                        content.append(f"- **事件对**: {corr.get('event1_id', '')} ↔ {corr.get('event2_id', '')}")
                        content.append(f"  - 关联强度: {corr.get('correlation_strength', 0):.2f}")
                        content.append(f"  - 关联类型: {', '.join(corr.get('correlation_types', []))}")
                        content.append(f"  - 时间间隔: {corr.get('time_difference_hours', 0):.1f}小时")
                        content.append(f"  - 距离: {corr.get('distance_km', 0):.2f}公里")
                    content.append("")
        
        # 结论和建议
        if "conclusions" in data:
            content.append("## 结论")
            content.append("")
            for conclusion in data["conclusions"]:
                content.append(f"- {conclusion}")
            content.append("")
        
        if "recommendations" in data:
            content.append("## 建议")
            content.append("")
            for recommendation in data["recommendations"]:
                content.append(f"- {recommendation}")
            content.append("")
        
        # 附录
        if "appendix" in data:
            content.append("## 附录")
            content.append("")
            
            appendix = data["appendix"]
            
            if "data_sources" in appendix:
                content.append("### 数据源")
                content.append("")
                for source in appendix["data_sources"]:
                    content.append(f"- {source}")
                content.append("")
            
            if "methodology" in appendix:
                content.append("### 研究方法")
                content.append("")
                content.append(appendix["methodology"])
                content.append("")
        
        return "\n".join(content)
    
    def _build_html_content(self, data: Dict[str, Any]) -> str:
        """构建HTML内容"""
        metadata = data.get("metadata", {})
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang='zh-CN'>",
            "<head>",
            "<meta charset='UTF-8'>",
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            f"<title>{metadata.get('title', '神秘事件研究报告')}</title>",
            "<style>",
            self._get_html_styles(),
            "</style>",
            "</head>",
            "<body>",
            "<div class='container'>"
        ]
        
        # 标题页
        html_parts.extend([
            "<div class='title-page'>",
            f"<h1>{metadata.get('title', '神秘事件研究报告')}</h1>",
            f"<p class='author'>作者: {metadata.get('author', '神秘事件研究助手')}</p>",
            f"<p class='date'>生成时间: {metadata.get('created_at', datetime.now().isoformat())}</p>",
            f"<p class='version'>版本: {metadata.get('version', '1.0')}</p>",
            "</div>"
        ])
        
        # 目录
        html_parts.extend([
            "<div class='toc'>",
            "<h2>目录</h2>",
            "<ul>",
            "<li><a href='#summary'>执行摘要</a></li>",
            "<li><a href='#findings'>关键发现</a></li>",
            "<li><a href='#overview'>事件概览</a></li>",
            "<li><a href='#analysis'>详细分析</a></li>",
            "<li><a href='#conclusions'>结论</a></li>",
            "<li><a href='#recommendations'>建议</a></li>",
            "<li><a href='#appendix'>附录</a></li>",
            "</ul>",
            "</div>"
        ])
        
        # 内容部分
        if "summary" in data:
            html_parts.extend([
                "<div class='section' id='summary'>",
                "<h2>执行摘要</h2>",
                f"<p>{data['summary']}</p>",
                "</div>"
            ])
        
        if "key_findings" in data:
            html_parts.extend([
                "<div class='section' id='findings'>",
                "<h2>关键发现</h2>",
                "<ol>"
            ])
            for finding in data["key_findings"]:
                html_parts.append(f"<li>{finding}</li>")
            html_parts.extend(["</ol>", "</div>"])
        
        # 事件概览
        if "events_overview" in data:
            overview = data["events_overview"]
            html_parts.extend([
                "<div class='section' id='overview'>",
                "<h2>事件概览</h2>",
                "<table class='overview-table'>",
                f"<tr><td>总事件数</td><td>{overview.get('total_events', 0)}</td></tr>",
                f"<tr><td>分析时间段</td><td>{overview.get('time_range', 'N/A')}</td></tr>",
                f"<tr><td>涉及地区</td><td>{overview.get('regions', 'N/A')}</td></tr>",
                f"<tr><td>主要事件类型</td><td>{overview.get('main_types', 'N/A')}</td></tr>",
                "</table>",
                "</div>"
            ])
        
        # 结束HTML
        html_parts.extend([
            "</div>",
            "</body>",
            "</html>"
        ])
        
        return "\n".join(html_parts)
    
    def _get_html_styles(self) -> str:
        """获取HTML样式"""
        return """
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .title-page {
            text-align: center;
            padding: 60px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .title-page h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .author, .date, .version {
            font-size: 1.1em;
            margin: 10px 0;
        }
        .toc {
            padding: 40px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        .toc h2 {
            color: #495057;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        .toc li {
            margin: 10px 0;
        }
        .toc a {
            color: #007bff;
            text-decoration: none;
            font-weight: 500;
        }
        .toc a:hover {
            text-decoration: underline;
        }
        .section {
            padding: 40px;
            border-bottom: 1px solid #dee2e6;
        }
        .section h2 {
            color: #495057;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .section h3 {
            color: #6c757d;
            margin-top: 30px;
            margin-bottom: 15px;
        }
        .overview-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .overview-table td {
            padding: 12px;
            border: 1px solid #dee2e6;
        }
        .overview-table td:first-child {
            background-color: #f8f9fa;
            font-weight: bold;
            width: 30%;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .chart-placeholder {
            background-color: #e9ecef;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #6c757d;
            font-style: italic;
        }
        """


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self):
        """初始化图表生成器"""
        pass
    
    def generate_timeline_chart(self, timeline_data: List[Dict[str, Any]]) -> str:
        """生成时间线图表"""
        # 在真实实现中，这里会使用matplotlib或plotly生成图表
        # 返回图表的base64编码或SVG字符串
        return "<div class='chart-placeholder'>时间线图表占位符</div>"
    
    def generate_location_heatmap(self, location_data: List[Dict[str, Any]]) -> str:
        """生成位置热力图"""
        return "<div class='chart-placeholder'>位置热力图占位符</div>"
    
    def generate_correlation_network(self, correlation_data: List[Dict[str, Any]]) -> str:
        """生成关联网络图"""
        return "<div class='chart-placeholder'>关联网络图占位符</div>"
    
    def generate_credibility_distribution(self, credibility_data: List[Dict[str, Any]]) -> str:
        """生成可信度分布图"""
        return "<div class='chart-placeholder'>可信度分布图占位符</div>"


@tool
@log_io
def generate_mystery_report(
    report_data: str,
    format_type: str = "markdown",
    output_path: Optional[str] = None
) -> str:
    """生成神秘事件研究报告
    
    Args:
        report_data: JSON格式的报告数据
        format_type: 报告格式 (markdown, pdf, html)
        output_path: 输出文件路径
    
    Returns:
        生成的报告内容或文件信息
    """
    try:
        generator = ReportGenerator()
        return generator._run(report_data, format_type, output_path)
    except Exception as e:
        error_msg = f"Failed to generate mystery report. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def create_executive_summary(
    analysis_results: str,
    max_length: int = 500
) -> str:
    """创建执行摘要
    
    Args:
        analysis_results: JSON格式的分析结果
        max_length: 最大字符长度
    
    Returns:
        执行摘要文本
    """
    try:
        results = json.loads(analysis_results)
        
        summary_parts = []
        
        # 事件概览
        if "events_overview" in results:
            overview = results["events_overview"]
            total_events = overview.get("total_events", 0)
            time_range = overview.get("time_range", "未知时间段")
            main_types = overview.get("main_types", "多种类型")
            
            summary_parts.append(
                f"本报告分析了{time_range}期间的{total_events}起神秘事件，主要类型包括{main_types}。"
            )
        
        # 关键发现
        if "key_findings" in results and results["key_findings"]:
            key_finding = results["key_findings"][0]  # 取第一个关键发现
            summary_parts.append(f"关键发现：{key_finding}")
        
        # 时间线分析
        if "analysis" in results and "timeline" in results["analysis"]:
            timeline = results["analysis"]["timeline"]
            if "trends" in timeline:
                trend = timeline["trends"].get("overall_trend", "稳定")
                summary_parts.append(f"时间趋势显示事件发生呈{trend}态势。")
        
        # 地理分析
        if "analysis" in results and "location" in results["analysis"]:
            location = results["analysis"]["location"]
            if "clusters" in location and location["clusters"]:
                cluster_count = len(location["clusters"])
                summary_parts.append(f"地理分析发现{cluster_count}个主要事件聚集区域。")
        
        # 可信度分析
        if "analysis" in results and "credibility" in results["analysis"]:
            credibility = results["analysis"]["credibility"]
            avg_score = credibility.get("average_score", 0)
            summary_parts.append(f"整体可信度评分为{avg_score:.2f}分。")
        
        # 组合摘要
        summary = " ".join(summary_parts)
        
        # 截断到指定长度
        if len(summary) > max_length:
            summary = summary[:max_length-3] + "..."
        
        return json.dumps({
            "summary": summary,
            "length": len(summary),
            "sections_included": len(summary_parts)
        }, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Failed to create executive summary. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)


@tool
@log_io
def generate_chart_data(
    analysis_data: str,
    chart_type: str
) -> str:
    """生成图表数据
    
    Args:
        analysis_data: JSON格式的分析数据
        chart_type: 图表类型 (timeline, heatmap, network, distribution)
    
    Returns:
        图表数据
    """
    try:
        data = json.loads(analysis_data)
        chart_generator = ChartGenerator()
        
        if chart_type == "timeline":
            timeline_data = data.get("timeline", {})
            chart_html = chart_generator.generate_timeline_chart(timeline_data)
        elif chart_type == "heatmap":
            location_data = data.get("location", {})
            chart_html = chart_generator.generate_location_heatmap(location_data)
        elif chart_type == "network":
            correlation_data = data.get("correlation", {})
            chart_html = chart_generator.generate_correlation_network(correlation_data)
        elif chart_type == "distribution":
            credibility_data = data.get("credibility", {})
            chart_html = chart_generator.generate_credibility_distribution(credibility_data)
        else:
            return json.dumps({"error": f"Unsupported chart type: {chart_type}"}, ensure_ascii=False)
        
        return json.dumps({
            "chart_type": chart_type,
            "chart_html": chart_html,
            "status": "success"
        }, ensure_ascii=False)
        
    except Exception as e:
        error_msg = f"Failed to generate chart data. Error: {repr(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg}, ensure_ascii=False)