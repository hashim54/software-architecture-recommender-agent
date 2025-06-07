#!/usr/bin/env python3
"""Simple test script to verify the Azure AI Agent works correctly."""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).resolve().parent / "backend"))

async def test_agent():
    """Test the IntakeAgent functionality."""
    try:
        from intake_agent import IntakeAgent
        
        print("Creating IntakeAgent...")
        agent = await IntakeAgent.create()
        print("✅ Agent created successfully!")
        
        # Test query
        query = "I need an architecture for a high-traffic web application that processes user data and needs to scale globally. What would you recommend?"
        print(f"\nTesting query: {query}")
        
        result = await agent.query(query)
        
        print(f"\n✅ Query processed successfully!")
        print(f"Thread ID: {result['thread_id']}")
        print(f"Status: {result['status']}")
        print(f"\nResponse:\n{result['assistant_response']}")
        
        # Test follow-up
        follow_up = "What specific Azure services would be best for this architecture?"
        print(f"\nTesting follow-up: {follow_up}")
        
        result2 = await agent.query(follow_up, thread_id=result['thread_id'])
        print(f"\n✅ Follow-up processed successfully!")
        print(f"Thread ID: {result2['thread_id']}")
        print(f"Status: {result2['status']}")
        print(f"\nResponse:\n{result2['assistant_response']}")
        
        # Cleanup
        await agent.cleanup()
        print("\n✅ Agent cleanup completed")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing Azure AI Agent...")
    asyncio.run(test_agent())
