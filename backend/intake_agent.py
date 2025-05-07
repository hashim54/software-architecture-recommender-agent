import os
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from pydantic import BaseModel
from typing import List, Dict, Any
from openai import AzureOpenAI
import json
import base64
from typing import Tuple
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential, AccessToken
import uuid
from copy import deepcopy


#configure service connections
aoai_endpoint   = ""
aoai_key        = ""
aoai_deployment = ""                      
api_version     = ""  


aoai_client = AzureOpenAI(
    api_key=aoai_key,
    azure_endpoint=aoai_endpoint,
    api_version=api_version,
)

search_endpoint = ""      # e.g. https://<search>.search.windows.net
search_admin_key = ""     # 
index_name = ""                       # change as needed
embedding_deployment = ""          # your AOAI embedding deployment
vector_config = ""
azure_openai_embedding_dimensions = 3072

search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(search_admin_key)
)

NUM_SEARCH_RESULTS = 5
K_NEAREST_NEIGHBORS = 30


rag_system_prompt = """
You are an AI assistant that helps people find the closest software architecture matching their use case requirements. You should explain in detail what exactly in the user requirements is being covered by the recommended architecture and what is not being covered. 
"""

intake_agent_system_prompt = """
You are the intake agent for a software architecture recommendation system. Your job is to initiate a conversation with the user and ask them the technical requirements of their use case. Their use case could be related to the deployment of an application on cloud, migration of a workload from on-prem to cloud or some database/data engineering workload. Try to extract as much details from the user as possible on thier use case before leveraging the JSON schema tools defined.
If you have enough requirements from users on their requirements, call the json-schema of the rag_results tool in order to return the closest match to the user's requirements of an approved architecture from the inventory. If you don't have enough technical requirements from the user then continue the conversation and ask the users to provide further details regarding their use case. 
• You can talk normally, or you can call the JSON‑schema tools I’ve defined.
• ONLY call a tool when it is needed for up‑to‑date, factual, or transactional data
  that you can’t reasonably hallucinate (e.g. live weather, stock quotes, DB lookups).
• When you *do* call a tool, respond with **nothing but** the tool_call block—no prose.
• If no tool is needed, answer conversationally and do **not** include a tool_call.
• Never invent tool names or parameters that were not provided in the `tools` array.
"""

tools = [
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

def run_search(search_query: str, category_filter: str | None = None) -> str:
    """
    Perform a search using Azure Cognitive Search with both semantic and vector queries.
    Returns the results as a formatted string.
    """
    # Generate vector embedding for the query
    query_vector = aoai_client.embeddings.create(
        input=[search_query],
        model=embedding_deployment
    ).data[0].embedding

    # Create the vector query
    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=K_NEAREST_NEIGHBORS,
        fields="content_vector"
    )
    
    # Create filter combining processed_ids and category filter
    filter_parts = []
    if category_filter:
        filter_parts.append(f"({category_filter})")
    filter_str = " and ".join(filter_parts) if filter_parts else None

    # Perform the search
    results = search_client.search(
        search_text=search_query,
        vector_queries=[vector_query],
        filter=filter_str,
        select=["id", "content", "name", "architecture_url"],
        top=NUM_SEARCH_RESULTS
    )
    
    # Format the search results into a string
    output_parts = ["\n=== Search Results ==="]
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
    
    formatted_output = "\n".join(output_parts)
    return formatted_output

def get_rag_results(user_query: str, search_results: str, system_prompt: str, conversation_history: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]]]:
    """
    Constructs the AOAI user message using the user query, search results, system prompt, and conversation history,
    then invokes the AOAI client to get the RAG results.
    """
    # Format the conversation history into a readable string
    history_string = "\n".join(
        [f"{entry['role'].capitalize()}: {entry['content']}" for entry in conversation_history]
    )

    # Construct the user message
    user_message = f"""
    Conversation History:
    {history_string}

    User Query:
    {user_query}

    Search Results:
    {search_results}
    """

    # Invoke AOAI client to get the RAG results
    response = aoai_client.chat.completions.create(
        model=aoai_deployment,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=3000,
        temperature=0.7
    )

    # Extract and return the RAG result from the response
    rag_result = response.choices[0].message.content
    history = deepcopy(conversation_history) if conversation_history else []
    history.append({"role": "assistant", "content": rag_result})

    return rag_result, history

