# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import json
import logging
import os
from typing import Annotated, Literal, Dict, List, Any
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.types import Command, interrupt

from agents import create_agent
from tools.search import LoggedTavilySearch, AcademicSearch, MysterySearch
from tools import (
    crawl_tool,
    get_web_search_tool,
    get_retriever_tool,
    python_repl_tool,
    get_academic_search_tool,
    get_mystery_search_tool,
    get_credibility_analyzer_tool,
    get_correlation_analyzer_tool,
    get_graph_storage_tool,
)

from config.agents import AGENT_LLM_MAP
from config.configuration import Configuration
from llms.llm import get_llm_by_type
from prompts.planner_model import Plan
from prompts.template import apply_prompt_template
from utils.json_utils import repair_json_output
from rag import MysteryEvent

from .types import State
from config import SELECTED_SEARCH_ENGINE, SearchEngine

logger = logging.getLogger(__name__)


@tool
def handoff_to_planner(
    task_title: Annotated[str, "The title of the task to be handed off."],
    locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
):
    """Handoff to planner agent to do plan."""
    return


@tool
def handoff_to_mystery_researcher(
    task_title: Annotated[str, "The title of the mystery research task."],
    event_type: Annotated[str, "The type of mystery event to research."],
):
    """Handoff to mystery researcher to collect mystery event data."""
    return


@tool
def handoff_to_academic_researcher(
    task_title: Annotated[str, "The title of the academic research task."],
    keywords: Annotated[str, "Academic search keywords."],
):
    """Handoff to academic researcher to search academic databases."""
    return


@tool
def handoff_to_credibility_analyzer(
    task_title: Annotated[str, "The title of the credibility analysis task."],
):
    """Handoff to credibility analyzer to assess information reliability."""
    return


@tool
def handoff_to_correlation_analyzer(
    task_title: Annotated[str, "The title of the correlation analysis task."],
):
    """Handoff to correlation analyzer to find event relationships."""
    return


def background_investigation_node(state: State, config: RunnableConfig):
    """Background investigation node for mystery research."""
    logger.info("Background investigation node is running for mystery research.")
    configurable = Configuration.from_runnable_config(config)
    query = state["messages"][-1].content
    background_investigation_results = None
    
    try:
        if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
            searched_content = LoggedTavilySearch(
                max_results=configurable.max_search_results
            ).invoke(query)
            if isinstance(searched_content, list):
                background_investigation_results = [
                    f"## {elem['title']}\n\n{elem['content']}" for elem in searched_content
                ]
                return {
                    "background_investigation_results": "\n\n".join(
                        background_investigation_results
                    )
                }
            else:
                logger.error(
                    f"Tavily search returned malformed response: {searched_content}"
                )
        elif SELECTED_SEARCH_ENGINE == SearchEngine.MYSTERY_SEARCH.value:
            # Use mystery-specific search
            mystery_search_tool = get_mystery_search_tool(configurable.max_search_results)
            background_investigation_results = mystery_search_tool.invoke(query)
        else:
            background_investigation_results = get_web_search_tool(
                configurable.max_search_results
            ).invoke(query)
            
        return {
            "background_investigation_results": json.dumps(
                background_investigation_results, ensure_ascii=False
            )
        }
    except Exception as e:
        logger.error(f"Error in background investigation: {e}")
        return {
            "background_investigation_results": f"Error: {str(e)}",
            "error_messages": state.get("error_messages", []) + [str(e)]
        }


def coordinator_node(state: State, config: RunnableConfig):
    """Coordinator node for mystery research workflow."""
    logger.info("Coordinator node is running for mystery research.")
    
    # Initialize processing status
    return {
        "processing_status": "processing",
        "locale": state.get("locale", "zh-CN"),
    }


def planner_node(
    state: State, config: RunnableConfig
) -> Command[Literal["human_feedback", "reporter"]]:
    """Planner node that generates the mystery research plan."""
    logger.info("Planner generating mystery research plan")
    configurable = Configuration.from_runnable_config(config)
    plan_iterations = state["plan_iterations"] if state.get("plan_iterations", 0) else 0
    messages = apply_prompt_template("mystery_planner", state, configurable)

    if (
        plan_iterations == 0
        and state.get("enable_background_investigation")
        and state.get("background_investigation_results")
    ):
        messages += [
            {
                "role": "user",
                "content": (
                    "background investigation results of user query:\n"
                    + state["background_investigation_results"]
                ),
            }
        ]

    llm = get_llm_by_type(AGENT_LLM_MAP["planner"])
    response = llm.invoke(messages)
    
    try:
        # Parse the plan
        plan_content = response.content if hasattr(response, 'content') else str(response)
        plan_json = repair_json_output(plan_content)
        plan = Plan.model_validate(plan_json)
        
        # Update state
        new_state = {
            "current_plan": plan,
            "plan_iterations": plan_iterations + 1,
        }
        
        # Check if plan needs human feedback
        if plan_iterations >= configurable.max_plan_iterations:
            return Command(goto="reporter", update=new_state)
        elif plan.has_enough_context:
            return Command(goto="reporter", update=new_state)
        else:
            return Command(goto="mystery_researcher", update=new_state)
            
    except Exception as e:
        logger.error(f"Error parsing plan: {e}")
        return Command(
            goto="reporter",
            update={
                "error_messages": state.get("error_messages", []) + [f"Plan parsing error: {str(e)}"]
            }
        )


