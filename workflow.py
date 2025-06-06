# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT

import asyncio
import logging
from graph import build_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_debug_logging():
    """Enable debug level logging for more detailed execution information."""
    logging.getLogger("Lingjing").setLevel(logging.DEBUG)


logger = logging.getLogger(__name__)

# Create the graph
graph = build_graph()


async def run_mystery_research_workflow_async(
    user_input: str,
    debug: bool = False,
    max_plan_iterations: int = 2,
    max_step_num: int = 5,
    enable_background_investigation: bool = True,
    enable_academic_search: bool = True,
    enable_credibility_filter: bool = True,
    enable_correlation_analysis: bool = True,
    enable_graph_storage: bool = True,
):
    """Run the mystery research workflow asynchronously with the given user input.

    Args:
        user_input: The user's query or request about mysterious events
        debug: If True, enables debug level logging
        max_plan_iterations: Maximum number of plan iterations
        max_step_num: Maximum number of steps in a plan
        enable_background_investigation: If True, performs web search before planning
        enable_academic_search: If True, includes academic database search
        enable_credibility_filter: If True, applies credibility filtering
        enable_correlation_analysis: If True, performs event correlation analysis
        enable_graph_storage: If True, stores results in Neo4j graph database

    Returns:
        The final state after the workflow completes
    """
    if not user_input:
        raise ValueError("Input could not be empty")

    if debug:
        enable_debug_logging()

    logger.info(f"Starting mystery research workflow with input: {user_input}")

    # Initial state for mystery research
    initial_state = {
        "messages": [{"role": "user", "content": user_input}],
        "locale": "zh-CN",  # Default to Chinese for mystery research
        "observations": [],
        "resources": [],
        "plan_iterations": 0,
        "current_plan": None,
        "final_report": "",
        "auto_accepted_plan": False,
        "enable_background_investigation": enable_background_investigation,
        "enable_academic_search": enable_academic_search,
        "enable_credibility_filter": enable_credibility_filter,
        "enable_correlation_analysis": enable_correlation_analysis,
        "enable_graph_storage": enable_graph_storage,
        "background_investigation_results": None,
        "mystery_events": [],
        "correlation_results": {},
        "credibility_scores": {},
        "academic_sources": [],
        "graph_relationships": [],
    }

    # Configuration for mystery research
    config = {
        "configurable": {
            "max_plan_iterations": max_plan_iterations,
            "max_step_num": max_step_num,
            "max_search_results": 10,  # Increased for comprehensive research
            "enable_academic_search": enable_academic_search,
            "enable_credibility_filter": enable_credibility_filter,
            "enable_correlation_analysis": enable_correlation_analysis,
            "enable_graph_storage": enable_graph_storage,
        }
    }

    try:
        # Run the workflow
        final_state = await graph.ainvoke(initial_state, config)
        logger.info("Mystery research workflow completed successfully")
        return final_state
    except Exception as e:
        logger.error(f"Error in mystery research workflow: {e}")
        raise


def run_mystery_research_workflow(
    user_input: str,
    debug: bool = False,
    max_plan_iterations: int = 2,
    max_step_num: int = 5,
    enable_background_investigation: bool = True,
    enable_academic_search: bool = True,
    enable_credibility_filter: bool = True,
    enable_correlation_analysis: bool = True,
    enable_graph_storage: bool = True,
):
    """Synchronous wrapper for the mystery research workflow.

    Args:
        user_input: The user's query or request about mysterious events
        debug: If True, enables debug level logging
        max_plan_iterations: Maximum number of plan iterations
        max_step_num: Maximum number of steps in a plan
        enable_background_investigation: If True, performs web search before planning
        enable_academic_search: If True, includes academic database search
        enable_credibility_filter: If True, applies credibility filtering
        enable_correlation_analysis: If True, performs event correlation analysis
        enable_graph_storage: If True, stores results in Neo4j graph database

    Returns:
        The final state after the workflow completes
    """
    return asyncio.run(
        run_mystery_research_workflow_async(
            user_input=user_input,
            debug=debug,
            max_plan_iterations=max_plan_iterations,
            max_step_num=max_step_num,
            enable_background_investigation=enable_background_investigation,
            enable_academic_search=enable_academic_search,
            enable_credibility_filter=enable_credibility_filter,
            enable_correlation_analysis=enable_correlation_analysis,
            enable_graph_storage=enable_graph_storage,
        )
    )


if __name__ == "__main__":
    # Example usage
    result = run_mystery_research_workflow(
        "请研究关于UFO目击事件的最新报告和学术研究",
        debug=True
    )
    print(f"Research completed: {result['final_report']}")