def chat_with_intake_agent(user_query: str, conversation_history: List[Dict[str, str]]) -> Tuple[str, List[Dict[str, str]], Dict[str, Any]]:
    """
    Sends the user_query plus prior conversation_history to AOAI and returns:
      • assistant_response – text from the model
      • updated_history    – history with the new user & assistant turns appended
    """
    #Build / extend history --------------------------------------------
    history = deepcopy(conversation_history) if conversation_history else []

    history_string = "\n".join(
        [f"{entry['role'].capitalize()}: {entry['content']}" for entry in conversation_history]
    )

    user_message = f"""
    Conversation History:
    {history_string}

    User Query:
    {user_query}
    """

    history.append({"role": "user", "content": user_query})

    #Call Azure OpenAI ---------------------------------------------------
    response = aoai_client.chat.completions.create(
        model=aoai_deployment,
        messages=[
            {"role": "system", "content": intake_agent_system_prompt},
            {"role": "user", "content": user_message}
        ],
        max_tokens=1500,
        temperature=0.7,
        tools=tools,
        tool_choice="auto"
    )
    assistant_response = response.choices[0].message.content
    assistant_response_tool = json.loads(response.choices[0].message.tool_calls[0].function.arguments) if response.choices[0].message.tool_calls else None

    #Update history with assistant turn ---------------------------------
    history.append({"role": "assistant", "content": assistant_response if assistant_response else ""})

    return assistant_response, history, assistant_response_tool


if __name__ == "__main__":
    #print("Starting intake agent...")
    #search_results = run_search(search_query="What is the architecture of Azure OpenAI?", category_filter=None)
    conversation_history = [{'role': 'user', 'content': 'I have a batc ingestion use case with reasonaly large data volumes. The batch process must run daily, ingest CSV files into a cloud data lake as is and be able to scale up and down. I am looking for an architecture that can help me with this use case. Can you help me with this?'}, {'role': 'assistant', 'content': 'Thank you for sharing the requirements! To ensure I provide you with the most suitable architecture recommendation for your batch ingestion use case, I need to gather a few more technical details:\n\n1. **Cloud Provider**: Do you have a preferred cloud provider (e.g., AWS, Azure, Google Cloud)?\n   \n2. **Data Lake**: Are you using a specific data lake service (e.g., Amazon S3, Azure Data Lake, Google Cloud Storage) or is this flexible?\n\n3. **Data Volume**: When you say "reasonably large data volumes," could you provide an estimate (e.g., GB per file, total GB per day)?\n\n4. **File Format**: Are the CSV files structured consistently or do they vary in schema? Are there any specific transformations needed post-ingestion?\n\n5. **Processing Framework**: Do you have a preference for a processing framework (e.g., Apache Spark, serverless options like AWS Lambda, or others)?\n\n6. **Cost Efficiency**: Is cost optimization a primary concern, or is performance/scalability the priority?\n\n7. **Security & Compliance**: Any specific compliance or security requirements (e.g., encryption, IAM policies)?\n\n8. **Future Needs**: Do you foresee needing to process data in real-time in the future, or is this strictly for batch processing?\n\nProviding these details will help me find the most appropriate architecture recommendation for your use case!'}]
    user_query = "Yes, my preferred cloud provider is Azure. I am using Azure Data Lake and the data volume is around 1TB per day. The files are structured consistently and I do not need any transformations. I would prefer a serverless option for processing. Cost efficiency is a primary concern for me. I do not have any specific compliance or security requirements. I do not foresee needing to process data in real-time in the future."
    assistant_response, history, assistant_response_tool = chat_with_intake_agent(user_query, conversation_history)
    print("\n=== Assistant Response ===")
    print(assistant_response)
    search_query = run_search(search_query=assistant_response_tool["user_query"], category_filter=None)
    print("\n=== RAG Results ===")
    rag_result, history = get_rag_results(user_query=assistant_response_tool["user_query"], search_results=search_query, system_prompt=rag_system_prompt, conversation_history=history)
    print(rag_result)
    print("\n=== Updated Conversation History ===")
    for entry in history:
        print(entry)
    #rag_result = get_rag_results(user_query="What is the architecture of Azure OpenAI?", search_results=search_results, system_prompt=rag_system_prompt, conversation_history=conversation_history)
    # Print the RAG results
    #print("\n=== RAG Result ===")
    #print(rag_result)