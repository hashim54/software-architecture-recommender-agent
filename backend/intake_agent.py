# Legacy procedural code has been moved to backend/legacy_intake_procedural.py for reference.

# Azure AI Agent for software architecture recommendations using Azure AI Projects SDK
import os
import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from dotenv import load_dotenv
from azure.ai.agents.models import AzureAISearchTool
from azure.ai.projects import AIProjectClient #, ConnectionType
from azure.ai.projects.models import ConnectionType
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceNotFoundError

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntakeAgent:
    """Azure AI Agent for recommending software architectures based on user requirements."""
    
    def __init__(self):
        self.client: Optional[AIProjectClient] = None
        self.agent_id: Optional[str] = None
        self.threads: Dict[str, str] = {}  # thread_id -> thread_id mapping
        self._initialized = False
        
        # Azure configuration from environment
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.project_connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
        self.model_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
        self.search_index_name = os.getenv("AZURE_AI_SEARCH_INDEX_NAME", "software-architecture-index")
        
        if not self.project_connection_string:
            raise ValueError("AZURE_AI_PROJECT_CONNECTION_STRING is required in environment variables")

    @classmethod
    async def create(cls) -> "IntakeAgent":
        """Factory method to create and initialize an IntakeAgent instance."""
        instance = cls()
        await instance._async_init()
        return instance
    
    async def _async_init(self):
        """Asynchronous initialization of the Azure AI Agent."""
        try:
            logger.info("Initializing Azure AI Agent...")
            
            # Create Azure AI Project client with managed identity
            credential = DefaultAzureCredential()
            self.client = AIProjectClient(
                endpoint=self.project_connection_string,
                credential=credential
            )
            
            # Find Azure AI Search connection
            ai_search_conn_id = self._find_search_connection()
            
            if not ai_search_conn_id:
                logger.warning("No Azure AI Search connection found. Creating agent without search capabilities.")
                # Create agent definition without tools
                agent_definition = self.client.agents.create_agent(
                    model=self.model_deployment_name,
                    name="Software Architecture Recommender",
                    instructions=self._get_agent_instructions(),
                    headers={"x-ms-enable-preview": "true"},
                )
            else:
                logger.info(f"Found Azure AI Search connection: {ai_search_conn_id}")
                
                # Create agent definition with Azure AI Search tool and proper tool_resources
                ai_search = AzureAISearchTool(index_connection_id=ai_search_conn_id, index_name=self.search_index_name)

                agent_definition = self.client.agents.create_agent(
                    model=self.model_deployment_name,
                    name="Software Architecture Recommender",
                    instructions=self._get_agent_instructions(),
                    tools=ai_search.definitions,
                    tool_resources=ai_search.resources,
                    headers={"x-ms-enable-preview": "true"},
                )

            self.agent_id = agent_definition.id
            self._initialized = True
            logger.info(f"Azure AI Agent initialized successfully with ID: {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI Agent: {str(e)}")
            raise

    def _find_search_connection(self) -> Optional[str]:
        """Find and return the Azure AI Search connection ID."""
        try:
            for connection in self.client.connections.list():
                if connection.type == ConnectionType.AZURE_AI_SEARCH:
                    logger.info(f"Found Azure AI Search connection: {connection.name}")
                    return connection.id
        except Exception as e:
            logger.error(f"Error finding search connection: {str(e)}")
        return None

    def _get_agent_instructions(self) -> str:
        """Get the system instructions for the agent."""
        return """You are a software architecture expert specializing in providing tailored recommendations 
        based on user requirements. Your role is to:

        1. Analyze user requirements for software projects
        2. Recommend appropriate architectural patterns and technologies
        3. Consider factors like scalability, maintainability, performance, and cost
        4. Provide specific Azure services recommendations when applicable
        5. Explain the reasoning behind your recommendations

        When users ask about software architecture:
        - Ask clarifying questions about requirements, scale, and constraints
        - Provide multiple options with pros and cons
        - Consider both current needs and future growth
        - Include implementation guidance and best practices
        - Use the available search index to find relevant architectural examples

        Be comprehensive but concise in your responses."""

    async def query(self, user_query: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query and return the agent's response.
        
        Args:
            user_query: The user's question or request
            thread_id: Optional thread ID for conversation continuity
            
        Returns:
            Dictionary containing the response and metadata
        """
        if not self._initialized:
            raise RuntimeError("Agent not initialized. Use IntakeAgent.create() to create an instance.")
        
        try:
            # Get or create thread
            thread_id = await self._get_or_create_thread(thread_id)
            
            # Add user message to thread
            self.client.agents.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_query
            )
            
            # Create and poll run
            run = self.client.agents.runs.create_and_process(
                thread_id=thread_id,
                agent_id=self.agent_id
            )
            # Get the assistant's messages from the thread
            messages = self.client.agents.messages.list(thread_id=thread_id)
            
            assistant_response = "I'm sorry, I couldn't generate a response. Please try again."
            # Convert ItemPaged to list and get the latest assistant message
            messages_list = list(messages)
            if messages_list:
                # Messages are typically returned in reverse chronological order (newest first)
                for message in messages_list:
                    if message.role == "assistant":
                        # Extract text content from the message
                        for content in message.content:
                            if hasattr(content, 'text') and hasattr(content.text, 'value'):
                                assistant_response = content.text.value
                                break
                        break
            
            return {
                "assistant_response": assistant_response,
                "thread_id": thread_id,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "assistant_response": f"An error occurred while processing your request: {str(e)}",
                "thread_id": thread_id,
                "status": "error"
            }

    async def _get_or_create_thread(self, thread_id: Optional[str] = None) -> str:
        """Get existing thread or create a new one."""
        if thread_id and thread_id in self.threads:
            return self.threads[thread_id]
        
        # Create new thread
        thread = self.client.agents.threads.create()
        thread_id = thread.id
        self.threads[thread_id] = thread_id
        
        logger.info(f"Created new thread: {thread_id}")
        return thread_id

    async def cleanup(self):
        """Clean up resources."""
        try:
            if self.agent_id and self.client:
                # Delete the agent
                self.client.agents.delete_agent(self.agent_id)
                logger.info("Agent deleted successfully")
            
            # Clear threads
            self.threads.clear()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        if self._initialized and self.agent_id:
            try:
                asyncio.create_task(self.cleanup())
            except Exception:
                pass  # Ignore errors during cleanup in destructor
