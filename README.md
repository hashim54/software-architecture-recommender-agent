# Software Architecture Recommender Agent

A modernized Azure AI Agent for providing intelligent software architecture recommendations using Azure AI Foundry SDK and the latest Semantic Kernel patterns.

## Overview

This application intelligently analyzes software project requirements and provides detailed architecture recommendations based on proven patterns and Azure services. It has been completely refactored from legacy procedural code to a modern Azure AI Agent implementation.

Software architects accumulate vast libraries of diagrams, white-papers, and Confluence pages from past projects. When a new initiative kicks off they often comb through this unstructured content manually to find reusable patterns—a slow and error-prone task. This application automates that research using Large Language Models (LLMs) and agentic workflows to surface the closest-matching reference architectures and explain how each one satisfies—or falls short of—the new project's requirements.

### Key Features

- **OCR + Figure Extraction**: Uses Azure Document Intelligence and GPT-4o for diagram analysis
- **Intelligent Diagram Summarization**: GPT-4o summarizes extracted architecture diagrams
- **Vector Search**: Hybrid semantic + vector search over indexed diagrams
- **Conversation Management**: Thread-based conversations with Azure AI Agent
- **Tool-Calling Agent**: Decides when to trigger search vs. keep asking follow-up questions
- **Azure Integration**: Full Azure services integration (Blob Storage, AI Search, OpenAI)

### Architecture Evolution

| **Legacy (Procedural)**                                | **Modern (Agent-based)**                         |
| ------------------------------------------------------ | ------------------------------------------------ |
| Procedural functions (`run_search`, `get_rag_results`) | Class-based Azure AI Agent with proper patterns  |
| Manual conversation history tracking                   | Thread-based conversation management             |
| Direct Azure OpenAI API calls                          | Azure AI Agent SDK integration                   |
| Custom search client implementation                    | AzureAISearchTool with connection-based config   |
| Synchronous processing                                 | Async factory pattern with proper initialization |

## Project Structure

```
software-architecture-recommender-agent/
├── backend/
│   ├── __init__.py
│   ├── app.py                          # FastAPI application with agent endpoints
│   ├── intake_agent.py                 # Azure AI Agent implementation
│   └── legacy_intake_procedural.py     # Archived legacy code
├── tests/
│   ├── test_intake_agent.py           # Agent testing script
│   ├── test_api.py                    # API endpoint testing
│   ├── test_connections.py            # Azure connection testing
│   ├── test_server.py                 # Server testing utilities
│   ├── check_environment.py           # Environment validation script
│   └── azure_search_connection_guide.py # Search connection diagnostics
├── scripts/
│   └── create_and_upload_index.py     # Azure AI Search index management
├── data/                              # Documentation and reference materials
│   ├── Present Analytics Patterns on Azure - 20250513.pdf
│   └── Present Migration Patterns From On-prem to Cloud - 20250513.pdf
├── .vscode/                           # VS Code debug configuration
│   ├── launch.json                    # Debug configurations
│   ├── tasks.json                     # Build and test tasks
│   ├── settings.json                  # Workspace settings
│   └── extensions.json                # Recommended extensions
├── requirements.txt                   # Python dependencies
├── .env                              # Environment configuration
├── debug_server.py                   # Enhanced debug server
├── start_server.py                   # Server startup script
├── software-architecture-recommender.code-workspace
└── README.md                         # This file
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- Azure subscription with the following services:
  - Azure AI Foundry (formerly Azure AI Studio)
  - Azure OpenAI Service
  - Azure AI Search (formerly Cognitive Search)
  - Azure Blob Storage (optional, for storing diagrams)
- VS Code (recommended for debugging)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd software-architecture-recommender-agent
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```properties
# Azure AI Project Configuration (required for new Azure AI Agents)
# Format: https://<resource-name>.services.ai.azure.com/api/projects/<project-name>
AZURE_AI_PROJECT_CONNECTION_STRING=https://your-resource.services.ai.azure.com/api/projects/your-project

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-openai-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002

# Azure AI Search Configuration
AZURE_AI_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_AI_SEARCH_KEY=your-search-key
AZURE_AI_SEARCH_INDEX_NAME=cw-architectures-index

# Optional: Azure Document Intelligence (for PDF processing)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=
AZURE_DOCUMENT_INTELLIGENCE_KEY=

