


# Legacy procedural code has been moved to backend/legacy_intake_procedural.py for reference.

# Azure AI Agent for Foundry
import os
from pathlib import Path
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from typing import List, Dict, Any, Tuple
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from copy import deepcopy
# Azure AI Agents SDK
from azure.ai.agents import Agent, agent

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@agent(name="IntakeAgent", description="Recommends software architectures based on user requirements.")
class IntakeAgent(Agent):
    def __init__(self):
        # Configure service connections
        self.aoai_endpoint   = os.environ["Azure_OpenAI_Endpoint"]
        self.aoai_key        = os.environ["Azure_OpenAI_Key"]
        self.aoai_deployment = "gpt-4o"
        self.api_version     = "2024-12-01-preview"
        self.aoai_client = AzureOpenAI(
            api_key=self.aoai_key,
            azure_endpoint=self.aoai_endpoint,
            api_version=self.api_version,
        )
        self.search_endpoint = os.environ["Azure_Search_Endpoint"]
        self.search_admin_key = os.environ["Azure_Search_Key"]
        self.index_name = os.environ["Azure_Search_Index_Name"]
        self.embedding_deployment = os.environ["Azure_OpenAI_Embedding_Deployment_Name"]
        self.vector_config = "arch-hnsw"
        self.azure_openai_embedding_dimensions = 3072
        self.search_client = SearchClient(
            endpoint=self.search_endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.search_admin_key)
        )
        self.NUM_SEARCH_RESULTS = 5
        self.K_NEAREST_NEIGHBORS = 30
        self.rag_system_prompt = (
            """
            You are an AI assistant that helps people find the closest software architecture matching their use case requirements. You should explain in detail what exactly in the user requirements is being covered by the recommended architecture and what is not being covered.
            """
        )

    def run_search(self, search_query: str, category_filter: str | None = None) -> Tuple[str, List[Dict[str, str]]]:
        # Generate vector embedding for the query
        query_vector = self.aoai_client.embeddings.create(
            input=[search_query],
            model=self.embedding_deployment
        ).data[0].embedding

        # Create the vector query
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=self.K_NEAREST_NEIGHBORS,
            fields="content_vector"
        )
        filter_parts = []
        if category_filter:
            filter_parts.append(f"({category_filter})")
        filter_str = " and ".join(filter_parts) if filter_parts else None

        results = self.search_client.search(
            search_text=search_query,
            vector_queries=[vector_query],
            filter=filter_str,
            select=["id", "content", "name", "architecture_url"],
            top=self.NUM_SEARCH_RESULTS
        )
        output_parts = ["\n=== Search Results ==="]
        architecture_result_urls = []
        for i, result in enumerate(results, 1):
            result_parts = [
                f"\nResult #{i}",
                "=" * 80,
                f"ID: {result['id']}",
                f"Name: {result['name']}",
                f"Architecture URL: {result['architecture_url']}",
                f"Score: {result['@search.score']}",
                "\n<Start Content>",
                "-" * 80,
                result['content'],
                "-" * 80,
                "<End Content>"
            ]
            output_parts.extend(result_parts)
            architecture_result_urls.append({"name": result['name'], "architecture_url": result['architecture_url']})
        formatted_output = "\n".join(output_parts)
        return formatted_output, architecture_result_urls

    def get_rag_results(self, user_query: str, search_results: str, conversation_history: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
        history_string = "\n".join(
            [f"{entry['role'].capitalize()}: {entry['content']}" for entry in conversation_history]
        )
        user_message = f"""
        Conversation History:
        {history_string}

        User Query:
        {user_query}

        Search Results:
        {search_results}
        """
        response = self.aoai_client.chat.completions.create(
            model=self.aoai_deployment,
            messages=[
                {"role": "system", "content": self.rag_system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        rag_result = response.choices[0].message.content
        history = deepcopy(conversation_history) if conversation_history else []
        history.append({"role": "assistant", "content": rag_result})
        return rag_result, history

    def execute(self, input: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entrypoint for Azure AI Foundry agent execution.
        Expects input to contain 'user_query' and optionally 'conversation_history'.
        """
        user_query = input.get("user_query", "")
        conversation_history = input.get("conversation_history", [])
        # Step 1: Search
        search_results_str, architecture_result_urls = self.run_search(user_query)
        # Step 2: RAG
        rag_result, updated_history = self.get_rag_results(user_query, search_results_str, conversation_history)
        return {
            "recommendation": rag_result,
            "urls": architecture_result_urls,
            "conversation_history": updated_history
        }
