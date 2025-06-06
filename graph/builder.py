# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from prompts.planner_model import StepType

from .types import State
from .nodes import (
    coordinator_node,
    planner_node,
    reporter_node,
    mystery_researcher_node,
    academic_researcher_node,
    credibility_analyzer_node,
    correlation_analyzer_node,
    graph_storage_node,
    human_feedback_node,
    background_investigation_node,
)


def continue_to_running_research_team(state: State):
    """Determine the next node based on current plan and mystery research requirements."""
    current_plan = state.get("current_plan")
    if not current_plan or not current_plan.steps:
        return "planner"
    if all(step.execution_res for step in current_plan.steps):
        return "planner"
    
    # Find the next unexecuted step
    for step in current_plan.steps:
        if not step.execution_res:
            break
    
    # Route based on step type and mystery research features
    if step.step_type and step.step_type == StepType.RESEARCH:
        # Check if academic search is needed
        if state.get("enable_academic_search") and "academic" in step.description.lower():
            return "academic_researcher"
        else:
            return "mystery_researcher"
    elif step.step_type and step.step_type == StepType.PROCESSING:
        # Check what kind of processing is needed
        if "credibility" in step.description.lower() and state.get("enable_credibility_filter"):
            return "credibility_analyzer"
        elif "correlation" in step.description.lower() and state.get("enable_correlation_analysis"):
            return "correlation_analyzer"
        elif "graph" in step.description.lower() and state.get("enable_graph_storage"):
            return "graph_storage"
        else:
            return "mystery_researcher"
    
    return "planner"


def should_continue_analysis(state: State):
    """Determine if additional analysis steps are needed."""
    current_plan = state.get("current_plan")
    if not current_plan:
        return "reporter"
    
    # Check if credibility analysis is needed and enabled
    if (state.get("enable_credibility_filter") and 
        not state.get("credibility_scores") and 
        state.get("mystery_events")):
        return "credibility_analyzer"
    
    # Check if correlation analysis is needed and enabled
    if (state.get("enable_correlation_analysis") and 
        not state.get("correlation_results") and 
        len(state.get("mystery_events", [])) > 1):
        return "correlation_analyzer"
    
    # Check if graph storage is needed and enabled
    if (state.get("enable_graph_storage") and 
        not state.get("graph_relationships") and 
        state.get("mystery_events")):
        return "graph_storage"
    
    return "reporter"


def _build_base_graph():
    """Build and return the base state graph with all nodes and edges for mystery research."""
    builder = StateGraph(State)
    
    # Add all nodes
    builder.add_edge(START, "coordinator")
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("background_investigator", background_investigation_node)
    builder.add_node("planner", planner_node)
    builder.add_node("reporter", reporter_node)
    builder.add_node("mystery_researcher", mystery_researcher_node)
    builder.add_node("academic_researcher", academic_researcher_node)
    builder.add_node("credibility_analyzer", credibility_analyzer_node)
    builder.add_node("correlation_analyzer", correlation_analyzer_node)
    builder.add_node("graph_storage", graph_storage_node)
    builder.add_node("human_feedback", human_feedback_node)
    
    # Add edges
    builder.add_edge("background_investigator", "planner")
    
    # Conditional edges from coordinator
    builder.add_conditional_edges(
        "coordinator",
        lambda state: "background_investigator" if state.get("enable_background_investigation") else "planner",
        ["background_investigator", "planner"]
    )
    
    # Conditional edges from planner
    builder.add_conditional_edges(
        "planner",
        continue_to_running_research_team,
        [
            "mystery_researcher",
            "academic_researcher", 
            "credibility_analyzer",
            "correlation_analyzer",
            "graph_storage",
            "human_feedback",
            "reporter"
        ],
    )
    
    # Research nodes back to planner or analysis
    builder.add_conditional_edges(
        "mystery_researcher",
        should_continue_analysis,
        ["planner", "credibility_analyzer", "correlation_analyzer", "graph_storage", "reporter"]
    )
    
    builder.add_conditional_edges(
        "academic_researcher",
        should_continue_analysis,
        ["planner", "credibility_analyzer", "correlation_analyzer", "graph_storage", "reporter"]
    )
    
    # Analysis nodes
    builder.add_conditional_edges(
        "credibility_analyzer",
        should_continue_analysis,
        ["correlation_analyzer", "graph_storage", "reporter"]
    )
    
    builder.add_conditional_edges(
        "correlation_analyzer",
        should_continue_analysis,
        ["graph_storage", "reporter"]
    )
    
    builder.add_edge("graph_storage", "reporter")
    
    # Human feedback and reporter
    builder.add_edge("human_feedback", "planner")
    builder.add_edge("reporter", END)
    
    return builder


def build_graph():
    """Build and compile the mystery research graph."""
    builder = _build_base_graph()
    return builder.compile()


def build_graph_with_memory():
    """Build and compile the mystery research graph with memory."""
    builder = _build_base_graph()
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)