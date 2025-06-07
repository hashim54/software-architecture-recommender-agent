import sys
import os
import asyncio
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(backend_path))

from intake_agent import IntakeAgent

async def test_intake_agent():
    """Test the IntakeAgent with a sample architecture question."""
    user_query = (
        "I need an architecture for a batch ingestion use case. "
        "The process must run daily, ingest CSV files into a cloud data lake, "
        "and be able to scale. Cost efficiency is important."
    )
    
    try:
        print("Creating and initializing Azure AI Agent...")
        agent = await IntakeAgent.create()
        print("Agent initialized successfully!")
        
        print(f"\nProcessing query: {user_query}")
        result = await agent.query(user_query)
        
        print("\n=== Agent Response ===")
        print(result["assistant_response"])
        print(f"\nThread ID: {result['thread_id']}")
        print(f"Status: {result['status']}")
        
        # Test follow-up question in the same thread
        follow_up = "What specific Azure services would you recommend for this architecture?"
        print(f"\nFollow-up query: {follow_up}")
        
        follow_up_result = await agent.query(follow_up, thread_id=result['thread_id'])
        
        print("\n=== Follow-up Response ===")
        print(follow_up_result["assistant_response"])
        print(f"Thread ID: {follow_up_result['thread_id']}")
        print(f"Status: {follow_up_result['status']}")
        
        # Clean up
        await agent.cleanup()
        print("\nAgent cleanup completed")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """Run the async test."""
    print("Testing Azure AI Intake Agent...")
    asyncio.run(test_intake_agent())

if __name__ == "__main__":
    main()
