# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import os

from .crawl import crawl_tool, batch_crawl_tool, mystery_site_crawler
from .python_repl import python_repl_tool, data_analysis_tool, mystery_data_processor
from .retriever import get_retriever_tool, get_document_by_id, get_related_documents, advanced_search_tool
from .search import (
    get_web_search_tool, 
    get_academic_search_tool,
    get_mystery_search_tool,
    LoggedTavilySearch,
    AcademicSearch,
    MysterySearch
)
from .analysis import (
    get_credibility_analyzer_tool,
    get_correlation_analyzer_tool,
    get_timeline_analyzer_tool,
    get_location_analyzer_tool,
    comprehensive_analysis_tool
)
from .storage import (
    get_graph_storage_tool,
    get_neo4j_tool,
    get_elasticsearch_tool,
    batch_storage_tool,
    query_storage_tool
)
from .report import (
    generate_mystery_report,
    create_executive_summary,
    generate_chart_data
)
from .tts import (
    convert_text_to_speech,
    narrate_mystery_report,
    get_available_tts_voices,
    create_audio_summary
)
from .credibility import (
    analyze_information_credibility,
    filter_reliable_information
)
from .correlation import (
    analyze_event_correlations,
    build_correlation_timeline,
    analyze_location_patterns
)
from .timeline import (
    analyze_timeline_patterns,
    generate_timeline_report
)
from .location import (
    analyze_location_patterns as location_analysis,
    find_location_clusters,
    generate_location_heatmap_data
)
from .graph_storage import (
    store_in_neo4j,
    store_in_elasticsearch,
    store_mystery_events_graph,
    query_related_events,
    search_events_by_criteria
)

__all__ = [
    # Crawling tools
    "crawl_tool",
    "batch_crawl_tool",
    "mystery_site_crawler",
    
    # Python REPL tools
    "python_repl_tool",
    "data_analysis_tool",
    "mystery_data_processor",
    
    # Retriever tools
    "get_retriever_tool",
    "get_document_by_id",
    "get_related_documents",
    "advanced_search_tool",
    
    # Search tools
    "get_web_search_tool",
    "get_academic_search_tool",
    "get_mystery_search_tool",
    "LoggedTavilySearch",
    "AcademicSearch",
    "MysterySearch",
    
    # Analysis tools
    "get_credibility_analyzer_tool",
    "get_correlation_analyzer_tool",
    "get_timeline_analyzer_tool",
    "get_location_analyzer_tool",
    "comprehensive_analysis_tool",
    
    # Storage tools
    "get_graph_storage_tool",
    "get_neo4j_tool",
    "get_elasticsearch_tool",
    "batch_storage_tool",
    "query_storage_tool",
    
    # Report generation tools
    "generate_mystery_report",
    "create_executive_summary",
    "generate_chart_data",
    
    # TTS tools
    "convert_text_to_speech",
    "narrate_mystery_report",
    "get_available_tts_voices",
    "create_audio_summary",
    
    # Credibility analysis
    "analyze_information_credibility",
    "filter_reliable_information",
    
    # Correlation analysis
    "analyze_event_correlations",
    "build_correlation_timeline",
    "analyze_location_patterns",
    
    # Timeline analysis
    "analyze_timeline_patterns",
    "generate_timeline_report",
    
    # Location analysis
    "location_analysis",
    "find_location_clusters",
    "generate_location_heatmap_data",
    
    # Graph storage
    "store_in_neo4j",
    "store_in_elasticsearch",
    "store_mystery_events_graph",
    "query_related_events",
    "search_events_by_criteria",
]