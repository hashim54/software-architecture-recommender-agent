#!/usr/bin/env python3
"""
Debug-enabled FastAPI server startup script for VS Code debugging.
This script provides better error handling and debugging capabilities.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug.log')
    ]
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Setup the Python environment and paths."""
    # Add the current directory to Python path
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))
    
    # Load environment variables
    from dotenv import load_dotenv
    env_path = current_dir / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment variables from {env_path}")
    else:
        logger.warning(f"No .env file found at {env_path}")
    
    # Log important environment variables (without sensitive data)
    logger.info("Environment setup:")
    logger.info(f"AZURE_AI_PROJECT_CONNECTION_STRING: {'Set' if os.getenv('AZURE_AI_PROJECT_CONNECTION_STRING') else 'Not set'}")
    logger.info(f"MODEL_DEPLOYMENT_NAME: {os.getenv('MODEL_DEPLOYMENT_NAME', 'Not set')}")
    logger.info(f"SEARCH_INDEX_NAME: {os.getenv('SEARCH_INDEX_NAME', 'Not set')}")

def start_server():
    """Start the FastAPI server with debug configuration."""
    import uvicorn
    
    logger.info("Starting FastAPI server in debug mode...")
    
    try:
        uvicorn.run(
            "backend.app:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="debug",
            access_log=True,
            use_colors=True,
            reload_dirs=["backend"],
            reload_excludes=["*.pyc", "__pycache__"]
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("SOFTWARE ARCHITECTURE RECOMMENDER - DEBUG MODE")
    logger.info("=" * 60)
    
    setup_environment()
    start_server()
