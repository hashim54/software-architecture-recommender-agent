#!/usr/bin/env python3
"""Test Azure AI Project connection and environment setup."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        "AZURE_AI_PROJECT_CONNECTION_STRING",
        "AZURE_OPENAI_DEPLOYMENT_NAME",
        "AZURE_AI_SEARCH_INDEX_NAME"
    ]
    
    print("Checking environment variables...")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:50]}{'...' if len(value) > 50 else ''}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print(f"\nOptional variables:")
    optional_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_AI_SEARCH_ENDPOINT", 
        "AZURE_AI_SEARCH_KEY"
    ]
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:50]}{'...' if len(value) > 50 else ''}")
        else:
            print(f"⚠️  {var}: NOT SET")

async def test_azure_connection():
    """Test Azure AI Project connection."""
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
        
        connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
        if not connection_string:
            print("❌ No connection string found")
            return False
            
        print(f"\nTesting Azure AI Project connection...")
        credential = DefaultAzureCredential()
        client = AIProjectClient.from_connection_string(
            conn_str=connection_string,
            credential=credential
        )
        
        print("✅ Azure AI Project client created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Azure connection failed: {str(e)}")
        return False

async def main():
    """Main test function."""
    print("=== Azure AI Agent Environment Test ===\n")
    
    check_environment()
    
    print(f"\n=== Testing Azure Connection ===")
    connection_ok = await test_azure_connection()
    
    if connection_ok:
        print("\n✅ Environment setup looks good!")
        print("You can now try running the FastAPI server or agent tests.")
    else:
        print("\n❌ Environment setup has issues.")
        print("Please check your Azure credentials and connection string.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
