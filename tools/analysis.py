#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

"""
Analysis tools for mysterious event research.
Provides credibility analysis, correlation analysis, timeline analysis, and location analysis tools.
"""

import logging
from typing import Dict, List, Any, Optional
from langchain_core.tools import tool

from .credibility import analyze_information_credibility, filter_reliable_information
from .correlation import analyze_event_correlations, build_correlation_timeline, analyze_location_patterns
from .timeline import analyze_timeline_patterns, generate_timeline_report
from .location import analyze_location_patterns as location_patterns, find_location_clusters, generate_location_heatmap_data
from .decorators import mystery_tool

logger = logging.getLogger(__name__)


@mystery_tool
@tool
def get_credibility_analyzer_tool(
    content: str,
    source_info: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Get credibility analysis tool for analyzing information reliability.
    
    Args:
        content: The content to analyze for credibility
        source_info: Information about the source (optional)
        context: Additional context for analysis (optional)
        
    Returns:
        Dict containing credibility analysis results
    """
    try:
        result = analyze_information_credibility(content, source_info, context)
        logger.info(f"Credibility analysis completed with score: {result.get('overall_score', 0)}")
        return result
    except Exception as e:
        logger.error(f"Error in credibility analysis: {str(e)}")
        return {"error": str(e), "overall_score": 0.0}


@mystery_tool
@tool
def get_correlation_analyzer_tool(
    events: List[Dict[str, Any]],
    analysis_type: str = "comprehensive"
) -> Dict[str, Any]:
    """Get correlation analysis tool for analyzing relationships between events.
    
    Args:
        events: List of mystery events to analyze
        analysis_type: Type of correlation analysis (comprehensive, temporal, geographical)
        
    Returns:
        Dict containing correlation analysis results
    """
    try:
        if analysis_type == "temporal":
            result = build_correlation_timeline(events)
        elif analysis_type == "geographical":
            result = analyze_location_patterns(events)
        else:
            result = analyze_event_correlations(events)
            
        logger.info(f"Correlation analysis completed for {len(events)} events")
        return result
    except Exception as e:
        logger.error(f"Error in correlation analysis: {str(e)}")
        return {"error": str(e), "correlations": []}


@mystery_tool
@tool
def get_timeline_analyzer_tool(
    events: List[Dict[str, Any]],
    analysis_period: Optional[str] = None
) -> Dict[str, Any]:
    """Get timeline analysis tool for analyzing temporal patterns in events.
    
    Args:
        events: List of mystery events with timestamps
        analysis_period: Period for analysis (daily, weekly, monthly, yearly)
        
    Returns:
        Dict containing timeline analysis results
    """
    try:
        result = analyze_timeline_patterns(events, analysis_period)
        logger.info(f"Timeline analysis completed for {len(events)} events")
        return result
    except Exception as e:
        logger.error(f"Error in timeline analysis: {str(e)}")
        return {"error": str(e), "patterns": []}


@mystery_tool
@tool
def get_location_analyzer_tool(
    events: List[Dict[str, Any]],
    analysis_type: str = "patterns"
) -> Dict[str, Any]:
    """Get location analysis tool for analyzing geographical patterns in events.
    
    Args:
        events: List of mystery events with location data
        analysis_type: Type of analysis (patterns, clusters, heatmap)
        
    Returns:
        Dict containing location analysis results
    """
    try:
        if analysis_type == "clusters":
            result = find_location_clusters(events)
        elif analysis_type == "heatmap":
            result = generate_location_heatmap_data(events)
        else:
            result = location_patterns(events)
            
        logger.info(f"Location analysis completed for {len(events)} events")
        return result
    except Exception as e:
        logger.error(f"Error in location analysis: {str(e)}")
        return {"error": str(e), "patterns": []}


@mystery_tool
@tool
def comprehensive_analysis_tool(
    events: List[Dict[str, Any]],
    enable_credibility: bool = True,
    enable_correlation: bool = True,
    enable_timeline: bool = True,
    enable_location: bool = True
) -> Dict[str, Any]:
    """Perform comprehensive analysis on mystery events.
    
    Args:
        events: List of mystery events to analyze
        enable_credibility: Whether to perform credibility analysis
        enable_correlation: Whether to perform correlation analysis
        enable_timeline: Whether to perform timeline analysis
        enable_location: Whether to perform location analysis
        
    Returns:
        Dict containing comprehensive analysis results
    """
    results = {
        "total_events": len(events),
        "analysis_timestamp": None,
        "credibility_analysis": None,
        "correlation_analysis": None,
        "timeline_analysis": None,
        "location_analysis": None,
        "summary": {}
    }
    
    try:
        from datetime import datetime
        results["analysis_timestamp"] = datetime.now().isoformat()
        
        # Credibility analysis
        if enable_credibility and events:
            credibility_scores = []
            for event in events:
                content = event.get("description", "")
                source_info = event.get("source", {})
                score_result = get_credibility_analyzer_tool(content, source_info)
                credibility_scores.append(score_result.get("overall_score", 0.0))
            
            results["credibility_analysis"] = {
                "average_score": sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0.0,
                "high_credibility_count": sum(1 for score in credibility_scores if score >= 0.7),
                "low_credibility_count": sum(1 for score in credibility_scores if score < 0.3),
                "scores": credibility_scores
            }
        
        # Correlation analysis
        if enable_correlation:
            results["correlation_analysis"] = get_correlation_analyzer_tool(events)
        
        # Timeline analysis
        if enable_timeline:
            results["timeline_analysis"] = get_timeline_analyzer_tool(events)
        
        # Location analysis
        if enable_location:
            results["location_analysis"] = get_location_analyzer_tool(events)
        
        # Generate summary
        results["summary"] = {
            "high_credibility_events": results.get("credibility_analysis", {}).get("high_credibility_count", 0),
            "correlation_count": len(results.get("correlation_analysis", {}).get("correlations", [])),
            "timeline_patterns": len(results.get("timeline_analysis", {}).get("patterns", [])),
            "location_clusters": len(results.get("location_analysis", {}).get("clusters", []))
        }
        
        logger.info(f"Comprehensive analysis completed for {len(events)} events")
        return results
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {str(e)}")
        results["error"] = str(e)
        return results