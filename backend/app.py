from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ── local business logic ────────────────────────────────────────────────────
from intake_agent import run_search, get_rag_results, chat_with_intake_agent, intake_agent_system_prompt, rag_system_prompt

#app = FastAPI(title="Intake-Agent API")

class Message(BaseModel):
    role: str   # "user" | "assistant" | "system"
    content: str

class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Message]] = None

class QueryResponse(BaseModel):
    assistant_response: str
    search_results: Optional[str] = None
    conversation_history: List[Message]

#@app.post("/query", response_model=QueryResponse)
def query_endpoint(body: QueryRequest):
    """
    Accepts a user query + (optional) prior conversation history,
    performs search + RAG, and returns the answer while updating history.
    """
    # Build / extend conversation history
    history: List[Dict[str, str]] = (
        [m.model_dump() for m in body.conversation_history] if body.conversation_history else []
    )

    # Initiate Intake agent

    assistant_response, history, assistant_response_tool = chat_with_intake_agent(body.query, history)

    if assistant_response_tool:

        # Call search
        try:
            search_results = run_search(body.query, category_filter=None)
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"Search failure: {ex}")

        # Call RAG
        try:
            assistant_response, history = get_rag_results(
            user_query=body.query,
            search_results=search_results,
            system_prompt=rag_system_prompt,
            conversation_history=history,
            )
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"RAG failure: {ex}")

    return QueryResponse(
        assistant_response=assistant_response,
        search_results=search_results if assistant_response_tool else None,
        conversation_history=[Message(**m) for m in history],
    )


if __name__ == "__main__":
    
    #conversation_history = [{'role': 'user', 'content': 'I have a batc ingestion use case with reasonaly large data volumes. The batch process must run daily, ingest CSV files into a cloud data lake as is and be able to scale up and down. I am looking for an architecture that can help me with this use case. Can you help me with this?'}, {'role': 'assistant', 'content': 'Thank you for sharing the requirements! To ensure I provide you with the most suitable architecture recommendation for your batch ingestion use case, I need to gather a few more technical details:\n\n1. **Cloud Provider**: Do you have a preferred cloud provider (e.g., AWS, Azure, Google Cloud)?\n   \n2. **Data Lake**: Are you using a specific data lake service (e.g., Amazon S3, Azure Data Lake, Google Cloud Storage) or is this flexible?\n\n3. **Data Volume**: When you say "reasonably large data volumes," could you provide an estimate (e.g., GB per file, total GB per day)?\n\n4. **File Format**: Are the CSV files structured consistently or do they vary in schema? Are there any specific transformations needed post-ingestion?\n\n5. **Processing Framework**: Do you have a preference for a processing framework (e.g., Apache Spark, serverless options like AWS Lambda, or others)?\n\n6. **Cost Efficiency**: Is cost optimization a primary concern, or is performance/scalability the priority?\n\n7. **Security & Compliance**: Any specific compliance or security requirements (e.g., encryption, IAM policies)?\n\n8. **Future Needs**: Do you foresee needing to process data in real-time in the future, or is this strictly for batch processing?\n\nProviding these details will help me find the most appropriate architecture recommendation for your use case!'}]
    #user_query = "Yes, my preferred cloud provider is Azure. I am using Azure Data Lake and the data volume is around 1TB per day. The files are structured consistently and I do not need any transformations. I would prefer a serverless option for processing. Cost efficiency is a primary concern for me. I do not have any specific compliance or security requirements. I do not foresee needing to process data in real-time in the future."
    conversation_history = []
    user_query = "What is the architecture of Azure OpenAI?"
    response = query_endpoint(QueryRequest( 
        query=user_query,
        conversation_history=conversation_history 
    )) 
    if response.search_results:
        print("RAG Results:")
        print(response.assistant_response)
    else:
        print("Intake Agent Follow-up:")
        print(response.assistant_response)
     