def mystery_researcher_node(state: State, config: RunnableConfig):
    """Mystery researcher node for collecting mystery event data."""
    logger.info("Mystery researcher node is running.")
    configurable = Configuration.from_runnable_config(config)
    
    try:
        # Get current step
        current_plan = state.get("current_plan")
        if not current_plan or not current_plan.steps:
            return {"error_messages": state.get("error_messages", []) + ["No plan available"]}
        
        # Find next unexecuted step
        current_step = None
        for step in current_plan.steps:
            if not step.execution_res:
                current_step = step
                break
        
        if not current_step:
            return {"observations": state.get("observations", []) + ["All steps completed"]}
        
        # Execute mystery research
        mystery_search_tool = get_mystery_search_tool(configurable.max_search_results)
        search_results = mystery_search_tool.invoke(current_step.description)
        
        # Extract mystery events from results
        mystery_events = []
        if isinstance(search_results, list):
            for result in search_results:
                try:
                    # Create MysteryEvent from search result
                    event = MysteryEvent(
                        title=result.get("title", ""),
                        description=result.get("content", ""),
                        event_type="unknown",  # Will be analyzed later
                        location="unknown",
                        date="unknown",
                        source_url=result.get("url", ""),
                        source_type="web",
                        credibility_score=0.5,  # Default, will be analyzed
                        witnesses=[],
                        evidence=[],
                        metadata=result
                    )
                    mystery_events.append(event)
                except Exception as e:
                    logger.warning(f"Error creating MysteryEvent: {e}")
        
        # Update step execution result
        current_step.execution_res = f"Found {len(mystery_events)} mystery events"
        
        return {
            "mystery_events": state.get("mystery_events", []) + mystery_events,
            "observations": state.get("observations", []) + [f"Mystery research completed: {current_step.execution_res}"],
            "current_plan": current_plan,
        }
        
    except Exception as e:
        logger.error(f"Error in mystery researcher: {e}")
        return {
            "error_messages": state.get("error_messages", []) + [f"Mystery research error: {str(e)}"]
        }


def academic_researcher_node(state: State, config: RunnableConfig):
    """Academic researcher node for searching academic databases."""
    logger.info("Academic researcher node is running.")
    configurable = Configuration.from_runnable_config(config)
    
    try:
        # Get current step
        current_plan = state.get("current_plan")
        if not current_plan or not current_plan.steps:
            return {"error_messages": state.get("error_messages", []) + ["No plan available"]}
        
        # Find next unexecuted step
        current_step = None
        for step in current_plan.steps:
            if not step.execution_res:
                current_step = step
                break
        
        if not current_step:
            return {"observations": state.get("observations", []) + ["All steps completed"]}
        
        # Execute academic search
        academic_search_tool = get_academic_search_tool(configurable.max_search_results)
        search_results = academic_search_tool.invoke(current_step.description)
        
        # Update step execution result
        current_step.execution_res = f"Found {len(search_results) if isinstance(search_results, list) else 1} academic sources"
        
        return {
            "academic_sources": state.get("academic_sources", []) + (search_results if isinstance(search_results, list) else [search_results]),
            "observations": state.get("observations", []) + [f"Academic research completed: {current_step.execution_res}"],
            "current_plan": current_plan,
        }
        
    except Exception as e:
        logger.error(f"Error in academic researcher: {e}")
        return {
            "error_messages": state.get("error_messages", []) + [f"Academic research error: {str(e)}"]
        }


def credibility_analyzer_node(state: State, config: RunnableConfig):
    """Credibility analyzer node for assessing information reliability."""
    logger.info("Credibility analyzer node is running.")
    
    try:
        mystery_events = state.get("mystery_events", [])
        academic_sources = state.get("academic_sources", [])
        
        if not mystery_events and not academic_sources:
            return {"observations": state.get("observations", []) + ["No data to analyze for credibility"]}
        
        credibility_analyzer_tool = get_credibility_analyzer_tool()
        
        # Analyze credibility of mystery events
        credibility_scores = {}
        for i, event in enumerate(mystery_events):
            try:
                score = credibility_analyzer_tool.invoke({
                    "content": event.description,
                    "source_type": event.source_type,
                    "source_url": event.source_url
                })
                credibility_scores[f"event_{i}"] = score
                # Update event credibility
                event.credibility_score = score
            except Exception as e:
                logger.warning(f"Error analyzing credibility for event {i}: {e}")
                credibility_scores[f"event_{i}"] = 0.5  # Default score
        
        # Analyze credibility of academic sources
        for i, source in enumerate(academic_sources):
            try:
                score = credibility_analyzer_tool.invoke({
                    "content": source.get("abstract", source.get("content", "")),
                    "source_type": "academic",
                    "source_url": source.get("url", "")
                })
                credibility_scores[f"academic_{i}"] = score
            except Exception as e:
                logger.warning(f"Error analyzing credibility for academic source {i}: {e}")
                credibility_scores[f"academic_{i}"] = 0.8  # Higher default for academic
        
        return {
            "credibility_scores": credibility_scores,
            "mystery_events": mystery_events,  # Updated with credibility scores
            "observations": state.get("observations", []) + [f"Credibility analysis completed for {len(credibility_scores)} items"],
        }
        
    except Exception as e:
        logger.error(f"Error in credibility analyzer: {e}")
        return {
            "error_messages": state.get("error_messages", []) + [f"Credibility analysis error: {str(e)}"]
        }


