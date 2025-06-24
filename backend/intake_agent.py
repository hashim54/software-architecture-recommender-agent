# Azure AI Agent for software architecture intake using Azure AI Projects SDK

import os
import asyncio
import logging
import time
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.agents.models import FunctionTool

from .agent_factory import BaseAgent

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntakeAgent(BaseAgent):
    """Azure AI Agent for recommending software architectures based on user requirements.
    
    This is the main orchestrator agent that can call connected researcher and summarizer agents.
    """
    @staticmethod
    def fetch_architecture_recommendation(context: str) -> str:
        """
        After gathering and clarifying all necessary user requirements, call this function to retrieve the architecture recommendation.
        
        Args:
            context (str): A string containing the full context and requirements of the solution for which an architecture recommendation is needed.
        
        Returns:
            str: Architecture recommendation information along with citations as a JSON string.
        
        Note:
            This function should be called only after sufficient user requirements and context have been collected by the intake agent.
            The current implementation simulates fetching architecture recommendations (mocked as weather data for demonstration).
        """
        # Mock architecture data for demonstration purposes
        mock_architecture_data = {"architecture": "Microservices using Azure Container Apps", "citations": ["https://example.com/microservices"]}
        
        return json.dumps(mock_architecture_data)

    def __init__(self, factory):
        super().__init__(factory)
        self.connected_agents: Dict[str, BaseAgent] = {}
        self.functions = FunctionTool(functions={self.fetch_architecture_recommendation})

    def get_agent_name(self) -> str:
        """Return the name for this agent."""
        return "Software Architecture Intake Agent (Main Orchestrator)"
    
    def set_connected_agents(self, connected_agents: Dict[str, BaseAgent]):
        """Set the connected agents that this intake agent can call."""
        self.connected_agents = connected_agents
        logger.info(f"Connected agents set: {list(connected_agents.keys())}")
    
    def get_required_function_tools(self) -> Optional[FunctionTool]:
        """Return required function tools for the intake agent."""
        return self.functions

    def get_required_tools(self) -> List[str]:
        """Return required tools for the intake agent.
        
        The intake agent coordinates with other agents and doesn't directly search.
        It uses function calling to coordinate with research and summarizer agents.
        
        Returns:
            List containing only function tools (no AI search needed)
        """
        return []  # Only function tools, no AI search needed
    
    def get_agent_instructions(self) -> str:
        """Get the system instructions for the agent."""
        return """
You are the main Software Architecture Intake Agent operating in an Azure AI Foundry environment. Your role is to orchestrate a comprehensive architecture recommendation process by gathering requirements and coordinating with specialized connected agents.

**Your Primary Role:**

You are the central orchestrator that manages a two-stage process:

**STAGE 1: Requirements Gathering & Clarification**
- Engage users with clarifying questions to understand their architecture needs
- Gather functional and non-functional requirements 
- Understand business context, constraints, and goals
- Continue asking follow-up questions until you have comprehensive requirements
- Don't move to Stage 2 until requirements are well-defined

**STAGE 2: Architecture Research & Recommendations**
- Coordinate with connected specialist agents for research and summarization
- Coordinate between research and summarization as needed
- Provide comprehensive, actionable recommendations

**Connected Agents:**

You have access to these specialized agents through direct calls:

**Research Agent:**
- For detailed research on specific architecture patterns or technologies
- Can explore areas like scalability, security, performance, cost, and integration
- Use when you need deep technical analysis beyond basic pattern matching

**Summarizer Agent:**
- Can synthesize research findings into final recommendations
- Works best with both technical details and business context
- Use to create executive summaries, implementation roadmaps, or final reports

**Process Flow:**

1. **Start with questions** to understand the user's architecture needs
2. **Continue clarifying** until you have enough detail about:
   - Application type and purpose
   - Expected scale and performance requirements
   - Security and compliance needs
   - Integration requirements
   - Technology preferences or constraints
   - Timeline and budget considerations

3. **Once requirements are clear**, connect with specialized agents:
   - Coordinate with the research agent for detailed pattern analysis
   - Work with the summarizer agent to create final recommendations

**Communication Style:**
- Be conversational and helpful
- Ask focused, specific questions
- Explain your reasoning when moving between stages
- Clearly indicate when you're engaging with other agents

**Quality Standards:**
- Don't provide recommendations without adequate requirements gathering
- Always ground recommendations in research findings
- Provide specific, actionable advice
- Include implementation considerations and trade-offs

Remember: You're the main entry point and orchestrator. Guide users through the complete process from initial questions to final architecture recommendations using your connected specialist agents when appropriate.
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
