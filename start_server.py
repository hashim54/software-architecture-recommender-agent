#!/usr/bin/env python3
"""Simple FastAPI test to check if the application starts correctly."""

import uvicorn
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    print("Starting FastAPI server...")
    try:
        uvicorn.run(
            "backend.app:app", 
            host="127.0.0.1", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