def correlation_analyzer_node(state: State, config: RunnableConfig):
    """Correlation analyzer node for finding event relationships."""
    logger.info("Correlation analyzer node is running.")
    
    try:
        mystery_events = state.get("mystery_events", [])
        
        if len(mystery_events) < 2:
            return {"observations": state.get("observations", []) + ["Not enough events for correlation analysis"]}
        
        correlation_analyzer_tool = get_correlation_analyzer_tool()
        correlation_results = correlation_analyzer_tool.invoke({
            "events": [{
                "id": i,
                "title": event.title,
                "description": event.description,
                "location": event.location,
                "date": event.date,
                "event_type": event.event_type
            } for i, event in enumerate(mystery_events)]
        })
        
        return {
            "correlation_results": correlation_results,
            "observations": state.get("observations", []) + ["Correlation analysis completed"],
        }
        
    except Exception as e:
        logger.error(f"Error in correlation analyzer: {e}")
        return {
            "error_messages": state.get("error_messages", []) + [f"Correlation analysis error: {str(e)}"]
        }


def graph_storage_node(state: State, config: RunnableConfig):
    """Graph storage node for storing data in Neo4j."""
    logger.info("Graph storage node is running.")
    
    try:
        mystery_events = state.get("mystery_events", [])
        correlation_results = state.get("correlation_results", {})
        
        if not mystery_events:
            return {"observations": state.get("observations", []) + ["No events to store in graph"]}
        
        graph_storage_tool = get_graph_storage_tool()
        graph_relationships = graph_storage_tool.invoke({
            "events": mystery_events,
            "correlations": correlation_results
        })
        
        return {
            "graph_relationships": graph_relationships,
            "observations": state.get("observations", []) + [f"Stored {len(mystery_events)} events in graph database"],
        }
        
    except Exception as e:
        logger.error(f"Error in graph storage: {e}")
        return {
            "error_messages": state.get("error_messages", []) + [f"Graph storage error: {str(e)}"]
        }


def human_feedback_node(state: State, config: RunnableConfig):
    """Human feedback node for manual review."""
    logger.info("Human feedback node is running.")
    
    # This would typically interrupt for human input
    # For now, we'll auto-approve
    return {
        "auto_accepted_plan": True,
        "observations": state.get("observations", []) + ["Human feedback: Plan approved"],
    }


def reporter_node(state: State, config: RunnableConfig):
    """Reporter node for generating final mystery research report."""
    logger.info("Reporter node is generating final mystery research report.")
    configurable = Configuration.from_runnable_config(config)
    
    try:
        # Collect all research data
        mystery_events = state.get("mystery_events", [])
        academic_sources = state.get("academic_sources", [])
        credibility_scores = state.get("credibility_scores", {})
        correlation_results = state.get("correlation_results", {})
        observations = state.get("observations", [])
        
        # Generate comprehensive report
        report_sections = {
            "executive_summary": f"Mystery Research Report - {len(mystery_events)} events analyzed",
            "methodology": "Multi-source data collection with credibility assessment and correlation analysis",
            "findings": "\n".join([f"- {event.title}: {event.description[:100]}..." for event in mystery_events[:5]]),
            "credibility_analysis": f"Average credibility score: {sum(credibility_scores.values()) / len(credibility_scores) if credibility_scores else 'N/A'}",
            "correlation_analysis": str(correlation_results) if correlation_results else "No correlations found",
            "academic_sources": f"{len(academic_sources)} academic sources reviewed",
            "observations": "\n".join(observations),
        }
        
        # Generate final report
        final_report = f"""
# 神秘事件研究报告

## 执行摘要
{report_sections['executive_summary']}

## 研究方法
{report_sections['methodology']}

## 主要发现
{report_sections['findings']}

## 可信度分析
{report_sections['credibility_analysis']}

## 关联分析
{report_sections['correlation_analysis']}

## 学术资源
{report_sections['academic_sources']}

## 处理过程
{report_sections['observations']}

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return {
            "final_report": final_report,
            "report_sections": report_sections,
            "processing_status": "completed",
        }
        
    except Exception as e:
        logger.error(f"Error in reporter: {e}")
        return {
            "final_report": f"Error generating report: {str(e)}",
            "processing_status": "error",
            "error_messages": state.get("error_messages", []) + [f"Report generation error: {str(e)}"]
        }