# Optional: Azure Blob Storage (for storing diagrams)
AZURE_BLOB_STORAGE_ACCOUNT_NAME=
AZURE_BLOB_CONTAINER_NAME=
AZURE_BLOB_SP_CLIENT_ID=
AZURE_BLOB_SP_CLIENT_SECRET=
AZURE_BLOB_SP_TENANT_ID=
```

### 5. Verify Environment

```bash
python tests/check_environment.py
```

## Usage

### Starting the Server

#### Option 1: Using FastAPI directly

```bash
cd software-architecture-recommender-agent
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

#### Option 2: Using the start script

```bash
python start_server.py
```

#### Option 3: Using VS Code tasks

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Tasks: Run Task"
3. Select "Start FastAPI Server"

### API Endpoints

Once the server is running, you can access:

- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Query Endpoint**: `POST /query`

### Making API Requests

```bash
# Test the query endpoint
curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "I need to build a scalable web application for e-commerce"}'
```

### Testing

The project includes comprehensive testing utilities in the `tests/` folder:

#### Command Line Testing

```bash
# Validate environment setup (run this first)
python tests/check_environment.py

# Test Azure connections
python tests/test_connections.py

# Run agent tests
python tests/test_intake_agent.py

# Test API endpoints
python tests/test_api.py

# Test server functionality
python tests/test_server.py
```

#### VS Code Task Testing

If using VS Code, you can run tests via the Command Palette (`Ctrl+Shift+P`):

1. Type "Tasks: Run Task"
2. Select from available test tasks:
   - **Check Environment** - Validate Azure configuration
   - **Run Tests** - Execute agent unit tests
   - **Test API Endpoints** - Test REST API functionality
   - **Test Azure Connections** - Verify Azure service connectivity
   - **Run All Tests** - Execute complete test suite

#### Test Descriptions

- **`check_environment.py`** - Validates all environment variables and Azure connections
- **`test_connections.py`** - Tests Azure AI Project, OpenAI, and Search connections
- **`test_intake_agent.py`** - Unit tests for the Azure AI Agent implementation
- **`test_api.py`** - Integration tests for FastAPI endpoints
- **`test_server.py`** - Server functionality and performance tests
- **`azure_search_connection_guide.py`** - Diagnostic tool for Azure Search issues

## Data Pipeline (Index Creation)

The application includes a data pipeline for processing architecture documentation:

### 1. Extract and Index Documents

```bash
python scripts/create_and_upload_index.py
```

This script:

- Extracts text and figures from PDF architecture white-papers
- Summarizes diagrams using Azure OpenAI Vision
- Creates vector embeddings
- Uploads content to Azure AI Search
- Stores images in Azure Blob Storage

### 2. Index Structure

The Azure AI Search index contains:

- **Text content**: Extracted from PDFs
- **Image summaries**: Generated by GPT-4o Vision
- **Vector embeddings**: For semantic search
- **Metadata**: File names, page numbers, diagram types

## Debugging Guide

### VS Code Debugging Setup

The project includes comprehensive VS Code debugging configuration:

#### Debug Configurations Available:

- **Debug FastAPI App**: Main configuration for debugging the FastAPI server
- **Debug FastAPI App (Alternative)**: Alternative using module syntax
- **Debug Start Server Script**: Debug the start_server.py script
- **Debug Test Agent**: Debug the test agent directly

#### To Debug:

1. **Open the workspace**:

   - Double-click `software-architecture-recommender.code-workspace`
   - OR open VS Code and use File → Open Workspace

2. **Set breakpoints**:

   - Open `backend/intake_agent.py` or `backend/app.py`
   - Click in the gutter next to line numbers
   - Good places: `_async_init()`, `query()` methods

3. **Start debugging**:
   - Press `F5` or go to Run → Start Debugging
   - Select "Debug FastAPI App"

#### Alternative Debug Methods:

**Using Tasks:**

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "Tasks: Run Task"
3. Select "Start FastAPI Server"

**Using Debug Server:**

```bash
python debug_server.py
```

### Common Issues and Solutions

#### 1. Authentication Issues

- Ensure correct Azure tenant is selected
- Verify managed identity permissions
- Check environment variables

#### 2. Module Import Errors

- Verify virtual environment is activated
- Check PYTHONPATH is set correctly
- Ensure all dependencies are installed

#### 3. Azure AI Search Connection Issues

- Verify search service endpoint and key
- Check index exists and is accessible
- Ensure proper connection configuration in Azure AI Project

## API Reference

### POST /query

Query the architecture recommendation agent.

**Request Body:**

```json
{
  "query": "string",
  "thread_id": "string (optional)"
}
```

