from typing import Optional, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from .agent_factory import agent_factory, BaseAgent
from .intake_agent import IntakeAgent
from .architecture_researcher_agent import ArchitectureResearcherAgent
from .summarizer_agent import SummarizerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Software Architecture Recommender API", version="3.0.0")

# Global main agent - the intake agent acts as the orchestrator
main_agent: Optional[IntakeAgent] = None

class QueryRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None

class QueryResponse(BaseModel):
    assistant_response: str
    thread_id: str
    status: str

class AgentStatusResponse(BaseModel):
    main_agent: str
    connected_agents: Dict[str, str]
    status: str

@app.on_event("startup")
async def startup_event():
    """Initialize the main orchestrator agent with connected agents on application startup."""
    global main_agent
    try:
        logger.info("Initializing Connected Agents System...")
        
        # Create connected specialist agents
        research_agent = await agent_factory.create_agent(ArchitectureResearcherAgent)
        # summarizer_agent = await agent_factory.create_agent(SummarizerAgent)
        
        # Create the main intake agent (orchestrator)
        created_agent = await agent_factory.create_agent(IntakeAgent)
        assert isinstance(created_agent, IntakeAgent), "Failed to create IntakeAgent"
        main_agent = created_agent
        
        # # Connect the specialist agents to the main agent
        # connected_agents = {
        #     "researcher": research_agent,
        #     "summarizer": summarizer_agent
        # }
        # main_agent.set_connected_agents(connected_agents)
        
        logger.info("Successfully initialized agents")
        logger.info(f"Main agent: {main_agent.get_agent_name()}")
        # logger.info(f"Connected agents: {list(connected_agents.keys())}")
        
    except Exception as e:
        logger.error(f"Failed to initialize connected agents system: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    global main_agent
    try:
        await agent_factory.cleanup()
        main_agent = None
        logger.info("Connected agents system cleanup completed")
    except Exception as e:
        logger.error(f"Error during agents cleanup: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest) -> QueryResponse:
    """
    Query the main software architecture agent (with connected specialist agents).
    
    Args:
        request: The query request containing user question and optional thread ID
        
    Returns:
        QueryResponse: The agent's response with thread information
    """
    if not main_agent:
        raise HTTPException(status_code=503, detail="Main agent not initialized")
    
    try:
        logger.info(f"Processing query via main orchestrator agent: {request.query[:100]}...")
        
        result = await main_agent.query(
            user_query=request.query,
            thread_id=request.thread_id
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query via main agent: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/agents", response_model=AgentStatusResponse)
def list_agents():
    """List the main agent and its connected agents status."""
    if not main_agent:
        return AgentStatusResponse(
            main_agent="not_initialized",
            connected_agents={},
            status="initializing"
        )
    
    # Get connected agents status
    connected_status = {}
    for agent_name, agent in main_agent.connected_agents.items():
        connected_status[agent_name] = "ready" if agent._initialized else "initializing"
    
    return AgentStatusResponse(
        main_agent="ready" if main_agent._initialized else "initializing",
        connected_agents=connected_status,
        status="ready" if main_agent._initialized else "initializing"
    )

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if main_agent and main_agent._initialized else "initializing",
        "service": "Software Architecture Recommender API - Connected Agents"
    }

@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "Software Architecture Recommender API - Connected Agents System",
        "version": "3.0.0",
        "description": "Main orchestrator agent with connected specialist agents for software architecture recommendations",
        "endpoints": {
            "query": "/query - POST - Submit architecture questions to the main orchestrator agent",
            "agents": "/agents - GET - Show main agent and connected agents status",
            "health": "/health - GET - Service health status"
        },
        "architecture": {
            "main_agent": "Intake Agent (Orchestrator) - Gathers requirements and coordinates with specialists",
            "connected_agents": {
                "researcher": "Performs deep research on architecture patterns and technologies",
                "summarizer": "Synthesizes findings into final recommendations and roadmaps"
            }
        },
        "workflow": [
            "1. Main agent gathers requirements through clarifying questions",
            "2. Main agent searches knowledge base for relevant patterns",
            "3. Main agent calls research agent for deep technical analysis when needed",
            "4. Main agent calls summarizer agent for final recommendations and roadmaps",
            "5. All interactions flow through the single main agent endpoint"
        ]
    }
