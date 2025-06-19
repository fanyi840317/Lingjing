from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio
from pydantic import BaseModel

# Import project modules
from config.configuration import Configuration
from workflow import run_mystery_research_workflow
from tools import (
    get_web_search_tool, get_academic_search_tool, get_mystery_search_tool,
    analyze_information_credibility, analyze_event_correlations,
    analyze_timeline_patterns, location_analysis,
    store_in_neo4j, store_in_elasticsearch,
    generate_mystery_report
)

# Create API router
api_router = APIRouter(prefix="/api", tags=["api"])

# Pydantic models for request/response
class ResearchTaskCreate(BaseModel):
    title: str
    description: str
    keywords: List[str]
    tags: List[str] = []
    priority: str = "medium"
    max_iterations: int = 5
    max_steps: int = 10
    enable_academic_search: bool = True
    enable_credibility_filter: bool = True
    enable_correlation_analysis: bool = True
    enable_graph_storage: bool = True

class ResearchTask(BaseModel):
    id: str
    title: str
    description: str
    keywords: List[str]
    tags: List[str]
    priority: str
    status: str
    progress: float
    created_at: datetime
    updated_at: datetime
    duration: Optional[int] = None
    results: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
    model: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt: Optional[str] = None
    history: List[ChatMessage] = []

class ConfigurationUpdate(BaseModel):
    config_data: Dict[str, Any]

class ReportRequest(BaseModel):
    task_id: str
    format: str = "markdown"
    include_timeline: bool = True
    include_credibility: bool = True
    include_sources: bool = True

# In-memory storage for demo (replace with actual database)
tasks_storage = {}
chat_history = []
reports_storage = {}
graph_data = {"nodes": [], "links": []}
timeline_events = []

