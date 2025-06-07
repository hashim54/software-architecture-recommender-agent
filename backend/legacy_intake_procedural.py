import json

class LegacyIntakeProcedural:
    """
    Reference implementation of the old procedural code for intake agent logic.
    Not used by the IntakeAgent class, but kept for reference/migration/testing.
    """
    def __init__(self):
        # Reference for the old system prompts and tools
        self.rag_system_prompt = """
        You are an AI assistant that helps people find the closest software architecture matching their use case requirements. You should explain in detail what exactly in the user requirements is being covered by the recommended architecture and what is not being covered.
        """

        self.intake_agent_system_prompt = """
        You are the intake agent for a software architecture recommendation system. Your job is to initiate a conversation with the user and ask them the technical requirements of their use case. Their use case could be related to the deployment of an application on cloud, migration of a workload from on-prem to cloud or some database/data engineering workload. Try to extract as much details from the user as possible on their use case before leveraging the JSON schema tools defined.
        If you have enough requirements from users on their requirements, call the json-schema of the rag_results tool in order to return the closest match to the user's requirements of an approved architecture from the inventory. If you don't have enough technical requirements from the user then continue the conversation and ask the users to provide further details regarding their use case. 
        • You can talk normally, or you can call the JSON‑schema tools I’ve defined.
        • ONLY call a tool when it is needed for up‑to‑date, factual, or transactional data
          that you can’t reasonably hallucinate (e.g. live weather, stock quotes, DB lookups).
        • When you *do* call a tool, respond with **nothing but** the tool_call block—no prose.
        • If no tool is needed, answer conversationally and do **not** include a tool_call.
        • Never invent tool names or parameters that were not provided in the `tools` array.
        """

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "run_search",
                    "description": "Return the search results for the technical requirements specified by the user.",
                    "parameters": {
                        "type": "object",
                        "properties": { "user_query": { "type": "string" }, "category_filter": { "type": "string" } },
                        "required": ["user_query"],
                    },
                },
            }
        ]

    def run_search(self, search_query: str, category_filter: str | None = None):
        # This is a placeholder. The actual implementation required global variables.
        # See previous code for details. Not functional as a method.
        pass

    def get_rag_results(self, user_query: str, search_results: str, system_prompt: str, conversation_history):
        # This is a placeholder. The actual implementation required global variables.
        # See previous code for details. Not functional as a method.
        pass

    def chat_with_intake_agent(self, user_query: str, conversation_history):
        # This is a placeholder. The actual implementation required global variables.
        # See previous code for details. Not functional as a method.
        pass
