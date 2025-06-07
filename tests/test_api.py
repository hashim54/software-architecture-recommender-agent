#!/usr/bin/env python3
"""Test the FastAPI endpoints to ensure everything works correctly."""

import asyncio
import requests
import json
import time
from threading import Thread
import uvicorn
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).resolve().parent))

def start_server():
    """Start the FastAPI server in a separate thread."""
    try:
        uvicorn.run(
            "backend.app:app", 
            host="127.0.0.1", 
            port=8000, 
            log_level="error"  # Reduce log output for testing
        )
    except Exception as e:
        print(f"Server error: {e}")

async def test_api():
    """Test the API endpoints."""
    base_url = "http://127.0.0.1:8000"
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test root endpoint
        print("Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Root endpoint: {response.status_code} - {response.json()}")
        
        # Test query endpoint
        print("Testing query endpoint...")
        query_data = {
            "query": "I need an architecture recommendation for a scalable web application that handles user authentication and data processing. What would you suggest?",
            "thread_id": None
        }
        
        response = requests.post(
            f"{base_url}/query", 
            json=query_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"Thread ID: {result.get('thread_id')}")
            print(f"Status: {result.get('status')}")
            print(f"Response: {result.get('assistant_response', 'No response')[:200]}...")
            
            # Test follow-up with thread ID
            if result.get('thread_id'):
                print("\nTesting follow-up query...")
                follow_up_data = {
                    "query": "What specific Azure services would be best for this architecture?",
                    "thread_id": result['thread_id']
                }
                
                follow_response = requests.post(
                    f"{base_url}/query", 
                    json=follow_up_data,
                    timeout=30
                )
                
                if follow_response.status_code == 200:
                    follow_result = follow_response.json()
                    print(f"✅ Follow-up successful!")
                    print(f"Response: {follow_result.get('assistant_response', 'No response')[:200]}...")
                else:
                    print(f"❌ Follow-up failed: {follow_response.status_code}")
                    print(follow_response.text)
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    """Main test function."""
    print("=== Azure AI Agent API Test ===\n")
    
    # Start server in background thread
    server_thread = Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Run API tests
    asyncio.run(test_api())
    
    print("\nAPI testing completed. Press Ctrl+C to stop the server.")

if __name__ == "__main__":
    main()