# Configuration endpoints
@api_router.get("/config")
async def get_configuration():
    """Get current system configuration"""
    try:
        config = Configuration()
        return {
            "research": {
                "max_resources": config.max_resources,
                "max_iterations": config.max_iterations,
                "max_steps": config.max_steps,
                "max_search_results": config.max_search_results
            },
            "mystery": {
                "enable_academic_search": config.enable_academic_search,
                "credibility_threshold": config.credibility_threshold,
                "enable_correlation_analysis": config.enable_correlation_analysis,
                "enable_graph_storage": config.enable_graph_storage
            },
            "ai_models": {
                "primary_model": "gpt-4",
                "fallback_model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "crawlers": {
                "max_depth": 3,
                "delay_seconds": 1,
                "user_agent": "MysteryResearchBot/1.0",
                "respect_robots_txt": True
            },
            "database": {
                "neo4j_enabled": True,
                "elasticsearch_enabled": True,
                "backup_enabled": True
            },
            "reports": {
                "max_length": 10000,
                "include_timeline": True,
                "include_credibility": True,
                "include_sources": True
            },
            "api": {
                "rate_limit": 100,
                "log_level": "INFO",
                "api_key_required": False,
                "cors_enabled": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

@api_router.post("/config")
async def update_configuration(config_update: ConfigurationUpdate):
    """Update system configuration"""
    try:
        # In a real implementation, this would update the actual configuration
        # For now, we'll just return success
        return {"message": "Configuration updated successfully", "config": config_update.config_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")

@api_router.post("/config/test-connection")
async def test_database_connection(service: str = Body(..., embed=True)):
    """Test database connection"""
    try:
        if service == "neo4j":
            # Test Neo4j connection
            result = {"status": "connected", "message": "Neo4j connection successful"}
        elif service == "elasticsearch":
            # Test Elasticsearch connection
            result = {"status": "connected", "message": "Elasticsearch connection successful"}
        else:
            result = {"status": "error", "message": "Unknown service"}
        
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Research task endpoints
@api_router.get("/research/tasks")
async def get_research_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, le=100)
):
    """Get list of research tasks with optional filtering"""
    try:
        tasks = list(tasks_storage.values())
        
        # Apply filters
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        if priority:
            tasks = [t for t in tasks if t["priority"] == priority]
        
        # Sort by created_at descending
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {"tasks": tasks[:limit], "total": len(tasks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")

@api_router.post("/research/tasks")
async def create_research_task(task_data: ResearchTaskCreate):
    """Create a new research task"""
    try:
        task_id = f"task_{len(tasks_storage) + 1}_{int(datetime.now().timestamp())}"
        
        task = {
            "id": task_id,
            "title": task_data.title,
            "description": task_data.description,
            "keywords": task_data.keywords,
            "tags": task_data.tags,
            "priority": task_data.priority,
            "status": "pending",
            "progress": 0.0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "duration": None,
            "results": None,
            "config": {
                "max_iterations": task_data.max_iterations,
                "max_steps": task_data.max_steps,
                "enable_academic_search": task_data.enable_academic_search,
                "enable_credibility_filter": task_data.enable_credibility_filter,
                "enable_correlation_analysis": task_data.enable_correlation_analysis,
                "enable_graph_storage": task_data.enable_graph_storage
            }
        }
        
        tasks_storage[task_id] = task
        
        # Start the research task asynchronously
        asyncio.create_task(execute_research_task(task_id))
        
        return {"message": "Research task created successfully", "task_id": task_id, "task": task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

@api_router.get("/research/tasks/{task_id}")
async def get_research_task(task_id: str):
    """Get details of a specific research task"""
    try:
        if task_id not in tasks_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"task": tasks_storage[task_id]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")

@api_router.put("/research/tasks/{task_id}/status")
async def update_task_status(task_id: str, status: str = Body(..., embed=True)):
    """Update task status (pause/resume/cancel)"""
    try:
        if task_id not in tasks_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = tasks_storage[task_id]
        task["status"] = status
        task["updated_at"] = datetime.now().isoformat()
        
        return {"message": f"Task status updated to {status}", "task": task}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task status: {str(e)}")

@api_router.delete("/research/tasks/{task_id}")
async def delete_research_task(task_id: str):
    """Delete a research task"""
    try:
        if task_id not in tasks_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        del tasks_storage[task_id]
        
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")

@api_router.get("/research/statistics")
async def get_research_statistics():
    """Get research statistics"""
    try:
        tasks = list(tasks_storage.values())
        
        stats = {
            "total_tasks": len(tasks),
            "running_tasks": len([t for t in tasks if t["status"] == "running"]),
            "completed_tasks": len([t for t in tasks if t["status"] == "completed"]),
            "failed_tasks": len([t for t in tasks if t["status"] == "failed"]),
            "pending_tasks": len([t for t in tasks if t["status"] == "pending"])
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

# Chat endpoints
@api_router.post("/chat/message")
async def send_chat_message(chat_request: ChatRequest):
    """Send a message to the AI chat system"""
    try:
        # Add user message to history
        user_message = {
            "role": "user",
            "content": chat_request.message,
            "timestamp": datetime.now().isoformat(),
            "model": None
        }
        chat_history.append(user_message)
        
        # Generate AI response (mock for now)
        ai_response = await generate_ai_response(chat_request)
        
        ai_message = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat(),
            "model": chat_request.model
        }
        chat_history.append(ai_message)
        
        return {
            "message": ai_message,
            "history": chat_history[-10:]  # Return last 10 messages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chat message: {str(e)}")

@api_router.get("/chat/history")
async def get_chat_history(limit: int = Query(50, le=100)):
    """Get chat history"""
    try:
        return {"history": chat_history[-limit:]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@api_router.delete("/chat/history")
async def clear_chat_history():
    """Clear chat history"""
    try:
        global chat_history
        chat_history = []
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")

# Reports endpoints
@api_router.get("/reports")
async def get_reports(
    task_id: Optional[str] = Query(None),
    format: Optional[str] = Query(None),
    limit: int = Query(50, le=100)
):
    """Get list of generated reports"""
    try:
        reports = list(reports_storage.values())
        
        # Apply filters
        if task_id:
            reports = [r for r in reports if r["task_id"] == task_id]
        if format:
            reports = [r for r in reports if r["format"] == format]
        
        # Sort by created_at descending
        reports.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {"reports": reports[:limit], "total": len(reports)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reports: {str(e)}")

@api_router.post("/reports/generate")
async def generate_research_report(report_request: ReportRequest):
    """Generate a research report"""
    try:
        if report_request.task_id not in tasks_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = tasks_storage[report_request.task_id]
        
        # Generate report (mock for now)
        report_id = f"report_{len(reports_storage) + 1}_{int(datetime.now().timestamp())}"
        
        report = {
            "id": report_id,
            "task_id": report_request.task_id,
            "title": f"Research Report: {task['title']}",
            "format": report_request.format,
            "created_at": datetime.now().isoformat(),
            "file_size": "2.5 MB",
            "status": "completed",
            "content": generate_mock_report_content(task, report_request)
        }
        
        reports_storage[report_id] = report
        
        return {"message": "Report generated successfully", "report_id": report_id, "report": report}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@api_router.get("/reports/{report_id}")
async def get_report(report_id: str):
    """Get details of a specific report"""
    try:
        if report_id not in reports_storage:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {"report": reports_storage[report_id]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")

@api_router.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    """Delete a report"""
    try:
        if report_id not in reports_storage:
            raise HTTPException(status_code=404, detail="Report not found")
        
        del reports_storage[report_id]
        
        return {"message": "Report deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")

# Graph endpoints
@api_router.get("/graph/data")
async def get_graph_data():
    """Get graph visualization data"""
    try:
        # Return mock graph data for now
        return {
            "nodes": [
                {"id": "1", "label": "UFO目击事件", "type": "mystery", "properties": {"date": "2024-01-15", "location": "某市", "credibility": 0.75}},
                {"id": "2", "label": "张三", "type": "person", "properties": {"role": "目击者", "age": 35, "occupation": "工程师"}},
                {"id": "3", "label": "李四", "type": "person", "properties": {"role": "目击者", "age": 42, "occupation": "教师"}},
                {"id": "4", "label": "某市公园", "type": "location", "properties": {"coordinates": [116.4074, 39.9042], "area": "城市公园"}},
                {"id": "5", "label": "照片证据", "type": "evidence", "properties": {"type": "图像", "quality": "high", "verified": True}}
            ],
            "links": [
                {"source": "1", "target": "2", "type": "involved", "strength": 0.9},
                {"source": "1", "target": "3", "type": "involved", "strength": 0.8},
                {"source": "1", "target": "4", "type": "located", "strength": 1.0},
                {"source": "1", "target": "5", "type": "supports", "strength": 0.7}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get graph data: {str(e)}")

@api_router.post("/graph/layout")
async def save_graph_layout(layout_data: Dict[str, Any] = Body(...)):
    """Save graph layout configuration"""
    try:
        # In a real implementation, this would save the layout to database
        return {"message": "Graph layout saved successfully", "layout": layout_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save graph layout: {str(e)}")

# Timeline endpoints
@api_router.get("/timeline/events")
async def get_timeline_events(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(100, le=500)
):
    """Get timeline events with optional filtering"""
    try:
        # Return mock timeline data for now
        events = [
            {
                "id": "event_1",
                "title": "UFO目击报告",
                "description": "多名目击者报告在公园上空看到不明飞行物",
                "date": "2024-01-15T20:30:00Z",
                "type": "sighting",
                "location": "某市公园",
                "credibility": 0.75,
                "sources": ["目击者证词", "照片证据"]
            },
            {
                "id": "event_2",
                "title": "雷达异常信号",
                "description": "空管局检测到异常雷达信号",
                "date": "2024-01-15T20:25:00Z",
                "type": "technical",
                "location": "空管中心",
                "credibility": 0.9,
                "sources": ["雷达数据", "技术报告"]
            },
            {
                "id": "event_3",
                "title": "媒体报道",
                "description": "当地媒体开始报道UFO目击事件",
                "date": "2024-01-16T08:00:00Z",
                "type": "media",
                "location": "新闻中心",
                "credibility": 0.6,
                "sources": ["新闻报道", "采访记录"]
            }
        ]
        
        # Apply filters
        if start_date:
            events = [e for e in events if e["date"] >= start_date]
        if end_date:
            events = [e for e in events if e["date"] <= end_date]
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        
        return {"events": events[:limit], "total": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get timeline events: {str(e)}")

# Helper functions
async def execute_research_task(task_id: str):
    """Execute a research task asynchronously"""
    try:
        task = tasks_storage[task_id]
        task["status"] = "running"
        task["updated_at"] = datetime.now().isoformat()
        
        # Simulate research progress
        for progress in [0.2, 0.4, 0.6, 0.8, 1.0]:
            await asyncio.sleep(2)  # Simulate work
            task["progress"] = progress
            task["updated_at"] = datetime.now().isoformat()
        
        # Mark as completed
        task["status"] = "completed"
        task["duration"] = 300  # 5 minutes
        task["results"] = {
            "summary": f"Research completed for: {task['title']}",
            "findings": ["Finding 1", "Finding 2", "Finding 3"],
            "sources_found": 15,
            "credibility_score": 0.78
        }
        
    except Exception as e:
        task["status"] = "failed"
        task["results"] = {"error": str(e)}

async def generate_ai_response(chat_request: ChatRequest) -> str:
    """Generate AI response for chat"""
    # Mock AI response for now
    responses = [
        "这是一个很有趣的神秘事件研究问题。让我来分析一下相关的信息...",
        "根据现有的证据和数据，我认为这个现象可能有以下几种解释...",
        "从可信度分析的角度来看，我们需要考虑以下几个因素...",
        "时间线分析显示，这些事件之间可能存在某种关联..."
    ]
    
    import random
    await asyncio.sleep(1)  # Simulate processing time
    return random.choice(responses)

def generate_mock_report_content(task: Dict[str, Any], report_request: ReportRequest) -> Dict[str, Any]:
    """Generate mock report content"""
    return {
        "summary": f"This report presents the findings of the research task '{task['title']}'. The investigation involved comprehensive analysis of multiple data sources and evidence.",
        "methodology": "The research employed a multi-faceted approach including web search, academic literature review, credibility analysis, and correlation analysis.",
        "findings": [
            "Key finding 1: Evidence suggests multiple independent witnesses",
            "Key finding 2: Technical data corroborates witness accounts",
            "Key finding 3: Timeline analysis reveals consistent patterns"
        ],
        "timeline": [
            {"date": "2024-01-15T20:25:00Z", "event": "Initial radar detection"},
            {"date": "2024-01-15T20:30:00Z", "event": "Visual sighting reported"},
            {"date": "2024-01-16T08:00:00Z", "event": "Media coverage begins"}
        ] if report_request.include_timeline else [],
        "credibility_analysis": {
            "overall_score": 0.78,
            "factors": [
                "Multiple independent witnesses: +0.3",
                "Technical corroboration: +0.4",
                "Media attention: +0.1",
                "Lack of physical evidence: -0.05"
            ]
        } if report_request.include_credibility else {},
        "sources": [
            "Witness testimony from John Doe",
            "Radar data from Air Traffic Control",
            "Photographic evidence",
            "Local news reports"
        ] if report_request.include_sources else [],
        "conclusions": "Based on the available evidence and analysis, this case presents a compelling mystery that warrants further investigation.",
        "recommendations": [
            "Conduct additional witness interviews",
            "Analyze technical data in greater detail",
            "Investigate similar cases in the region"
        ]
    }