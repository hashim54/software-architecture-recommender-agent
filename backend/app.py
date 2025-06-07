from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

from .intake_agent import IntakeAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Software Architecture Recommender API", version="1.0.0")

# Global agent instance - will be initialized on startup
agent: Optional[IntakeAgent] = None

class QueryRequest(BaseModel):
    query: str
    thread_id: Optional[str] = None

class QueryResponse(BaseModel):
    assistant_response: str
    thread_id: str
    status: str

@app.on_event("startup")
async def startup_event():
    """Initialize the Azure AI Agent on application startup."""
    global agent
    try:
        logger.info("Initializing Azure AI Agent...")
        agent = await IntakeAgent.create()
        logger.info("Azure AI Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Azure AI Agent: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    global agent
    if agent:
        try:
            await agent.cleanup()
            logger.info("Agent cleanup completed")
        except Exception as e:
            logger.error(f"Error during agent cleanup: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest) -> QueryResponse:
    """
    Query the software architecture recommendation agent.
    
    Args:
        request: The query request containing user question and optional thread ID
        
    Returns:
        QueryResponse: The agent's response with thread information
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(f"Processing query: {request.query[:100]}...")
        
        result = await agent.query(
            user_query=request.query,
            thread_id=request.thread_id
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy" if agent else "initializing",
        "service": "Software Architecture Recommender API"
    }

@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "Software Architecture Recommender API",
        "version": "1.0.0",
        "description": "Azure AI Agent for software architecture recommendations",
        "endpoints": {
            "query": "/query - POST - Submit architecture questions",
            "health": "/health - GET - Service health status"
        }
    }
