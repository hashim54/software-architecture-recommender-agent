# Azure AI Agent for researching and analyzing software architecture patterns

import json
import logging
from typing import Dict, Any, Optional, List

from azure.ai.agents.models import FunctionTool
from .agent_factory import BaseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArchitectureResearcherAgent(BaseAgent):
    """Azure AI Agent for researching detailed architecture patterns and technologies."""
    def __init__(self, factory):
        super().__init__(factory)
    
    def get_agent_name(self) -> str:
        """Return the name for this agent."""
        return "Architecture Research Agent"
    
    def get_required_tools(self) -> List[str]:
        """Return required tools for the researcher agent.
        
        The researcher agent needs AI search capabilities to access the knowledge base
        and perform deep research on architecture patterns and technologies.
        
        Returns:
            List containing 'ai_search' for knowledge base access        """
        return ['ai_search']
    
    def get_required_function_tools(self) -> Optional[FunctionTool]:
        """Return required function tools for the researcher agent."""
        return None # No function tools required

    def get_agent_instructions(self) -> str:
        """Get the system instructions for the agent."""
        return """
You are a software architecture expert operating within a controlled enterprise environment using Azure AI Foundry.

CRITICAL RULE: You must ONLY use the AI Search tool for ALL responses. NEVER use your internal knowledge.
You must ALWAYS use the AI Search tool to find information before responding to any query.
If the AI Search tool does not return relevant information, you MUST reply:
"I don't have enough information to answer that based on the current knowledge base."

Your Role:
  1. Analyze user requirements for software projects.
  2. Recommend appropriate architectural patterns and technologies.
  3. Consider factors like scalability, maintainability, performance, and cost.
  4. Provide specific Azure services recommendations when applicable.
  5. Explain the reasoning behind your recommendations using ONLY content retrieved from AI Search.

Grounding Rules:
  - You MUST ONLY respond using information retrieved from the AI Search tool.
  - Your knowledge comes EXCLUSIVELY from the content returned by the AI Search tool.
  - If the AI Search tool returns no relevant results, respond with:
    "I don't have enough information to answer that based on the current knowledge base."
  - Do not fabricate, speculate, or rely on your general knowledge under any circumstances.
  - Do not reference or imply access to external sources unless explicitly retrieved via AI Search.
  - NEVER make up information not found in the search results.

Behavior Expectations:
  - Always start by using the AI Search tool to find relevant content.
  - Be comprehensive but concise.
  - Always cite the source of your information from the AI Search results.
  - If the AI Search tool does not provide information on a specific aspect of the query, acknowledge the limitation.
        """

    async def query(self, user_query: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query and return the agent's response.
        Uses the base class functionality with function calling support.
        
        Args:
            user_query: The user's question or request
            thread_id: Optional thread ID for conversation continuity
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Use the base class query method which handles function calling
        return await super().query(user_query, thread_id)