**Response:**

```json
{
  "assistant_response": "string",
  "thread_id": "string",
  "status": "success|error"
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "ISO 8601 timestamp"
}
```

## Development Workflow

### Two Main Components:

| Module                                 | Purpose                                                                                                                                                                                        |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **scripts/create_and_upload_index.py** | • Extract text + figures from PDF architecture white-papers<br>• Summarize diagrams with Azure OpenAI Vision<br>• Build vector embeddings and publish to Azure AI Search + Blob Storage        |
| **backend/**                           | FastAPI service with conversational **Intake Agent** that:<br>1. Collects user requirements<br>2. Runs hybrid semantic+vector search<br>3. Uses RAG to explain how architectures fit use-cases |

### Key Improvements in Modern Version

- **Azure AI Agent Architecture**: Uses Azure AI Projects SDK with proper agent patterns
- **Thread-based Conversations**: Implements conversation continuity using Azure AI Agent threads
- **Async Factory Pattern**: Proper async initialization with factory method
- **FastAPI Backend**: Clean REST API with proper error handling
- **Managed Identity Support**: Secure authentication using Azure managed identities
- **Azure AI Search Integration**: Leverages existing search index for contextual recommendations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

### Common Error Messages

**"AZURE_AI_PROJECT_CONNECTION_STRING is required"**

- Ensure your `.env` file contains the correct Azure AI Project connection string
- Format: `https://<resource-name>.services.ai.azure.com/api/projects/<project-name>`

**"No Azure AI Search connection found"**

- Verify your Azure AI Search service is properly configured
- Check that the search connection is set up in your Azure AI Project
- Ensure the service has proper permissions

**"Token tenant mismatch"**

- Use Azure tenant switching tools to set correct tenant
- Verify authentication credentials point to the correct tenant

**"'ItemPaged' object has no attribute 'data'"**

- This has been fixed in the current version
- Ensure you're using the latest code that properly handles Azure SDK responses

For additional help, check the debug logs or create an issue in the repository.

- **Python 3.8+** (Python 3.12+ recommended)
- **PowerShell** (for Windows development)
- **Azure subscription** with:
  - Azure AI Project (Azure AI Foundry)
  - Azure OpenAI service with deployed model
  - Azure AI Search service (optional, for enhanced recommendations)

### Step-by-Step Build Instructions

#### 1. Environment Setup

Create and activate a Python virtual environment:

```powershell
# Navigate to project directory
cd software-architecture-recommender-agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# For Command Prompt users:
# .\.venv\Scripts\activate.bat
```

#### 2. Install Dependencies

```powershell
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install all required dependencies
pip install -r requirements.txt

# Verify installation
pip list | Select-String "azure|fastapi|semantic-kernel"
```

#### 3. Configure Environment Variables

The project includes a properly configured `.env` file. Verify the settings match your Azure resources:

```powershell
# Check current environment configuration
Get-Content .env

# If needed, copy from template
# Copy-Item .env.template .env
```

**Required Environment Variables:**

- `AZURE_AI_PROJECT_CONNECTION_STRING` - Your Azure AI Project connection string
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI service endpoint
- `AZURE_OPENAI_KEY` - Azure OpenAI access key
- `AZURE_OPENAI_DEPLOYMENT_NAME` - Model deployment name (e.g., gpt-4.1-mini)
- `AZURE_AI_SEARCH_INDEX_NAME` - Search index name for recommendations

#### 4. Validate Environment

Run the environment validation script to ensure everything is configured correctly:

```powershell
python tests/check_environment.py
```

Expected output:

```
=== Azure AI Agent Environment Test ===

Checking environment variables...
✅ AZURE_AI_PROJECT_CONNECTION_STRING: https://software-arch-rec-cw-resource.serv...
✅ AZURE_OPENAI_DEPLOYMENT_NAME: gpt-4.1-mini
✅ AZURE_AI_SEARCH_INDEX_NAME: cw-architectures-index
✅ Environment setup looks good!
```

## Testing Instructions

### 1. Unit Testing - Direct Agent Testing

Test the Azure AI Agent directly without the FastAPI layer:

```powershell
# Run the agent unit tests
python tests\test_intake_agent.py
```

Expected behavior:

- Creates Azure AI Agent instance
- Processes sample architecture query
- Tests conversation continuity with follow-up questions
- Performs cleanup

### 2. Integration Testing - API Testing

#### Option A: Automated API Testing

```powershell
# Start server and run automated API tests
python tests/test_api.py
```

This script will:

- Start the FastAPI server automatically
- Test all endpoints (health, root, query)
- Test conversation continuity
- Provide detailed output of responses

#### Option B: Manual Server Testing

Start the server manually for interactive testing:

```powershell
# Start the FastAPI development server
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000

# Alternative using the start script
python start_server.py
```

Server will be available at: `http://127.0.0.1:8000`

### 3. API Endpoint Testing

#### Health Check

```powershell
# PowerShell method
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method GET

# Using curl (if available)
curl -X GET "http://127.0.0.1:8000/health"
```

#### Architecture Query Testing

```powershell
# PowerShell method
$body = @{
    query = "I need an architecture for a high-traffic e-commerce platform with microservices. What would you recommend?"
    thread_id = $null
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/query" -Method POST -Body $body -ContentType "application/json"

# Using curl
curl -X POST "http://127.0.0.1:8000/query" `
     -H "Content-Type: application/json" `
     -d '{
       "query": "I need an architecture for a scalable web application with real-time features. What Azure services would you recommend?",
       "thread_id": null
     }'
```

#### Follow-up Query Testing

```powershell
# Use the thread_id from the previous response
$followUpBody = @{
    query = "What about cost optimization for this architecture?"
    thread_id = "thread_abc123"  # Replace with actual thread_id from previous response
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/query" -Method POST -Body $followUpBody -ContentType "application/json"
```

### 4. Interactive Testing with Swagger UI

Once the server is running, access the interactive API documentation:

1. Open browser to: `http://127.0.0.1:8000/docs`
2. Use the Swagger UI to test endpoints interactively
3. Try sample queries and examine responses

### 5. Performance Testing

For basic performance testing:

```powershell
# Test multiple concurrent requests (requires Apache Bench or similar)
# ab -n 10 -c 2 -T application/json -p query.json http://127.0.0.1:8000/query

# Create test query file
$testQuery = @{
    query = "What's the best architecture for a data analytics platform?"
    thread_id = $null
} | ConvertTo-Json | Out-File -FilePath "query.json" -Encoding UTF8

# Alternative: PowerShell-based load testing
1..5 | ForEach-Object -Parallel {
    $body = @{
        query = "Test query $_: What architecture would you recommend for a mobile backend?"
        thread_id = $null
    } | ConvertTo-Json

    Invoke-RestMethod -Uri "http://127.0.0.1:8000/query" -Method POST -Body $body -ContentType "application/json"
} -ThrottleLimit 3
```

## Troubleshooting Build and Test Issues

### Common Build Issues

1. **Virtual Environment Activation Fails:**

   ```powershell
   # If execution policy prevents script execution
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

   # Then retry activation
   .\.venv\Scripts\Activate.ps1
   ```

2. **Package Installation Errors:**

   ```powershell
   # Clear pip cache and retry
   pip cache purge
   pip install -r requirements.txt --no-cache-dir

   # If specific packages fail, install individually
   pip install azure-ai-projects
   pip install semantic-kernel[azure]>=1.24.0
   ```

3. **Import Errors:**

   ```powershell
   # Verify Python path includes the project directory
   python -c "import sys; print('\n'.join(sys.path))"

   # Ensure you're in the project root directory
   Get-Location
   ```

### Common Test Issues

1. **Agent Initialization Failures:**

   - Verify Azure credentials: `az login` (if using Azure CLI)
   - Check connection string format in `.env`
   - Ensure Azure AI Project has proper permissions

2. **API Connection Errors:**

   ```powershell
   # Check if server is running
   netstat -an | Select-String "8000"

   # Test with curl/PowerShell from different terminal
   Test-NetConnection -ComputerName 127.0.0.1 -Port 8000
   ```

3. **Timeout Issues:**
   - Azure AI responses may take 10-30 seconds
   - Increase timeout values in test scripts if needed
   - Check Azure service status and quotas

### Debug Mode

Enable detailed logging for troubleshooting:

```powershell
# Set environment variable for debug logging
$env:PYTHONPATH="."
$env:AZURE_LOG_LEVEL="DEBUG"

# Run with verbose output
python -v tests/check_environment.py
```

## Usage

### Starting the FastAPI Server

```powershell
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

### API Endpoints

#### Health Check

```http
GET /health
```

#### Architecture Query

```http
POST /query
Content-Type: application/json

{
  "query": "I need an architecture for a high-traffic web application with global scaling requirements. What would you recommend?",
  "thread_id": null  // Optional: for conversation continuity
}
```

**Response:**

```json
{
  "assistant_response": "Based on your requirements for a high-traffic web application...",
  "thread_id": "thread_abc123",
  "status": "success"
}
```

### Testing the Agent

#### Direct Agent Testing

```powershell
python tests/test_intake_agent.py
```

#### API Testing

```powershell
python tests/test_api.py
```

## Key Features

### 1. Azure AI Agent Implementation

- Uses `@agent` decorator pattern for modern Azure AI development
- Proper async initialization with factory method
- Thread-based conversation management
- Automatic resource cleanup

### 2. Architecture Recommendations

The agent specializes in:

- Analyzing software project requirements
- Recommending architectural patterns and technologies
- Considering scalability, maintainability, performance, and cost
- Providing Azure-specific service recommendations
- Offering implementation guidance and best practices

### 3. Azure AI Search Integration

- Leverages existing architecture documentation in search index
- Provides contextual recommendations based on proven patterns
- Supports both standalone and search-enhanced responses

### 4. Conversation Continuity

- Thread-based conversation management
- Maintains context across multiple queries
- Supports follow-up questions and clarifications

## Azure AI Project Configuration

The agent requires an Azure AI Project (Azure AI Foundry) with:

1. **Model Deployment**: GPT-4 or compatible model
2. **Connections**:
   - Azure OpenAI connection for LLM access
   - Azure AI Search connection (optional) for enhanced recommendations
3. **Managed Identity**: For secure service-to-service authentication

## Environment Variables Reference

| Variable                             | Description                           | Required |
| ------------------------------------ | ------------------------------------- | -------- |
| `AZURE_AI_PROJECT_CONNECTION_STRING` | Azure AI Project connection string    | Yes      |
| `AZURE_OPENAI_DEPLOYMENT_NAME`       | OpenAI model deployment name          | Yes      |
| `AZURE_AI_SEARCH_INDEX_NAME`         | Search index name for recommendations | Yes      |
| `AZURE_AI_SEARCH_ENDPOINT`           | Search service endpoint URL           | No       |
| `AZURE_AI_SEARCH_KEY`                | Search service access key             | No       |

## Development and Testing

### Running Tests

```powershell
# Test the agent directly
python tests/test_intake_agent.py

# Test the API endpoints
python tests/test_api.py

# Check environment setup
python tests/check_environment.py
```

### Adding New Features

1. Extend the `IntakeAgent` class in `backend/intake_agent.py`
2. Add new API endpoints in `backend/app.py`
3. Update tests in `tests/` directory
4. Update this README with new functionality

## Troubleshooting

### Common Issues

1. **Agent initialization fails**

   - Verify Azure AI Project connection string
   - Check Azure credentials and permissions
   - Ensure the model deployment is accessible

2. **Search integration not working**

   - Verify Azure AI Search connection in AI Project
   - Check search index exists and has data
   - Ensure proper permissions for search service

3. **Authentication errors**
   - Use Azure CLI: `az login` for local development
   - Verify managed identity configuration for Azure deployment
   - Check Azure RBAC permissions

### Logging

The application uses Python logging. Set log level in the code or via environment:

```python
logging.basicConfig(level=logging.DEBUG)  # For detailed logs
```

## Migration from Legacy Code

The legacy procedural code is preserved in `backend/legacy_intake_procedural.py` for reference. Key migration changes:

1. **Function to Class**: Converted procedural functions to Azure AI Agent class
2. **Manual to Automatic**: Replaced manual conversation tracking with thread management
3. **Direct to SDK**: Changed from direct API calls to Azure AI Agent SDK
4. **Synchronous to Asynchronous**: Implemented proper async patterns throughout

## Additional Features

### Data Pipeline (Optional)

The project includes scripts for building a vector search index from architecture documentation:

```powershell
# Extract text and figures from PDF architecture white-papers
# Summarize diagrams with Azure OpenAI Vision
# Build vector embeddings and publish to Azure AI Search + Blob Storage
python scripts\create_and_upload_index.py
```

### Legacy Support

The original procedural implementation is preserved in `backend/legacy_intake_procedural.py` for:

- Reference and comparison
- Migration documentation
- Fallback capabilities during transition

## Contributing

1. Follow the existing code patterns and Azure best practices
2. Add tests for new functionality
3. Update documentation for any API changes
4. Use managed identity for all Azure service authentication

## License

See LICENSE file for details.
